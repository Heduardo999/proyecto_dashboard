import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import plotly.graph_objects as go
import plotly.figure_factory as ff
from streamlit_option_menu import option_menu
from numerize.numerize import numerize
from dateutil.relativedelta import relativedelta
#from datetime import datetime

st.set_page_config(page_title="Dashboard", page_icon="🌎", layout="wide")
st.subheader("🏠 Tienda Av. Larco 986")


# Espaciado superior, estilos css
st.markdown("""
<style>

/* ================== CONTENEDOR PRINCIPAL ================== */
div.block-container {
    padding-top: 2.2rem;
    padding-bottom: 1rem;
}
/* celular */ 
@media (max-width: 768px) {
    div.block-container {
        padding-top: 2.4rem !important;
        padding-bottom: 1rem !important;
    }
}

/* ================== HEADERS ================== */
h1, h2, h3 {
    margin-top: 0.3rem !important;
    margin-bottom: 0.3rem !important;
}
@media (max-width: 768px) {
    h3 {
        font-size: 18px !important;  /* ajusta aquí */
    }
}

/* ================== SUBHEADER (clave) ================== */
.stSubheader {
    margin-top: 0.5rem !important;
    margin-bottom: 0.3rem !important;
}

/* ================== SUBIR LOS INPUT Y LABEL DE LAS FECHAS - celular ================== */
@media (max-width: 768px) {
    /* Subir inputs de fecha */
    div[data-testid="stDateInput"] {
        margin-top: -16px !important;
    }
    /* Opcional: subir también el label */
    div[data-testid="stDateInput"] label {
        margin-bottom: 8px !important;
    }
}

/* ================== COLUMNAS ================== */
[data-testid="column"] {
    padding-top: 0.2rem !important;
    padding-bottom: 0.2rem !important;
}

/* ================== GRÁFICOS ================== */
.stPlotlyChart {
    margin-top: -10px !important;
    margin-bottom: -5px !important;
}

/* ================== EXPANDERS ================== */
.streamlit-expanderHeader {
    margin-top: 0.3rem !important;
}

.streamlit-expanderContent {
    margin-top: 0 !important;
}

/* ================== DATAFRAMES ================== */
.stDataFrame {
    margin-top: 0.3rem !important;
}

/* ================== ELIMINAR ESPACIOS VACÍOS ================== */
.stMarkdown p {
    margin-bottom: 0 !important;
}

/* ================== SIDEBAR ================== */
section[data-testid="stSidebar"] {
    padding-top: 0rem;
}
/* ====== HEADER DEL SIDEBAR (Filtros:) ====== */
section[data-testid="stSidebar"] h2 {
    margin-bottom: 0.5rem !important;
    padding-bottom: 0rem !important;
    margin-top: -1rem !important;
}
/* ====== LABEL DEL MULTISELECT ====== */
section[data-testid="stSidebar"] .stMultiSelect label {
    margin-top: 0rem !important;
    padding-top: 0rem !important;
}
/* ====== CONTENEDOR DEL MULTISELECT ====== */
section[data-testid="stSidebar"] .stMultiSelect {
    margin-top: -0.5rem !important;
}
            
/* ================== BOTONES ================== */
.stButton {
    margin-top: 0.3rem;
}

/* ================== ALERTAS ================== */
.stAlert {
    margin-top: 0.5rem;
}

/* ====== TEXTO DE st.info() - texto de las cajas de metricas ====== */
.stAlert p {
    font-size: 16px !important;  /* ajusta aquí */
}

/* ====== LABEL de st.metric (ej: "Suma Total S/") ====== */
[data-testid="stMetricLabel"] {
    font-size: 13px !important;
}

/* ====== VALOR de st.metric (el número grande) ====== */
[data-testid="stMetricValue"] {
    font-size: 32px !important;
    font-weight: 600;
}
@media (max-width: 768px) {
    [data-testid="stMetricValue"] {
        font-size: 24px !important;
    }
}

/* ================== REDUCCIÓN GLOBAL DE GAP ENTRE BLOQUES ================== */
.element-container {
    margin-bottom: 0.4rem !important;
}
            
/* ====== CONTENEDOR DE COLUMNAS ====== */
[data-testid="column"] > div {
    gap: 0.2rem !important;
}
            
/* ====== CONTENEDOR DEL HTML (clave real) ====== */
div[data-testid="stElementContainer"]:has(iframe) {
    margin-bottom: -25px !important;
}
/* celular */
@media (max-width: 768px) {
    div[data-testid="stElementContainer"]:has(iframe) {
        margin-bottom: 10px !important;
    }
}
            
/* ====== IFRAME (components.html) ====== */
iframe {
    margin-bottom: 0px !important;  /* 🔥 reduce espacio debajo */
    display: block; !important;
    /* padding-bottom: 0 !important; */
}

/* ====== DIVISOR (GLOBAL) ====== */
.stApp hr {
    margin-top: 0.2rem !important;     /* más pegado al subheader */
    margin-bottom: 0.3rem !important;  /* separación inferior controlada */
}
/* celular */
@media (max-width: 768px) {
    .stApp hr {
        margin-top: 0rem !important;
        margin-bottom: 0.2rem !important;
    }
}

/* ====== CONTENEDOR GENERAL ====== */
.element-container {
    margin-bottom: 0.2rem !important;
}

</style>
""", unsafe_allow_html=True)

# ================================== cargan datos =============================================
#df = pd.read_csv("data/Celular.csv", 
#                    encoding="ISO-8859-1",
#                    on_bad_lines='skip',
#                    sep=';',
#                    low_memory=False
#                )

df = pd.read_excel("data/ventas.xlsx",
                    skiprows=8
                )

df_dos = pd.read_excel("data/pagos.xlsx",
                    skiprows=4
                )
# ==================================== side bar logo ==========================================
with st.sidebar:
    box_date = datetime.datetime.now().strftime("%d %B %Y")

    # Centrar con columnas
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.image(
            "data/logoRF.png",
            #caption=f"Last updated by:  \n {box_date}",
            #caption="Last updated by: ",
            caption=f"Actualizado el :  \n {box_date}",
            width = 150,
        )

# ================================= fechas ================================
df["FECHA"] = pd.to_datetime(df["FECHA"])

fecha_actual = datetime.datetime.now()
startDate = fecha_actual.replace(day=1)
#startDate = df['FECHA'].min()
endDate   = df["FECHA"].max()

col1, col2 = st.columns(2)
with col1:
    fecha_inicio = st.date_input("Fecha Inicial", value=startDate, format="DD/MM/YYYY")
    date1 = pd.to_datetime(fecha_inicio)  # 00:00:00 del día seleccionado
with col2:
    fecha_fin = st.date_input("Fecha Final", value=endDate, format="DD/MM/YYYY")
    # Ajustar la fecha final para incluir todo el día hasta las 23:59:59
    date2 = pd.to_datetime(fecha_fin) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

# Validar que fecha_inicio sea <= fecha_fin
if fecha_inicio > fecha_fin:
    st.error("❌ Error: La fecha inicial no puede ser mayor que la fecha final")
    st.stop()  # Detiene la ejecución si hay error

# =================================== escoger documento ===================================
st.sidebar.header("Filtros: ")

tipo_documento = st.sidebar.multiselect(
    "📍 Selecciona Tipo de Documento",
    options=['Factura', 'Boleta', 'Ticket'],
    placeholder="Opciones",
    help="Selecciona uno o más tipos de documento"
)

# 1) =================================== metricas ====================================
def metricas():
    df_filtrado = aplicar_filtros(df)

    # La forma más simple - sin usar agg ni reset_index
    ventas_total = df_filtrado.drop_duplicates(subset=['NÚMERO'])['IMPORTE TOTAL DEL COMPROBANTE'].sum()
    
    num_transacciones = df_filtrado['NÚMERO'].nunique()
    #total_items = len(df_filtrado)
    total_items = df_filtrado['CANTIDAD (ITEM)'].sum()
    
    if num_transacciones > 0:
        promedio_ventas = df_filtrado.groupby('NÚMERO')['TOTAL (ITEM)'].sum().mean()
    else:
        promedio_ventas = 0

    if num_transacciones > 0:
        items_por_transaccion = df_filtrado.groupby('NÚMERO')['CANTIDAD (ITEM)'].sum().mean()
    else:
        items_por_transaccion = 0

    total1, total2, total3, total4, total5 = st.columns(5, gap = 'small')

    with total1:
        st.info('Total en Ventas', icon = "💰")
        st.metric("Suma Total S/", f"{ventas_total:,.2f}")
    with total2:
        st.info('Items Vendidos', icon="📦")
        st.metric("Total Items", f"{total_items:,}")
    with total3:
        st.info('Transacciones', icon="🛒")
        st.metric("N° Transacciones", f"{num_transacciones:,}")
    with total4:
        st.info('Ventas Promedio', icon = "📊")
        st.metric("Ventas / Transacción", f"{promedio_ventas:,.2f}")
    with total5:
        st.info('Items Promedio', icon = "📁")
        st.metric("Items Vendidos / Transacción", f"{items_por_transaccion:,.2f}")

    st.markdown("""---""")

