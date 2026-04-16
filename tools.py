import pandas as pd
import streamlit as st

SALES_REQUIRED_COLUMNS = {
    'FECHA',
    'NÚMERO',
    'IMPORTE TOTAL DEL COMPROBANTE',
    'TOTAL (ITEM)',
    'CANTIDAD (ITEM)',
    'CATEGORÍA (ITEM)',
    'VENDEDOR',
    'ESTADO',
    'DESCUENTO GLOBAL CON IGV',
    'DESCRIPCIÓN (ITEM)'
}

PAYMENTS_REQUIRED_COLUMNS = {
    'FECHA',
    'NÚMERO',
    'IMPORTE TOTAL DEL COMPROBANTE',
    'MÉTODO (PAGO)'
}

OPTIONAL_COLUMNS = {
    'DOCUMENTOS'
}


@st.cache_data
def load_excel_file(path: str, skiprows: int = 0) -> pd.DataFrame:
    try:
        return pd.read_excel(path, skiprows=skiprows)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"No se encontró el archivo: {path}") from exc
    except Exception as exc:
        raise RuntimeError(f"Error al leer el archivo {path}: {exc}") from exc


def validate_dataframe_columns(df: pd.DataFrame, required_columns, df_name: str) -> bool:
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        st.error(
            f"⚠️ El archivo de {df_name} no contiene las columnas obligatorias: {missing}."
            f" Columnas disponibles: {list(df.columns)}"
        )
        return False
    return True


def ensure_datetime_column(df: pd.DataFrame, column: str = 'FECHA') -> pd.DataFrame:
    if column not in df.columns:
        return df

    if not pd.api.types.is_datetime64_any_dtype(df[column]):
        df[column] = pd.to_datetime(df[column], errors='coerce')

    if df[column].isna().any():
        st.warning(f"Algunas filas en la columna '{column}' no pudieron convertirse a fecha y se marcarán como NaT.")
    return df


def filter_document_type(df: pd.DataFrame, tipo_documento) -> pd.DataFrame:
    if not tipo_documento or 'DOCUMENTOS' not in df.columns:
        return df

    doc_str = df['DOCUMENTOS'].astype(str)
    mask = pd.Series(False, index=df.index)

    if 'Factura' in tipo_documento:
        mask = mask | doc_str.str.startswith('F', na=False)
    if 'Boleta' in tipo_documento:
        mask = mask | doc_str.str.startswith('B', na=False)
    if 'Ticket' in tipo_documento:
        mask = mask | df['DOCUMENTOS'].isna() | doc_str.str.strip().eq('') | doc_str.str.contains(r'^\s*$', na=True)

    return df[mask].copy()


def apply_filters(
    df_datos: pd.DataFrame,
    tipo_documento,
    date1: pd.Timestamp,
    date2: pd.Timestamp,
    eliminar_anulados: bool = True,
    eliminar_fechas: bool = True
) -> pd.DataFrame:
    df_temp = df_datos.copy()

    if eliminar_anulados and 'ESTADO' in df_temp.columns:
        df_temp = df_temp[df_temp['ESTADO'] != 'Anulado'].copy()

    if eliminar_fechas and 'FECHA' in df_temp.columns:
        if not pd.api.types.is_datetime64_any_dtype(df_temp['FECHA']):
            df_temp['FECHA'] = pd.to_datetime(df_temp['FECHA'], errors='coerce')
        df_temp = df_temp[(df_temp['FECHA'] >= date1) & (df_temp['FECHA'] <= date2)].copy()

    df_temp = filter_document_type(df_temp, tipo_documento)
    return df_temp.reset_index(drop=True)


def aggregate_unique_transaction_amount(df: pd.DataFrame, period: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=['period', 'IMPORTE TOTAL DEL COMPROBANTE'])

    df_temp = df.copy()
    df_temp['period'] = df_temp['FECHA'].dt.to_period(period)
    aggregated = (
        df_temp.drop_duplicates(subset=['NÚMERO'])
        .groupby('period')['IMPORTE TOTAL DEL COMPROBANTE']
        .sum()
        .reset_index()
    )
    return aggregated


def fill_period_range(aggregated: pd.DataFrame, period_range) -> pd.DataFrame:
    completed = aggregated.set_index('period').reindex(period_range, fill_value=0).reset_index()
    completed.columns = ['period', 'TOTAL (ITEM)']
    return completed


def aggregate_sales_by_key(df: pd.DataFrame, key: str) -> pd.DataFrame:
    df_items = df.groupby(key)['CANTIDAD (ITEM)'].sum().reset_index()
    df_importe = (
        df.drop_duplicates(subset=['NÚMERO'])
        .groupby(key)
        .agg({
            'IMPORTE TOTAL DEL COMPROBANTE': 'sum',
            'NÚMERO': 'nunique'
        })
        .reset_index()
    )
    return df_importe.merge(df_items, on=key, how='left')


def aggregate_sales_by_key_without_items(df: pd.DataFrame, key: str) -> pd.DataFrame:
    return (
        df.drop_duplicates(subset=['NÚMERO'])
        .groupby(key)
        .agg({
            'IMPORTE TOTAL DEL COMPROBANTE': 'sum',
            'NÚMERO': 'nunique'
        })
        .reset_index()
    )


def limpiar_nombre_vendedor(nombre):
    if pd.isna(nombre):
        return 'Sin asignar'

    nombre = str(nombre).strip()
    if not nombre:
        return 'Sin asignar'

    nombre_lower = nombre.lower()
    if nombre_lower in {'store', 'store.'}:
        return 'Admin'

    if 'store.' in nombre_lower:
        parte = nombre_lower.split('.')[-1]
        if parte and parte != 'store':
            nombre_limpio = parte.capitalize()
            return nombre_limpio[:6] + '.' if len(nombre_limpio) > 6 else nombre_limpio
        return 'Admin'

    if 'store' in nombre_lower and nombre_lower != 'store':
        parte = nombre_lower.replace('store', '').strip(' .')
        if parte:
            nombre_limpio = parte.capitalize()
            return nombre_limpio[:6] + '.' if len(nombre_limpio) > 6 else nombre_limpio

    nombre_limpio = nombre.capitalize()
    return nombre_limpio[:6] + '.' if len(nombre_limpio) > 6 else nombre_limpio