# 2) ================== GRAFICO EN EL TIEMPO : VENTAS POR dias ================================
def graph_time_dia():
    # df_filtrado_grafico = df_filtrado_grafico[mask_grafico]
    df_filtrado_grafico = aplicar_filtros(df, eliminar_fechas=False)
    
    # calculamos fechas para el grafico (curva actual)
    fecha_fin_grafico = date2
    fecha_inicio_grafico = (date2 - pd.Timedelta(days=6)).normalize()

    # calculamos fechas para curva del año anterior
    fecha_fin_anterior = fecha_fin_grafico - relativedelta(years=1)
    fecha_inicio_anterior = fecha_inicio_grafico - relativedelta(years=1)

    # Filtrar datos para el gráfico actual
    df_grafico = df_filtrado_grafico[
        (df_filtrado_grafico['FECHA'] >= fecha_inicio_grafico) & 
        (df_filtrado_grafico['FECHA'] <= fecha_fin_grafico)
    ].copy()

    # Filtrar datos para año anterior
    df_grafico_anterior = df_filtrado_grafico[
        (df_filtrado_grafico['FECHA'] >= fecha_inicio_anterior) & 
        (df_filtrado_grafico['FECHA'] <= fecha_fin_anterior)
    ].copy()

    # preparar datos para curva actual
    if len(df_grafico) > 0:
        # Agrupar datos existentes
        df_grafico['year_month_dia'] = df_grafico['FECHA'].dt.to_period("D")

        # DataFrame para sumar IMPORTE TOTAL DEL COMPROBANTE (solo una vez por transacción)
        df_importe = df_grafico.drop_duplicates(subset=['NÚMERO']).groupby('year_month_dia').agg({
            'IMPORTE TOTAL DEL COMPROBANTE': 'sum'  # Suma importes de transacciones únicas
        }).reset_index()
        ventas_diarias = df_importe.groupby('year_month_dia')['IMPORTE TOTAL DEL COMPROBANTE'].sum().reset_index()
    else:
        # Si no hay datos, crear DataFrame vacío con estructura correcta
        ventas_diarias = pd.DataFrame(columns=['year_month_dia', 'IMPORTE TOTAL DEL COMPROBANTE'])

    # preparar datos para curva año anterior
    if len(df_grafico_anterior) > 0:
        # Agrupar datos existentes
        df_grafico_anterior['year_month_dia'] = df_grafico_anterior['FECHA'].dt.to_period("D")

        # DataFrame para sumar IMPORTE TOTAL DEL COMPROBANTE (solo una vez por transacción)
        df_importe = df_grafico_anterior.drop_duplicates(subset=['NÚMERO']).groupby('year_month_dia').agg({
            'IMPORTE TOTAL DEL COMPROBANTE': 'sum'  # Suma importes de transacciones únicas
        }).reset_index()

        ventas_anterior_diarias = df_importe.groupby('year_month_dia')['IMPORTE TOTAL DEL COMPROBANTE'].sum().reset_index()
    #   st.dataframe(ventas_anterior_diarias)
    else:
        # Si no hay datos, crear DataFrame vacío con estructura correcta
        ventas_anterior_diarias = pd.DataFrame(columns=['year_month_dia', 'IMPORTE TOTAL DEL COMPROBANTE'])

    # crear rango de dias para año actual
    dias_completos = pd.period_range(
        start = fecha_inicio_grafico.to_period('D'),
        end = fecha_fin_grafico.to_period('D'),
        freq='D'
    )

    # crear un rango de dias para el año anterior
    dias_completos_anterior = pd.period_range(
        start = fecha_inicio_anterior.to_period('D'),
        end = fecha_fin_anterior.to_period('D'),
        freq='D'
    )

    # Reindexar para incluir todos los dias (los que no tienen datos serán 0) - año actual
    ventas_completas = ventas_diarias.set_index('year_month_dia')
    ventas_completas = ventas_completas.reindex(dias_completos, fill_value=0)
    ventas_completas = ventas_completas.reset_index()
    ventas_completas.columns = ['year_month_dia', 'TOTAL (ITEM)']
    # Etiquetas para el eje X con el año actual (solo mes)
    ventas_completas['etiqueta_x'] = ventas_completas['year_month_dia'].dt.strftime("%d/%m")

    # Reindexar para incluir todos los meses (los que no tienen datos serán 0) - año anterior
    ventas_anterior_completas = ventas_anterior_diarias.set_index('year_month_dia')
    ventas_anterior_completas = ventas_anterior_completas.reindex(dias_completos_anterior, fill_value=0)
    ventas_anterior_completas = ventas_anterior_completas.reset_index()
    ventas_anterior_completas.columns = ['year_month_dia', 'TOTAL (ITEM)']
    # Usar las MISMAS etiquetas que el año actual (solo mes) para superposición
    ventas_anterior_completas['etiqueta_x'] = ventas_anterior_completas['year_month_dia'].dt.strftime("%d/%m")

    # Crear gráfico
    st.subheader('📉 Ventas Diarias')
    fig_time_dia = go.Figure()

    # añadir primera curva (año actual)
    fig_time_dia.add_trace(go.Scatter(
        x = ventas_completas['etiqueta_x'],
        y = ventas_completas['TOTAL (ITEM)'],
        mode = 'lines+markers',
        name = f"Año {date2.year}",
        line = dict(color='#FFD700', width=2),
        marker = dict(color='#FFD700', size=8, line=dict(color='white', width=0.5)),
        customdata = ventas_completas[['etiqueta_x', 'TOTAL (ITEM)']].values,
        hovertemplate=f"Día : " + "%{customdata[0]}<br>" +
                      "Ventas =  S/ %{customdata[1]:,.2f}<br>" +
                      "<extra></extra>"
    ))

    # añadir segunda curva (año anterior)
    fig_time_dia.add_trace(go.Scatter(
        x = ventas_anterior_completas['etiqueta_x'],
        y = ventas_anterior_completas['TOTAL (ITEM)'],
        mode = 'lines+markers',
        name = f"Año {date2.year-1}",
        line = dict(color='#1E88E5', width=2),
        marker = dict(color='#1E88E5', size=8, line=dict(color='white', width=0.5)),
        customdata = ventas_anterior_completas[['etiqueta_x', 'TOTAL (ITEM)']].values,
        hovertemplate=f"Día : " + "%{customdata[0]}<br>" +
                      "Ventas =  S/ %{customdata[1]:,.2f}<br>" +
                      "<extra></extra>"
    ))

    # CONFIGURAR EJE X PARA ETIQUETAS HORIZONTALES
    fig_time_dia.update_xaxes(
        tickangle=0,  # 0 grados = horizontal
        tickmode='array',
        tickvals=ventas_completas['etiqueta_x'],
        ticktext=ventas_completas['etiqueta_x']
    )

    # ACTUALIZAR LAYOUT
    fig_time_dia.update_layout(
        #title=f"⏳ Del {fecha_inicio_grafico.strftime("%d/%m")} al {fecha_fin_grafico.strftime("%d/%m")}",
        title=dict(
            text=f"⏳ Del {fecha_inicio_grafico.strftime('%d/%m')} al {fecha_fin_grafico.strftime('%d/%m')}",
            font=dict(size=14)  # 🔥 controla el tamaño aquí
        ),
        xaxis_title="Días",
        #xaxis_title_font_size=16,
        yaxis_title="Ventas (S/)",
        #yaxis_title_font_size=16,
        template="gridon",
        legend=dict(
            yanchor="top",
            y=1.20,
            xanchor="right",
            x=0.96
        ),
        margin=dict(l=10, r=10, t=0, b=10),
        height = 300 if st.session_state.get("is_mobile", True) else 300,
        dragmode=False
    )

    st.plotly_chart(fig_time_dia, use_container_width=True, config={"displayModeBar": False})

    #==================== data view de las ventas por dias =======================
    cl1, cl2 = st.columns(2)

    with cl1:
        with st.expander("Ver Datos - Ventas por Días", expanded = False):

            # Crear DataFrame combinado
            df_combinado = pd.DataFrame({
                'Día': ventas_completas['etiqueta_x'],
                f'Ventas (S/) - {date2.year-1}': ventas_anterior_completas['TOTAL (ITEM)'],
                f'Ventas (S/) - {date2.year}': ventas_completas['TOTAL (ITEM)'],
            })

            # Crear una copia del DataFrame para no modificar el original
            df_combinado_con_totales = df_combinado.copy()

            col_actual = f'Ventas (S/) - {date2.year}'
            col_anterior = f'Ventas (S/) - {date2.year-1}'

            total_actual = df_combinado[col_actual].sum()
            total_anterior = df_combinado[col_anterior].sum()

            df_combinado_con_totales.loc['TOTAL'] = {
                'Día': 'TOTAL',
                col_anterior: total_anterior,
                col_actual: total_actual,
            }

            # Aplicar estilo con gradiente
            styled_df = df_combinado_con_totales.style \
                .background_gradient(cmap="cividis", subset=[f'Ventas (S/) - {date2.year}', f'Ventas (S/) - {date2.year-1}']) \
                .format({
                    f'Ventas (S/) - {date2.year}': '{:,.2f}',
                    f'Ventas (S/) - {date2.year-1}': '{:,.2f}'
                })

            # Mostrar dataframe
            st.dataframe(styled_df, use_container_width = True, hide_index = True)

            csv_ventas_dia = df_combinado.copy()
            csv_ventas_dia[f'Ventas (S/) - {date2.year}'] = csv_ventas_dia[f'Ventas (S/) - {date2.year}'].map('{:.2f}'.format)
            csv_ventas_dia[f'Ventas (S/) - {date2.year-1}'] = csv_ventas_dia[f'Ventas (S/) - {date2.year-1}'].map('{:.2f}'.format)

            csv = csv_ventas_dia.to_csv(index = False).encode('utf-8')
            st.download_button("📥 Descargar Data", data = csv, file_name = "ventas_por_dia.csv", mime = "text/csv",
                        help = "Click aqui para descargar los datos en un archivo CSV", use_container_width = True)
    #with cl2:
        #st.info("hola")
    #st.write("")
    st.markdown("""---""")

# 3) ================== GRAFICO EN EL TIEMPO : VENTAS POR MES ================================
def graph_time_mes():
    df_filtrado_grafico = aplicar_filtros(df, eliminar_fechas=False)

    # calculamos fechas para el grafico (curva actual)
    fecha_fin_grafico = date2
    fecha_inicio_grafico = pd.Timestamp(year=date2.year, month=1, day=1)

    # calculamos fechas para curva del año anterior
    fecha_fin_anterior = fecha_fin_grafico - relativedelta(years=1)
    fecha_inicio_anterior = pd.Timestamp(year=fecha_fin_anterior.year, month=1, day=1)
    
    # Filtrar datos para el gráfico actual
    df_grafico = df_filtrado_grafico[
        (df_filtrado_grafico['FECHA'] >= fecha_inicio_grafico) & 
        (df_filtrado_grafico['FECHA'] <= fecha_fin_grafico)
    ].copy()

    # Filtrar datos para año anterior
    df_grafico_anterior = df_filtrado_grafico[
        (df_filtrado_grafico['FECHA'] >= fecha_inicio_anterior) & 
        (df_filtrado_grafico['FECHA'] <= fecha_fin_anterior)
    ].copy()

    # preparar datos para curva actual
    if len(df_grafico) > 0:
        # Agrupar datos existentes
        df_grafico['year_month'] = df_grafico['FECHA'].dt.to_period("M")

        # DataFrame para sumar IMPORTE TOTAL DEL COMPROBANTE (solo una vez por transacción)
        df_importe = df_grafico.drop_duplicates(subset=['NÚMERO']).groupby('year_month').agg({
            'IMPORTE TOTAL DEL COMPROBANTE': 'sum'  # Suma importes de transacciones únicas
        }).reset_index()
        ventas_mensuales = df_importe.groupby('year_month')['IMPORTE TOTAL DEL COMPROBANTE'].sum().reset_index()
    else:
        # Si no hay datos, crear DataFrame vacío con estructura correcta
        ventas_mensuales = pd.DataFrame(columns=['year_month', 'IMPORTE TOTAL DEL COMPROBANTE'])

    # preparar datos para curva año anterior
    if len(df_grafico_anterior) > 0:
        # Agrupar datos existentes
        df_grafico_anterior['year_month'] = df_grafico_anterior['FECHA'].dt.to_period("M")

        # DataFrame para sumar IMPORTE TOTAL DEL COMPROBANTE (solo una vez por transacción)
        df_importe = df_grafico_anterior.drop_duplicates(subset=['NÚMERO']).groupby('year_month').agg({
            'IMPORTE TOTAL DEL COMPROBANTE': 'sum'  # Suma importes de transacciones únicas
        }).reset_index()
        ventas_anterior = df_importe.groupby('year_month')['IMPORTE TOTAL DEL COMPROBANTE'].sum().reset_index()
    else:
        ventas_anterior = pd.DataFrame(columns=['year_month', 'IMPORTE TOTAL DEL COMPROBANTE'])

    # crear rango de meses para año actual
    meses_completos = pd.period_range(
        start=fecha_inicio_grafico.to_period('M'),
        end=fecha_fin_grafico.to_period('M'),
        freq='M'
    )

    # crear un rango de meses para el año anterior
    meses_completos_anterior = pd.period_range(
        start=fecha_inicio_anterior.to_period('M'),
        end=fecha_fin_anterior.to_period('M'),
        freq='M'
    )
    
    # Reindexar para incluir todos los meses (los que no tienen datos serán 0) - año actual
    ventas_completas = ventas_mensuales.set_index('year_month')
    ventas_completas = ventas_completas.reindex(meses_completos, fill_value=0)
    ventas_completas = ventas_completas.reset_index()
    ventas_completas.columns = ['year_month', 'TOTAL (ITEM)']
    # Etiquetas para el eje X con el año actual (solo mes)
    ventas_completas['etiqueta_x'] = ventas_completas['year_month'].dt.strftime("%b")

    # Reindexar para incluir todos los meses (los que no tienen datos serán 0) - año anterior
    ventas_anterior_completas = ventas_anterior.set_index('year_month')
    ventas_anterior_completas = ventas_anterior_completas.reindex(meses_completos_anterior, fill_value=0)
    ventas_anterior_completas = ventas_anterior_completas.reset_index()
    ventas_anterior_completas.columns = ['year_month', 'TOTAL (ITEM)']
    # Usar las MISMAS etiquetas que el año actual (solo mes) para superposición
    ventas_anterior_completas['etiqueta_x'] = ventas_anterior_completas['year_month'].dt.strftime("%b")

    # Crear gráfico
    st.subheader('📈 Ventas Mensuales')
    fig_time_mes = go.Figure()

    # añadir primera curva (año actual)
    fig_time_mes.add_trace(go.Scatter(
        x=ventas_completas['etiqueta_x'],
        y=ventas_completas['TOTAL (ITEM)'],
        mode='lines+markers',
        name=f"Año {date2.year}",
        line=dict(color='#FFD700', width=2),
        marker=dict(color='#FFD700', size=8, line=dict(color='white', width=0.5)),
        customdata=ventas_completas[['etiqueta_x', 'TOTAL (ITEM)']].values,
        hovertemplate=f"Año - Mes : {date2.year} - " + "%{customdata[0]}<br>" +
                      "Ventas =  S/ %{customdata[1]:,.2f}<br>" +
                      "<extra></extra>"
    ))

    # añadir segunda curva (año anterior)
    fig_time_mes.add_trace(go.Scatter(
        x=ventas_anterior_completas['etiqueta_x'],
        y=ventas_anterior_completas['TOTAL (ITEM)'],
        mode='lines+markers',
        name=f"Año {date2.year-1}",
        line=dict(color='#1E88E5', width=2),
        marker=dict(color='#1E88E5', size=8, line=dict(color='white', width=0.5)),
        customdata=ventas_anterior_completas[['etiqueta_x', 'TOTAL (ITEM)']].values,
        hovertemplate=f"Año - Mes : {date2.year-1} - " + "%{customdata[0]}<br>" +
                      "Ventas =  S/ %{customdata[1]:,.2f}<br>" +
                      "<extra></extra>"
    ))
    
    # ACTUALIZAR LAYOUT
    fig_time_mes.update_layout(
        #title=f"⏳ Comparativa: {date2.year-1} vs {date2.year}",
        title=dict(
            text=f"⏳ Comparativa: {date2.year-1} vs {date2.year}",
            font=dict(size=14)  # 🔥 controla el tamaño aquí
        ),
        xaxis_title="Mes",
        #xaxis_title_font_size=19,
        yaxis_title="Ventas (S/)",
        #yaxis_title_font_size=19,
        template="gridon",
        legend=dict(
            yanchor="top",
            y=1.20,
            xanchor="right",
            x=0.96
        ),
        margin=dict(l=10, r=10, t=0, b=10),
        height = 300 if st.session_state.get("is_mobile", True) else 300,
        dragmode=False
    )
    
    # CONFIGURAR EJE X PARA ETIQUETAS HORIZONTALES
    fig_time_mes.update_xaxes(
        tickangle=0,  # 0 grados = horizontal
        tickmode='array',
        tickvals=ventas_completas['etiqueta_x'],
        ticktext=ventas_completas['etiqueta_x']
    )
    #fig_time_mes.update_traces(line_shape='spline')
    st.plotly_chart(fig_time_mes, use_container_width=True, config={"displayModeBar": False})

    #==================== data view de las ventas por mes =======================
    cl1, cl2 = st.columns(2)

    with cl1:
        with st.expander("Ver Datos - Ventas por Mes", expanded = False):

            # Crear DataFrame combinado
            df_combinado = pd.DataFrame({
                'Mes': ventas_completas['etiqueta_x'],
                f'Ventas (S/) - {date2.year-1}': ventas_anterior_completas['TOTAL (ITEM)'],
                f'Ventas (S/) - {date2.year}': ventas_completas['TOTAL (ITEM)'],
            })

            # Crear una copia del DataFrame para no modificar el original
            df_combinado_con_totales = df_combinado.copy()

            col_actual = f'Ventas (S/) - {date2.year}'
            col_anterior = f'Ventas (S/) - {date2.year-1}'

            total_actual = df_combinado[col_actual].sum()
            total_anterior = df_combinado[col_anterior].sum()

            df_combinado_con_totales.loc['TOTAL'] = {
                'Mes': 'TOTAL',
                col_anterior: total_anterior,
                col_actual: total_actual,
            }

            # Aplicar estilo con gradiente
            styled_df = df_combinado_con_totales.style \
                .background_gradient(cmap="cividis", subset=[f'Ventas (S/) - {date2.year}', f'Ventas (S/) - {date2.year-1}']) \
                .format({
                    f'Ventas (S/) - {date2.year}': '{:,.2f}',
                    f'Ventas (S/) - {date2.year-1}': '{:,.2f}'
                })

            # Mostrar dataframe
            st.dataframe(styled_df, use_container_width = True, hide_index = True)

            csv_ventas_mes = df_combinado.copy()
            csv_ventas_mes[f'Ventas (S/) - {date2.year}'] = csv_ventas_mes[f'Ventas (S/) - {date2.year}'].map('{:.2f}'.format)
            csv_ventas_mes[f'Ventas (S/) - {date2.year-1}'] = csv_ventas_mes[f'Ventas (S/) - {date2.year-1}'].map('{:.2f}'.format)

            csv = csv_ventas_mes.to_csv(index = False).encode('utf-8')
            st.download_button("📥 Descargar Data", data = csv, file_name = "ventas_por_mes.csv", mime = "text/csv",
                        help = "Click aqui para descargar los datos en un archivo CSV", use_container_width = True)
    #with cl2:
        #st.info("hola")
    #st.write("")
    st.markdown("""---""")

# 4) ============================== ventas por categoria ==================================
def graph_categoria():
    # Aplicar los mismos filtros
    df_filtrado = aplicar_filtros(df)

    # DataFrame para sumar CANTIDAD (ITEM) y contar transacciones únicas (con todos los items)
    df_items = df_filtrado.groupby('CATEGORÍA (ITEM)').agg({
        'CANTIDAD (ITEM)': 'sum',  # Suma todos los items
        #'NÚMERO': 'nunique'  # Cuenta transacciones únicas
    }).reset_index()

    # DataFrame para sumar IMPORTE TOTAL DEL COMPROBANTE (solo una vez por transacción)
    df_importe = df_filtrado.drop_duplicates(subset=['NÚMERO']).groupby('CATEGORÍA (ITEM)').agg({
        'IMPORTE TOTAL DEL COMPROBANTE': 'sum',  # Suma importes de transacciones únicas
        'NÚMERO': 'nunique'  # Cuenta transacciones únicas
    }).reset_index()

    # Combinar ambos DataFrames
    df_categoria = df_importe.merge(df_items, on='CATEGORÍA (ITEM)', how='left')

    # Reordenar las columnas
    df_categoria = df_categoria[['CATEGORÍA (ITEM)', 'IMPORTE TOTAL DEL COMPROBANTE', 'CANTIDAD (ITEM)', 'NÚMERO']]

    df_categoria.rename(columns={
        'CATEGORÍA (ITEM)' : 'Categoría',
        'IMPORTE TOTAL DEL COMPROBANTE': 'Total Ventas',
        'NÚMERO': 'N° Transac.',
        'CANTIDAD (ITEM)': 'N° Items'
    }, inplace=True)
    
    # Ordenar por Total Ventas y limitar a top 10
    df_categoria = df_categoria.sort_values('Total Ventas', ascending=False).reset_index(drop=True).head(10)

    # Crear las columnas DENTRO de la función
    col1, col2 = st.columns(2)

    with col1:
        st.subheader('📋 Top 10 - Ventas por Categoría')

        fig_categoria = px.bar(
            df_categoria,
            x='Total Ventas',
            y='Categoría',
            orientation='h',
            title='<b>Top 10 Categorías por Ventas</b>',
            color_discrete_sequence=['#2E8B57'] * len(df_categoria),
            template='plotly_white',
            text='Total Ventas'  # Mostrar valores en barras
        )
        # Personalizar formato
        fig_categoria.update_traces(
            texttemplate='S/ %{x:,.2f}',
            textposition='inside',
            marker=dict(line=dict(color='white', width=1)),
            customdata=df_categoria[['Categoría', 'Total Ventas', 'N° Items']].values,
            hovertemplate=#f"Año - Mes = {date2.year-1} - " + "%{customdata[0]}<br>" +
                        #"Ventas (S/) =  S/ %{customdata[1]:,.2f}<br>" +
                        "Cantidad = %{customdata[2]}"
                        "<extra></extra>"
        )

        fig_categoria.update_layout(
            #title = f"🧭 Período: {fecha_inicio.strftime('%d-%m-%Y')} a {fecha_fin.strftime('%d-%m-%Y')}",
            title=dict(
                text=f"🧭 Período: {fecha_inicio.strftime('%d-%m-%Y')} a {fecha_fin.strftime('%d-%m-%Y')}",
                font=dict(size=14)  # 🔥 controla el tamaño aquí
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                showgrid=False,
                title='Ventas (S/)',
                #title_font_size=19            
            ),
            yaxis=dict(
                title='Categoría',
                categoryorder='total ascending',  # ✅ Forzar orden de mayor a menor
                #tickfont=dict(size=22)
                #title_font_size=19
            ),
            margin=dict(l=10, r=10, t=50, b=10),
            height=430,
            #height = 400 if st.session_state.get("is_mobile", True) else 400,
            dragmode=False
        )
        st.plotly_chart(fig_categoria, use_container_width=True, config={"displayModeBar": False})

    with col2:
        st.subheader("➡ Resumen")
        
        # Calcular los totales
        total_ventas = df_categoria['Total Ventas'].sum()
        total_cantidad = df_categoria['N° Items'].sum()
        total_transacciones = df_categoria['N° Transac.'].sum()

        # Crear una copia del DataFrame para no modificar el original
        df_categoria_con_totales = df_categoria.copy()

        # Agregar fila de totales
        df_categoria_con_totales.loc['TOTAL'] = {
            'Categoría': 'TOTAL',
            'Total Ventas': total_ventas,
            'N° Items': total_cantidad,
            'N° Transac.': total_transacciones
        }

        # Mostrar la tabla con totales
        st.dataframe(
            df_categoria_con_totales.style
            .format({'Total Ventas': 'S/ {:,.2f}', 'N° Items': '{:,.0f}', 'N° Transac.': '{:,.0f}'})
            .background_gradient(cmap='Greens', subset=['Total Ventas']),
            use_container_width=True,
            hide_index=True,
            height=422
        )

    #st.write("")
    st.markdown("""---""")

# 5) ========================== grafico ventas por vendedor ==============================
def graph_vendedor():
    df_filtrado = aplicar_filtros(df)
    
    left, right = st.columns(2)
    
    with left:
        # grafico de ventas por vendedor
        st.subheader('👨‍💻 Ventas por Vendedor')

        # DataFrame para sumar CANTIDAD (ITEM) y contar transacciones únicas (con todos los items)
        df_items = df_filtrado.groupby('VENDEDOR').agg({
            'CANTIDAD (ITEM)': 'sum',  # Suma todos los items
            #'NÚMERO': 'nunique'  # Cuenta transacciones únicas
        }).reset_index()

        # DataFrame para sumar IMPORTE TOTAL DEL COMPROBANTE (solo una vez por transacción)
        df_importe = df_filtrado.drop_duplicates(subset=['NÚMERO']).groupby('VENDEDOR').agg({
            'IMPORTE TOTAL DEL COMPROBANTE': 'sum',  # Suma importes de transacciones únicas
            'NÚMERO': 'nunique'  # Cuenta transacciones únicas
        }).reset_index()

        # Combinar ambos DataFrames
        df_vendedor = df_importe.merge(df_items, on='VENDEDOR', how='left')

        # Reordenar las columnas
        df_vendedor = df_vendedor[['VENDEDOR', 'IMPORTE TOTAL DEL COMPROBANTE', 'CANTIDAD (ITEM)', 'NÚMERO']]

        df_vendedor.rename(columns={
            'VENDEDOR' : 'Vendedor',
            'IMPORTE TOTAL DEL COMPROBANTE': 'Total Ventas',
            'NÚMERO': 'N° Transac.',
            'CANTIDAD (ITEM)': 'N° Items'
        }, inplace=True)
        
        # Ordenar por Total Ventas
        df_vendedor = df_vendedor.sort_values('Total Ventas', ascending=False).reset_index(drop=True)
    
        fig_vendedor = px.pie(
            df_vendedor,
            values="Total Ventas",
            names="Vendedor",
            template='gridon',
            hole = 0.5
        )
        # Esto activa las líneas conectoras automáticas
        fig_vendedor.update_traces(
            textposition='outside',      # Texto fuera del pastel
            textinfo='label+percent',    # Muestra etiqueta y porcentaje
            texttemplate='%{label}<br>%{percent:.2%}',  # Formato
            marker=dict(line=dict(color='white', width=2)),  # Bordes blancos
            customdata=df_vendedor[['Vendedor', 'Total Ventas']].values,
            hovertemplate='<b>%{label}</b><br>' +
                #'👤 Vendedor: %{label}<br>' +
                'Ventas: S/ %{value:,.2f}<br>' +
                #'📊 Porcentaje: %{percent:.1%}<br>' +
                '<extra></extra>'
        )
        fig_vendedor.update_layout(
            #title = f"🧭 Período: {fecha_inicio.strftime('%d-%m-%Y')} a {fecha_fin.strftime('%d-%m-%Y')}",
            title=dict(
                text=f"🧭 Período: {fecha_inicio.strftime('%d-%m-%Y')} a {fecha_fin.strftime('%d-%m-%Y')}",
                font=dict(size=14)  # 🔥 controla el tamaño aquí
            ),
            showlegend=False,  # ✅ Elimina la leyenda
            height=380
        )

        st.plotly_chart(fig_vendedor, use_container_width=True)

    with right:
        st.subheader("➡ Resumen")
        #st.write("")

        df_vendedor.columns = ['Vendedor', 'Total Ventas', 'N° Items', 'N° Transac.']

        # Calcular los totales
        total_ventas = df_vendedor['Total Ventas'].sum()
        total_items = df_vendedor['N° Items'].sum()
        total_transacciones = df_vendedor['N° Transac.'].sum()

        # Crear una copia del DataFrame para no modificar el original
        df_vendedor_con_totales = df_vendedor.copy()

        # Agregar fila de totales
        df_vendedor_con_totales.loc['TOTAL'] = {
            'Vendedor': 'TOTAL',
            'Total Ventas': total_ventas,
            'N° Items': total_items,
            'N° Transac.': total_transacciones
        }

        # Mostrar la tabla con totales
        st.dataframe(
            df_vendedor_con_totales.style
            .format({'Total Ventas': 'S/ {:,.2f}'})
            .background_gradient(cmap='Oranges', subset=['Total Ventas']),
            use_container_width=True,
            hide_index=True,
            #height=260
        )

        #col1, col2, col3 = st.columns(3)
        #with col1:
            # mostrar total de ventas
        #    total_ventas = df_vendedor['Total Ventas'].sum()
        #    st.markdown(f"""
        #        <div style="text-align: center">
        #            <div style="font-size: 0.9rem; color: #fff;">Total Ventas</div>
        #            <div style="font-size: 1.4rem; font-weight: bold; color: #fff; text-align: center">S/ {total_ventas:,.2f}</div>
        #        </div>
        #    """, unsafe_allow_html=True)
        #with col2:
            # Mostrar cantidad de items vendidos
        #    total_items = df_vendedor['N° Items'].sum()
        #    st.markdown(f"""
        #        <div style="text-align: center">
        #            <div style="font-size: 0.9rem; color: #fff;">Total Items</div>
        #            <div style="font-size: 1.4rem; font-weight: bold; color: #fff; text-align: center">{total_items:,.0f}</div>
        #        </div>
        #    """, unsafe_allow_html=True)
        #with col3:
            # mostrar numero de transacciones
        #    total_transacciones = df_vendedor['N° Transacciones'].sum()
        #    st.markdown(f"""
        #        <div style="text-align: center">
        #            <div style="font-size: 0.9rem; color: #fff;">Total Transacciones</div>
        #            <div style="font-size: 1.4rem; font-weight: bold; color: #fff; text-align: center">{total_transacciones:,.0f}</div>
        #        </div>
        #    """, unsafe_allow_html=True)
            
    #st.write("")
    st.markdown("""---""")

# 6) ============================== ventas por tipo de pago ==================================
def graph_tipo_pago():
     # Verificar que df_dos tenga la columna DOCUMENTOS
    if 'DOCUMENTOS' not in df_dos.columns:
        st.error(f"df_dos no tiene la columna 'DOCUMENTOS'. Columnas disponibles: {list(df_dos.columns)}")
        return
    
    # Aplicar los mismos filtros a df_dos
    df_filtrado_dos = aplicar_filtros(df_dos)
    
     # DataFrame para sumar CANTIDAD (ITEM) y contar transacciones únicas (con todos los items)
    df_items = df_filtrado_dos.groupby('MÉTODO (PAGO)').agg({
        'NÚMERO': 'nunique'  # Cuenta transacciones únicas
    }).reset_index()

    # DataFrame para sumar IMPORTE TOTAL DEL COMPROBANTE (solo una vez por transacción)
    df_importe = df_filtrado_dos.drop_duplicates(subset=['NÚMERO']).groupby('MÉTODO (PAGO)').agg({
        'IMPORTE TOTAL DEL COMPROBANTE': 'sum'  # Suma importes de transacciones únicas
    }).reset_index()

    # Combinar ambos DataFrames
    df_tipo_pago = df_importe.merge(df_items, on='MÉTODO (PAGO)', how='left')

    df_tipo_pago.rename(columns={
        'MÉTODO (PAGO)' : 'Método de Pago',
        'IMPORTE TOTAL DEL COMPROBANTE': 'Total Ventas',
        'NÚMERO': 'N° Transac.',
     }, inplace=True)

    # Ordenar por Total Ventas
    df_tipo_pago = df_tipo_pago.sort_values('Total Ventas', ascending=False).reset_index(drop=True)

    # Crear las columnas DENTRO de la función
    col1, col2 = st.columns(2)

    with col1:
        st.subheader('💳 Ventas por Método de Pago')
        fig = px.bar(
            df_tipo_pago,
            x = "Método de Pago",
            y = "Total Ventas",
            text = ['S/ {:,.2f}'.format(x) for x in df_tipo_pago["Total Ventas"]],
            template = "plotly_white",
            color = "Método de Pago",
            color_discrete_sequence = px.colors.qualitative.Pastel,
            #title=f"🧭 Período: {fecha_inicio.strftime('%d-%m-%Y')} a {fecha_fin.strftime('%d-%m-%Y')}",
            #title=dict(
            #    text=f"🧭 Período: {fecha_inicio.strftime('%d-%m-%Y')} a {fecha_fin.strftime('%d-%m-%Y')}",
            #    font=dict(size=14)  # 🔥 controla el tamaño aquí
            #),
        )

        # Cambiar color del texto a NEGRO a los datos que va dentro de las barras
        fig.update_traces(
            textposition='outside',     # 'inside' o 'outside'
            textfont = dict(
                color = 'white',       # Color negro
                size = 12,             # Tamaño de fuente
                family = 'Arial'       # Tipo de fuente
            ),
            hoverinfo='skip',  # ✅ Skip el hover
            hovertemplate=None  # ✅ Elimina el template del hover
        )
        # cambiar etiquetas a los ejes
        fig.update_layout(
            title=dict(
                text=f"🧭 Período: {fecha_inicio.strftime('%d-%m-%Y')} a {fecha_fin.strftime('%d-%m-%Y')}",
                font=dict(size=14)  # 🔥 controla el tamaño aquí
            ),
            xaxis_title="Método de Pago",        # ✅ Nuevo texto para eje X
            yaxis_title="Ventas (S/)",       # ✅ Nuevo texto para eje Y
            #xaxis_title_font=dict(size=14, color='white', family='Arial'),
            #yaxis_title_font=dict(size=14, color='white', family='Arial'),
            showlegend=False,
            height=300,
            margin=dict(l=10, r=10, t=50, b=10),
            xaxis=dict(
                showgrid=False,
                title='Método de Pago',
                #title_font_size=18            
            ),
            yaxis=dict(
                title='Ventas (S/)',
                categoryorder='total ascending',  # ✅ Forzar orden de mayor a menor
                #title_font_size=18
            ),
            dragmode=False
        )
        st.plotly_chart(fig, use_container_width = True, config={"displayModeBar": False})

    with col2:
        st.subheader("➡ Resumen")

        # Calcular los totales
        total_ventas = df_tipo_pago['Total Ventas'].sum()
        total_transacciones = df_tipo_pago['N° Transac.'].sum()

        # Crear una copia del DataFrame para no modificar el original
        df_tipo_pago_totales = df_tipo_pago.copy()

        # Agregar fila de totales
        df_tipo_pago_totales.loc['TOTAL'] = {
            'Método de Pago': 'TOTAL',
            'Total Ventas': total_ventas,
            'N° Transac.': total_transacciones
        }
         
        # Mostrar tabla con los datos
        st.dataframe(
            df_tipo_pago_totales.style
            .format({'Total Ventas': 'S/ {:,.2f}'})
            .background_gradient(cmap='Blues', subset=['Total Ventas']),
            use_container_width=True,
            hide_index=True
        )
        
        #col1, col2, col3 = st.columns(3)
        #with col2:
            # mostrar total de ventas
        #    total_ventas = df_tipo_pago['Total Ventas'].sum()
        #    st.markdown(f"""
        #        <div style="text-align: center">
        #            <div style="font-size: 0.9rem; color: #fff;">Total Ventas</div>
        #            <div style="font-size: 1.4rem; font-weight: bold; color: #fff; text-align: center">S/ {total_ventas:,.2f}</div>
        #        </div>
        #    """, unsafe_allow_html=True)
        #with col3:
            # mostrar numero de transacciones
        #    total_transacciones = df_tipo_pago['N° Transacciones'].sum()
        #    st.markdown(f"""
        #        <div style="text-align: center">
        #             <div style="font-size: 0.9rem; color: #fff;">Total Transacciones</div>
        #            <div style="font-size: 1.4rem; font-weight: bold; color: #fff; text-align: center">{total_transacciones:,.0f}</div>
        #        </div>
        #    """, unsafe_allow_html=True)

    #st.write("")
    st.markdown("""---""")

# 7) ========================== grafico ventas anuladas y descuentos ==============================
def graph_anulados():
    df_filtrado = aplicar_filtros(df, eliminar_anulados=False)

    left, right = st.columns(2)

    # ================= LEFT =================
    with left:
        st.subheader('🛑 Ventas Anuladas por Vendedor')

        df_anulados = df_filtrado[df_filtrado['ESTADO'] == 'Anulado']

        if len(df_anulados) == 0:
            st.info("No hay ventas anuladas en el período seleccionado")
        else:
            df_items = df_anulados.groupby('VENDEDOR').agg({
                'CANTIDAD (ITEM)': 'sum',
                'NÚMERO': 'nunique'
            }).reset_index()

            df_importe = df_anulados.drop_duplicates(subset=['NÚMERO']).groupby('VENDEDOR').agg({
                'IMPORTE TOTAL DEL COMPROBANTE': 'sum'
            }).reset_index()

            df_anulados = df_importe.merge(df_items, on='VENDEDOR', how='left')

            df_anulados.rename(columns={
                'VENDEDOR': 'Vendedor',
                'IMPORTE TOTAL DEL COMPROBANTE': 'Total Ventas',
                'CANTIDAD (ITEM)': 'N° Items',
                'NÚMERO': 'N° Transacciones'
            }, inplace=True)

            df_anulados = df_anulados.sort_values('Total Ventas', ascending=False).reset_index(drop=True)

            fig_anulados = px.pie(
                df_anulados,
                values="Total Ventas",
                names="Vendedor",
                template='plotly_white',
                hole=0.0
            )

            fig_anulados.update_traces(
                textposition='outside',
                textinfo='label+percent',
                texttemplate='%{label}<br>%{percent:.1%}',
                marker=dict(line=dict(color='white', width=2)),
                customdata=df_anulados[['Total Ventas', 'N° Items', 'N° Transacciones']].to_numpy(),
                hovertemplate='<b>%{label}</b><br>' +
                              '💸 Ventas Anuladas: S/ %{customdata[0][0]:,.2f}<br>' +
                              '📦 N° Items: %{customdata[0][1]:,.0f}<br>' +
                              '📄 N° Transacciones: %{customdata[0][2]:,.0f}<br>' +
                              '<extra></extra>'
            )

            fig_anulados.update_layout(
                #title=f"🧭 Período: {fecha_inicio.strftime('%d-%m-%Y')} a {fecha_fin.strftime('%d-%m-%Y')}",
                title=dict(
                    text=f"🧭 Período: {fecha_inicio.strftime('%d-%m-%Y')} a {fecha_fin.strftime('%d-%m-%Y')}",
                    font=dict(size=14)  # 🔥 controla el tamaño aquí
                ),
                showlegend=False,
                height=400
            )

            st.plotly_chart(fig_anulados, use_container_width=True, key="grafico_anulados_vendedor")

    # ================= RIGHT =================
    with right:
        st.subheader('💸 Descuentos por Vendedor')

        df_descuentos = df_filtrado[df_filtrado['DESCUENTO GLOBAL CON IGV'] > 0]

        if len(df_descuentos) == 0:
            st.info("No hay descuentos en el período seleccionado")
        else:
            df_items = df_descuentos.groupby('VENDEDOR').agg({
                'CANTIDAD (ITEM)': 'sum',
                'NÚMERO': 'nunique'
            }).reset_index()

            df_importe = df_descuentos.drop_duplicates(subset=['NÚMERO']).groupby('VENDEDOR').agg({
                'DESCUENTO GLOBAL CON IGV': 'sum'
            }).reset_index()

            df_descuentos = df_importe.merge(df_items, on='VENDEDOR', how='left')

            df_descuentos.rename(columns={
                'VENDEDOR': 'Vendedor',
                'DESCUENTO GLOBAL CON IGV': 'Total Descuentos',
                'CANTIDAD (ITEM)': 'N° Items',
                'NÚMERO': 'N° Transacciones'
            }, inplace=True)

            df_descuentos = df_descuentos.sort_values('Total Descuentos', ascending=False).reset_index(drop=True)

            fig_descuentos = px.pie(
                df_descuentos,
                values="Total Descuentos",
                names="Vendedor",
                template='plotly_white',
                hole=0.0
            )

            fig_descuentos.update_traces(
                textposition='outside',
                textinfo='label+percent',
                texttemplate='%{label}<br>%{percent:.1%}',
                marker=dict(line=dict(color='white', width=2)),
                customdata=df_descuentos[['Total Descuentos', 'N° Items', 'N° Transacciones']].to_numpy(),
                hovertemplate='<b>%{label}</b><br>' +
                              '💸 Total Descuentos: S/ %{customdata[0][0]:,.2f}<br>' +
                              '📦 N° Items: %{customdata[0][1]:,.0f}<br>' +
                              '📄 N° Transacciones: %{customdata[0][2]:,.0f}<br>' +
                              '<extra></extra>'
            )

            fig_descuentos.update_layout(
                #title=f"🧭 Período: {fecha_inicio.strftime('%d-%m-%Y')} a {fecha_fin.strftime('%d-%m-%Y')}",
                title=dict(
                    text=f"🧭 Período: {fecha_inicio.strftime('%d-%m-%Y')} a {fecha_fin.strftime('%d-%m-%Y')}",
                    font=dict(size=14)  # 🔥 controla el tamaño aquí
                ),
                showlegend=False,
                height=400
            )

            st.plotly_chart(fig_descuentos, use_container_width=True, key="grafico_descuentos_vendedor")

    # ================= DIVIDER =================
    st.markdown("""---""")

# 8) =========================== productos mas y menos vendidos ================================
def graph_productos():
    df_filtrado = aplicar_filtros(df)

    izquierda, derecha = st.columns(2)
    with izquierda:
        #st.markdown('#### ⬆ Top 10 de Productos más Vendidos')
        st.subheader('⬆ Top 10 Productos más Vendidos')
        #with st.expander('Tabla resumen'):
        with st.expander(f"🧭 Período: {fecha_inicio.strftime('%d-%m-%Y')} a {fecha_fin.strftime('%d-%m-%Y')}"):
            productos_mas = (
                df_filtrado.groupby('DESCRIPCIÓN (ITEM)')[['CANTIDAD (ITEM)']]
                .sum()
                .sort_values('CANTIDAD (ITEM)', ascending=False)
                .head(10)
                .reset_index()
            )

            productos_mas.columns = ['Descripción', 'Cantidad']
            productos_mas['Cantidad'] = productos_mas['Cantidad'].map('{:,.0f}'.format)

            styled_df = productos_mas.style \
                .background_gradient(cmap='Greens', subset=['Cantidad']) \
                .set_table_styles([{
                        'selector': 'th',
                        'props': [('background-color', '#1E3A8A'), ('color', 'white')]
                    }
                ])

            st.dataframe(
                styled_df,
                column_config={
                    "Descripción": st.column_config.Column(
                        "Descripción",
                        width="large",
                        #alignment="left"  # ✅ Funciona
                    ),
                    "Cantidad": st.column_config.Column(
                        "Cant",
                        width="small",
                        #alignment="center"  # ✅ Funciona
                    )
                },
                use_container_width=True,
                hide_index=True
            )

    with derecha:
        #st.markdown('#### ⬇ Bottom 10 de Productos menos Vendidos')
        st.subheader('⬇ Bottom 10 Productos menos Vendidos')
        #with st.expander('Tabla resumen'):
        with st.expander(f"🧭 Período: {fecha_inicio.strftime('%d-%m-%Y')} a {fecha_fin.strftime('%d-%m-%Y')}"):
            productos_mas = (
                df_filtrado.groupby('DESCRIPCIÓN (ITEM)')[['CANTIDAD (ITEM)']]
                .sum()
                .sort_values('CANTIDAD (ITEM)', ascending=True)
                .head(10)
                .reset_index()
            )

            productos_mas.columns = ['Descripción', 'Cantidad']
            productos_mas['Cantidad'] = productos_mas['Cantidad'].map('{:,.0f}'.format)

            styled_df = productos_mas.style \
                .background_gradient(cmap='Reds', subset=['Cantidad']) \
                .set_table_styles([{
                        'selector': 'th',
                        'props': [('background-color', '#1E3A8A'), ('color', 'white')]
                    }
                ])

            st.dataframe(
                styled_df,
                column_config={
                    "Descripción": st.column_config.Column(
                        "Descripción",
                        width="large",
                        #alignment="left"  # ✅ Funciona
                    ),
                    "Cantidad": st.column_config.Column(
                        "Cant",
                        width="small",
                        #alignment="center"  # ✅ Funciona
                    )
                },
                use_container_width=True,
                hide_index=True
            )

# 9)=========================== curvas x vendedor ================================
def graph_time_dia_vendedores():
    """
    Gráfico de ventas diarias por vendedor para los últimos 7 días
    """
    # Aplicar filtros sin eliminar fechas
    df_filtrado_grafico = aplicar_filtros(df, eliminar_fechas=False)
    
    # calcular fechas para el gráfico (últimos 12 días)
    fecha_fin_grafico = date2
    fecha_inicio_grafico = (date2 - pd.Timedelta(days=6)).normalize()
    
    # Filtrar datos para el período
    df_grafico = df_filtrado_grafico[
        (df_filtrado_grafico['FECHA'] >= fecha_inicio_grafico) & 
        (df_filtrado_grafico['FECHA'] <= fecha_fin_grafico)
    ].copy()
    
    if len(df_grafico) == 0:
        st.warning("No hay datos para el período seleccionado")
        return
    
    # Agrupar por día y vendedor (usando importe único por transacción)
    df_importe_unico = df_grafico.drop_duplicates(subset=['NÚMERO']).copy()
    df_importe_unico['fecha_dia'] = df_importe_unico['FECHA'].dt.to_period("D")
    
    # Agrupar por fecha y vendedor
    ventas_por_vendedor = df_importe_unico.groupby(['fecha_dia', 'VENDEDOR'])['IMPORTE TOTAL DEL COMPROBANTE'].sum().reset_index()
    
    # Crear rango completo de días
    dias_completos = pd.period_range(
        start=fecha_inicio_grafico.to_period('D'),
        end=fecha_fin_grafico.to_period('D'),
        freq='D'
    )
    
    # Obtener lista de vendedores
    vendedores = ventas_por_vendedor['VENDEDOR'].unique()
    
    # Crear DataFrame completo con todos los días y vendedores
    df_completo = pd.DataFrame()
    
    for vendedor in vendedores:
        df_vendedor = ventas_por_vendedor[ventas_por_vendedor['VENDEDOR'] == vendedor].copy()

        df_vendedor = df_vendedor.set_index('fecha_dia')[['IMPORTE TOTAL DEL COMPROBANTE']]
        df_vendedor = df_vendedor.reindex(dias_completos)
        df_vendedor['IMPORTE TOTAL DEL COMPROBANTE'] = df_vendedor['IMPORTE TOTAL DEL COMPROBANTE'].fillna(0)
        df_vendedor = df_vendedor.reset_index()
        df_vendedor.columns = ['fecha_dia', 'IMPORTE TOTAL DEL COMPROBANTE']
        df_vendedor['VENDEDOR'] = vendedor

        df_vendedor['etiqueta_x'] = df_vendedor['fecha_dia'].dt.strftime("%d/%m")
        
        df_completo = pd.concat([df_completo, df_vendedor], ignore_index=True)
    
    # Crear gráfico
    st.subheader('📈 Ventas Diarias por Vendedor')
    fig_time_dia_vendedores = go.Figure()
    
    colores = ['#FFD700', '#1E88E5', '#DC143C', '#32CD32', '#FF8C00', '#8A2BE2', '#FF69B4', '#00CED1']
    
    for i, vendedor in enumerate(vendedores):
        df_vendedor = df_completo[df_completo['VENDEDOR'] == vendedor]
        color = colores[i % len(colores)]
        
        fig_time_dia_vendedores.add_trace(go.Scatter(
            x=df_vendedor['etiqueta_x'],
            y=df_vendedor['IMPORTE TOTAL DEL COMPROBANTE'],
            mode='lines+markers',
            name=vendedor,
            line=dict(color=color, width=2),
            marker=dict(color=color, size=6, line=dict(color='white', width=0.5)),
            customdata=df_vendedor[['etiqueta_x', 'IMPORTE TOTAL DEL COMPROBANTE', 'VENDEDOR']].values,
            hovertemplate=f"Vendedor: %{{customdata[2]}}<br>" +
                          f"Día: %{{customdata[0]}}<br>" +
                          f"Ventas: S/ %{{customdata[1]:,.2f}}<br>" +
                          "<extra></extra>"
        ))
    
    if len(vendedores) > 0:
        fig_time_dia_vendedores.update_xaxes(
            tickangle=0,
            tickmode='array',
            tickvals=df_completo[df_completo['VENDEDOR'] == vendedores[0]]['etiqueta_x'].unique(),
            ticktext=df_completo[df_completo['VENDEDOR'] == vendedores[0]]['etiqueta_x'].unique()
        )
    
    fig_time_dia_vendedores.update_layout(
        #title=f"⏳ Del {fecha_inicio_grafico.strftime('%d/%m')} al {fecha_fin_grafico.strftime('%d/%m')}",
        title=dict(
            text=f"⏳ Del {fecha_inicio_grafico.strftime('%d/%m')} al {fecha_fin_grafico.strftime('%d/%m')}",
            font=dict(size=14)  # 🔥 controla el tamaño aquí
        ),
        xaxis_title="Días",
        yaxis_title="Ventas (S/)",
        showlegend=True,
        template="gridon",
        legend=dict(yanchor="top", y=1.15, xanchor="right", x=0.98, orientation="h"),
        margin=dict(l=10, r=10, t=50, b=10),
        #height=500,
        height = 300 if st.session_state.get("is_mobile", True) else 300,
        dragmode=False
    )
    
    st.plotly_chart(fig_time_dia_vendedores, use_container_width=True, config={"displayModeBar": False})
    
    # Mostrar tabla de datos - CORREGIDO
    with st.expander("Ver Datos - Ventas por Día y Vendedor", expanded=False):

        # Crear tabla pivote
        tabla_pivote = df_completo.pivot_table(
            index='etiqueta_x',
            columns='VENDEDOR',
            values='IMPORTE TOTAL DEL COMPROBANTE',
            fill_value=0
        ).reset_index()

        # ===================== AGREGAR FILA TOTAL =====================
        columnas_numericas = [col for col in tabla_pivote.columns if col != 'etiqueta_x']

        fila_total = tabla_pivote[columnas_numericas].sum()
        fila_total['etiqueta_x'] = 'TOTAL'

        # Convertir a DataFrame y ordenar columnas
        fila_total = pd.DataFrame([fila_total])[tabla_pivote.columns]

        # Concatenar al final
        tabla_pivote = pd.concat([tabla_pivote, fila_total], ignore_index=True)
        
        # Crear un diccionario con los formatos solo para las columnas numéricas
        format_dict = {}
        columnas_numericas = [col for col in tabla_pivote.columns if col != 'etiqueta_x']

        #Formato: 2 decimales con separador de miles
        #format_dict = {col: '{:,.2f}' for col in columnas_numericas}
        format_dict = {col: 'S/ {:,.2f}' for col in columnas_numericas}

        styled_df = tabla_pivote.style.format(format_dict) \
            .background_gradient(cmap='Purples', subset=columnas_numericas) \
            .set_table_styles([{
                'selector': 'th',
                'props': [('background-color', '#1E3A8A'), ('color', 'white')]
            }])

        st.dataframe(
                styled_df,
                column_config={
                    "etiqueta_x": st.column_config.Column(
                        "Día",
                        width="small",
                        #alignment="left"  # ✅ Funciona
                    ),
                },
                use_container_width=True,
                hide_index=True
            )
        
        # Descargar datos
        csv = tabla_pivote.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Descargar Data",
            data=csv,
            file_name="ventas_por_dia_vendedor.csv",
            mime="text/csv",
            help="Click aquí para descargar los datos",
            use_container_width=True
        )
    
    st.markdown("""---""")

# 10) ========================== metricas para cada vendedor ====================================
import streamlit.components.v1 as components

def metricas_vendedor():

    df_filtrado = aplicar_filtros(df)
    
    if len(df_filtrado) == 0:
        st.warning("No hay datos para mostrar")
        return
    
    df_limpio = df_filtrado.copy()
    df_limpio['VENDEDOR_LIMPIO'] = df_limpio['VENDEDOR'].apply(limpiar_nombre_vendedor)
    
    ventas_por_vendedor = df_limpio.drop_duplicates(subset=['NÚMERO']) \
        .groupby('VENDEDOR_LIMPIO')['IMPORTE TOTAL DEL COMPROBANTE'].sum()

    transacciones_por_vendedor = df_limpio.groupby('VENDEDOR_LIMPIO')['NÚMERO'].nunique()
    items_por_vendedor = df_limpio.groupby('VENDEDOR_LIMPIO')['CANTIDAD (ITEM)'].sum()
    
    ticket_promedio = (ventas_por_vendedor / transacciones_por_vendedor).fillna(0)
    items_x_transaccion = (items_por_vendedor / transacciones_por_vendedor).fillna(0)
    
    st.subheader("📊 Métricas por Vendedor")
    
    vendedores = ventas_por_vendedor.index.tolist()
    total_ventas_general = ventas_por_vendedor.sum()

    # ===================== HTML RESPONSIVE =====================
    html_total = '''
    <div class="cards-container">
    <style>
    .cards-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
    }

    @media (max-width: 1024px) {
        .cards-container {
            grid-template-columns: repeat(3, 1fr);
        }
    }

    @media (max-width: 768px) {
        .cards-container {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    .card {
        background: white;
        border-radius: 12px;
        padding: 14px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 3px 6px rgba(0,0,0,0.05);
        font-family: Arial, sans-serif;
    }

    .card-title {
        display:flex;
        justify-content:space-between;
        font-weight:bold;
        color:#111;
        margin-bottom:6px;
    }

    .badge {
        background:#eee;
        padding:3px 8px;
        border-radius:10px;
        font-size:12px;
    }

    .metric {
        font-size:20px;
        font-weight:bold;
    }

    .label {
        font-size:12px;
        color:#666;
    }

    .row {
        display:flex;
        justify-content:space-between;
        margin-top:8px;
    }
    </style>
    '''

    for vendedor in vendedores:
        ventas = ventas_por_vendedor[vendedor]
        transacciones = transacciones_por_vendedor[vendedor]
        items = items_por_vendedor[vendedor]
        ticket = ticket_promedio[vendedor]
        items_x_trans = items_x_transaccion[vendedor]
        
        porcentaje = (ventas / total_ventas_general * 100) if total_ventas_general > 0 else 0
        
        if vendedor.lower() == "admin":
            icono = "👑"
        elif vendedor.lower() == "briyic":
            icono = "⭐"
        else:
            icono = "👤"
        
        html_total += f'''
        <div class="card">

            <div class="card-title">
                <span>{icono} {vendedor}</span>
                <span class="badge">{porcentaje:.1f}%</span>
            </div>

            <div class="label">Total Ventas</div>
            <div class="metric">S/ {ventas:,.2f}</div>

            <div class="row">
                <div>
                    <div class="label">Transacciones</div>
                    <b>{transacciones}</b>
                </div>
                <div>
                    <div class="label">Items</div>
                    <b>{items}</b>
                </div>
            </div>

            <div class="row">
                <div>
                    <div class="label">Ticket</div>
                    <b>S/ {ticket:,.2f}</b>
                </div>
                <div>
                    <div class="label">Items/Tx</div>
                    <b>{items_x_trans:.1f}</b>
                </div>
            </div>

        </div>
        '''

    html_total += '</div>'

    # Altura dinámica (evita espacios muertos)
    import math

    num_vendedores = len(vendedores)

    # Calcular filas para desktop (4 columnas)
    filas_desktop = math.ceil(num_vendedores / 4)

    # Altura real por tarjeta (ajustada)
    altura_por_fila = 180

    # Altura base + margen de seguridad
    altura = filas_desktop * altura_por_fila + 40

    components.html(html_total, height=altura, scrolling=True)

    st.markdown("---")

# ============================= funcion filtros ==========================================
def aplicar_filtros(df_datos, eliminar_anulados=True, eliminar_fechas=True):
    """
    Aplica los mismos filtros que se usaron en df_filtrado
    """
    df_temp = df_datos.copy()
    
    # Filtro 1: Eliminar anulados (si existe la columna y se solicita)
    if eliminar_anulados and 'ESTADO' in df_temp.columns:
        df_temp = df_temp[df_temp['ESTADO'] != 'Anulado'].copy()
    
    # Filtro 2: Filtro de fechas
    if eliminar_fechas and 'FECHA' in df_temp.columns:
        # Asegurar que la columna FECHA sea datetime
        if not pd.api.types.is_datetime64_any_dtype(df_temp['FECHA']):
            df_temp["FECHA"] = pd.to_datetime(df_temp["FECHA"])
        
        df_temp = df_temp[(df_temp["FECHA"] >= date1) & (df_temp["FECHA"] <= date2)].copy()
    
    # Filtro 3: Filtro por tipo de documento
    if tipo_documento and len(tipo_documento) > 0 and 'DOCUMENTOS' in df_temp.columns:
        # IMPORTANTE: Resetear el índice antes de crear la máscara
        df_temp = df_temp.reset_index(drop=True)
        
        # Crear la máscara
        mask = pd.Series([False] * len(df_temp))
        
        # Convertir a string para evitar errores
        doc_str = df_temp['DOCUMENTOS'].astype(str)
        
        if 'Factura' in tipo_documento:
            mask = mask | doc_str.str.startswith('F', na=False)
        if 'Boleta' in tipo_documento:
            mask = mask | doc_str.str.startswith('B', na=False)
        if 'Ticket' in tipo_documento:
            mask = mask | df_temp['DOCUMENTOS'].isna() | \
                    doc_str.str.strip().eq('') | \
                    doc_str.str.contains('^\s*$', na=True)
        
        # Aplicar el filtro
        df_temp = df_temp[mask].copy()
    
    # Resetear índice final
    df_temp = df_temp.reset_index(drop=True)
    
    return df_temp

#========================== funcion limpia nombres ==============================
def limpiar_nombre_vendedor(nombre):
    """
    Limpia y formatea nombres de vendedores dinámicamente
    """
    if pd.isna(nombre):
        return "Sin asignar"
    
    nombre = str(nombre).strip()
    
    # Manejar nombres vacíos
    if not nombre or nombre.isspace():
        return "Sin asignar"
    
    # Convertir a minúsculas para procesar
    nombre_lower = nombre.lower()
    
    # Casos especiales (solo para transformaciones comunes)
    if nombre_lower == 'store' or nombre_lower == 'store.':
        return "Admin"
    
    # Si tiene formato 'store.algo' o 'store algo'
    if 'store.' in nombre_lower:
        parte = nombre_lower.split('.')[-1]
        if parte and parte != 'store':
            # Capitalizar y limitar longitud
            nombre_limpio = parte.capitalize()
            return nombre_limpio[:6] + "." if len(nombre_limpio) > 6 else nombre_limpio
        return "Admin"
    
    if 'store' in nombre_lower and nombre_lower != 'store':
        # Extraer la parte después de 'store'
        parte = nombre_lower.replace('store', '').strip(' .')
        if parte:
            nombre_limpio = parte.capitalize()
            return nombre_limpio[:6] + "." if len(nombre_limpio) > 6 else nombre_limpio
    
    # Para cualquier otro nombre, capitalizar y limitar longitud
    nombre_limpio = nombre.capitalize()
    
    # Limitar a 6 caracteres
    if len(nombre_limpio) > 6:
        nombre_limpio = nombre_limpio[:6] + "."
    
    return nombre_limpio

# n) ===================================== menu lateral =========================================
def sidebar():
    with st.sidebar:
        selected = option_menu(
            menu_title = "Main Menú",
            options = ["Ventas", "Compras", "Productos", "Vendedores"],
            icons = ["cart4", "bag", "p-circle", "people-fill"],
            menu_icon = "cast",
            default_index = 0
        )
    if selected == "Ventas":
        st.subheader(f"🛒 Página: {selected}")
        st.markdown("""---""")

        metricas()
        graph_time_dia()
        graph_time_mes()

        df_filtrado = aplicar_filtros(df)
        if len(df_filtrado) > 0:
            #st.write(f"**Total de registros filtrados:** {len(df_filtrado)}")
            graph_categoria()
            graph_vendedor()
            graph_tipo_pago()
            graph_anulados()
            graph_productos()
        else:
            st.error("No hay datos para los filtros seleccionados")

    if selected == "Compras":
        st.subheader(f"Página: {selected}")
        st.markdown("""---""")
        st.info("🚧 Página en construcción")

    if selected == "Productos":
        st.subheader(f"Página: {selected}")
        st.markdown("""---""")
        st.info("🚧 Página en construcción")

    if selected == "Vendedores":
        st.subheader(f"Página: {selected}")
        st.markdown("""---""")
        metricas_vendedor()
        graph_time_dia_vendedores()
        #st.info("🚧 Página en construcción")
    
sidebar()
#st.dataframe(df_filtrado)
