import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_option_menu import option_menu

from tools import (
    PAYMENTS_REQUIRED_COLUMNS,
    SALES_REQUIRED_COLUMNS,
    apply_filters,
    aggregate_sales_by_key,
    aggregate_sales_by_key_without_items,
    aggregate_unique_transaction_amount,
    ensure_datetime_column,
    fill_period_range,
    load_excel_file,
    limpiar_nombre_vendedor,
    validate_dataframe_columns,
)


st.set_page_config(page_title='Dashboard', page_icon='🌎', layout='wide')
st.subheader('🏠 Tienda Av. Larco 986')

st.markdown(
    '''
    <style>
        div.block-container {padding-top:2.6rem; padding-left: 0.75rem; padding-right: 0.75rem;}
        .stApp hr {
            margin-top: -15px !important;
            margin-bottom: 15px !important;
        }
        @media (max-width: 768px) {
            div.block-container {padding-top: 1.1rem; padding-left: 0.5rem; padding-right: 0.5rem;}
        }
    </style>
    ''',
    unsafe_allow_html=True,
)


def is_mobile_view() -> bool:
    params = st.query_params
    if 'mobile' in params:
        return str(params['mobile'][0]).lower() in ('true', '1', 'yes')

    st.html(
        """
        <script>
        function updateMobileParam() {
            const width = window.visualViewport?.width || window.innerWidth || document.documentElement.clientWidth;
            const isMobile = width <= 768;
            const params = new URLSearchParams(window.location.search);
            params.set('mobile', isMobile ? 'true' : 'false');
            const newSearch = '?' + params.toString();
            if (window.location.search !== newSearch) {
                window.location.replace(newSearch);
            }
        }
        updateMobileParam();
        if (window.visualViewport) {
            window.visualViewport.addEventListener('resize', updateMobileParam);
        } else {
            window.addEventListener('resize', updateMobileParam);
        }
        </script>
        """,
        unsafe_allow_javascript=True,
    )
    return False




def cargar_datos():
    df_ventas = load_excel_file('data/ventas.xlsx', skiprows=8)
    df_pagos = load_excel_file('data/pagos.xlsx', skiprows=4)

    if not validate_dataframe_columns(df_ventas, SALES_REQUIRED_COLUMNS, 'ventas'):
        st.stop()
    if not validate_dataframe_columns(df_pagos, PAYMENTS_REQUIRED_COLUMNS, 'pagos'):
        st.stop()

    df_ventas = ensure_datetime_column(df_ventas, 'FECHA')
    df_pagos = ensure_datetime_column(df_pagos, 'FECHA')

    return df_ventas, df_pagos


df, df_dos = cargar_datos()


with st.sidebar:
    box_date = datetime.datetime.now().strftime('%d %B %Y')
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.image(
            'data/logoRF.png',
            caption=f'Actualizado el :  \n {box_date}',
            width=150,
        )


start_date = datetime.datetime.now().replace(day=1)
end_date = df['FECHA'].max()

col1, col2 = st.columns(2)
with col1:
    fecha_inicio = st.date_input('Fecha Inicial', value=start_date, format='DD/MM/YYYY')
    date1 = pd.to_datetime(fecha_inicio)
with col2:
    fecha_fin = st.date_input('Fecha Final', value=end_date, format='DD/MM/YYYY')
    date2 = pd.to_datetime(fecha_fin) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

if fecha_inicio > fecha_fin:
    st.error('❌ Error: La fecha inicial no puede ser mayor que la fecha final')
    st.stop()

st.sidebar.header('Filtros: ')

tipo_documento = st.sidebar.multiselect(
    '📍 Selecciona Tipo de Documento',
    options=['Factura', 'Boleta', 'Ticket'],
    placeholder='Opciones',
    help='Selecciona uno o más tipos de documento',
)


def metricas():
    df_filtrado = apply_filters(df, tipo_documento, date1, date2)
    ventas_total = df_filtrado.drop_duplicates(subset=['NÚMERO'])['IMPORTE TOTAL DEL COMPROBANTE'].sum()
    num_transacciones = df_filtrado['NÚMERO'].nunique()
    total_items = df_filtrado['CANTIDAD (ITEM)'].sum()

    if num_transacciones > 0:
        promedio_ventas = df_filtrado.groupby('NÚMERO')['TOTAL (ITEM)'].sum().mean()
        items_por_transaccion = df_filtrado.groupby('NÚMERO')['CANTIDAD (ITEM)'].sum().mean()
    else:
        promedio_ventas = 0
        items_por_transaccion = 0

    total1, total2, total3, total4, total5 = st.columns(5, gap='small')
    with total1:
        st.info('Total en Ventas', icon='💰')
        st.metric('Suma Total S/', f'{ventas_total:,.2f}')
    with total2:
        st.info('Items Vendidos', icon='📦')
        st.metric('Total Items', f'{total_items:,}')
    with total3:
        st.info('Transacciones', icon='🛒')
        st.metric('N° Transacciones', f'{num_transacciones:,}')
    with total4:
        st.info('Ventas Promedio', icon='📊')
        st.metric('Ventas / Transacción', f'{promedio_ventas:,.2f}')
    with total5:
        st.info('Items Promedio', icon='📁')
        st.metric('Items Vendidos / Transacción', f'{items_por_transaccion:,.2f}')

    st.markdown('---')


def graph_time_dia():
    df_filtrado_grafico = apply_filters(df, tipo_documento, date1, date2, eliminar_fechas=False)
    fecha_fin_grafico = date2
    fecha_inicio_grafico = (date2 - pd.Timedelta(days=6)).normalize() if is_mobile_view() else (date2 - pd.Timedelta(days=12)).normalize()
    fecha_fin_anterior = fecha_fin_grafico - pd.DateOffset(years=1)
    fecha_inicio_anterior = fecha_inicio_grafico - pd.DateOffset(years=1)

    df_grafico = df_filtrado_grafico[(df_filtrado_grafico['FECHA'] >= fecha_inicio_grafico) & (df_filtrado_grafico['FECHA'] <= fecha_fin_grafico)].copy()
    df_grafico_anterior = df_filtrado_grafico[(df_filtrado_grafico['FECHA'] >= fecha_inicio_anterior) & (df_filtrado_grafico['FECHA'] <= fecha_fin_anterior)].copy()

    ventas_diarias = aggregate_unique_transaction_amount(df_grafico, 'D')
    ventas_anterior_diarias = aggregate_unique_transaction_amount(df_grafico_anterior, 'D')

    dias_completos = pd.period_range(start=fecha_inicio_grafico.to_period('D'), end=fecha_fin_grafico.to_period('D'), freq='D')
    dias_completos_anterior = pd.period_range(start=fecha_inicio_anterior.to_period('D'), end=fecha_fin_anterior.to_period('D'), freq='D')

    ventas_completas = fill_period_range(ventas_diarias, dias_completos)
    ventas_completas['etiqueta_x'] = ventas_completas['period'].dt.strftime('%d/%m')

    ventas_anterior_completas = fill_period_range(ventas_anterior_diarias, dias_completos_anterior)
    ventas_anterior_completas['etiqueta_x'] = ventas_anterior_completas['period'].dt.strftime('%d/%m')

    st.subheader('📉 Ventas Diarias')
    fig_time_dia = go.Figure()
    fig_time_dia.add_trace(go.Scatter(
        x=ventas_completas['etiqueta_x'],
        y=ventas_completas['TOTAL (ITEM)'],
        mode='lines+markers',
        name=f'Año {date2.year}',
        line=dict(color='#FFD700', width=2),
        marker=dict(color='#FFD700', size=8, line=dict(color='white', width=0.5)),
        customdata=ventas_completas[['etiqueta_x', 'TOTAL (ITEM)']].values,
        hovertemplate=f'Día : ' + '%{customdata[0]}<br>' + 'Ventas =  S/ %{customdata[1]:,.2f}<br>' + '<extra></extra>',
    ))
    fig_time_dia.add_trace(go.Scatter(
        x=ventas_anterior_completas['etiqueta_x'],
        y=ventas_anterior_completas['TOTAL (ITEM)'],
        mode='lines+markers',
        name=f'Año {date2.year-1}',
        line=dict(color='#1E88E5', width=2),
        marker=dict(color='#1E88E5', size=8, line=dict(color='white', width=0.5)),
        customdata=ventas_anterior_completas[['etiqueta_x', 'TOTAL (ITEM)']].values,
        hovertemplate=f'Día : ' + '%{customdata[0]}<br>' + 'Ventas =  S/ %{customdata[1]:,.2f}<br>' + '<extra></extra>',
    ))

    fig_time_dia.update_xaxes(tickangle=0, tickmode='array', tickvals=ventas_completas['etiqueta_x'], ticktext=ventas_completas['etiqueta_x'])
    fig_time_dia.update_layout(
        title=f"⏳ Del {fecha_inicio_grafico.strftime('%d/%m')} al {fecha_fin_grafico.strftime('%d/%m')}",
        xaxis_title='Días',
        xaxis_title_font_size=19,
        yaxis_title='Ventas (S/)',
        yaxis_title_font_size=19,
        template='gridon',
        legend=dict(yanchor='top', y=1.20, xanchor='right', x=0.96),
        margin=dict(l=10, r=10, t=0, b=10),
        width=1000,
    )
    st.plotly_chart(fig_time_dia, use_container_width=True, config={"staticPlot": True,"displayModeBar": False})

    cl1, cl2 = st.columns(2)
    with cl1:
        with st.expander('Ver Datos - Ventas por Días', expanded=False):
            df_combinado = pd.DataFrame({
                'Día': ventas_completas['etiqueta_x'],
                f'Ventas (S/) - {date2.year-1}': ventas_anterior_completas['TOTAL (ITEM)'],
                f'Ventas (S/) - {date2.year}': ventas_completas['TOTAL (ITEM)'],
            })
            styled_df = df_combinado.style.background_gradient(cmap='cividis', subset=[f'Ventas (S/) - {date2.year}', f'Ventas (S/) - {date2.year-1}']).format({f'Ventas (S/) - {date2.year}': '{:,.2f}', f'Ventas (S/) - {date2.year-1}': '{:,.2f}'})
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            csv_ventas_dia = df_combinado.copy()
            csv_ventas_dia[f'Ventas (S/) - {date2.year}'] = csv_ventas_dia[f'Ventas (S/) - {date2.year}'].map('{:.2f}'.format)
            csv_ventas_dia[f'Ventas (S/) - {date2.year-1}'] = csv_ventas_dia[f'Ventas (S/) - {date2.year-1}'].map('{:.2f}'.format)
            csv = csv_ventas_dia.to_csv(index=False).encode('utf-8')
            st.download_button('📥 Descargar Data', data=csv, file_name='ventas_por_dia.csv', mime='text/csv', help='Click aqui para descargar los datos en un archivo CSV', use_container_width=True)
    st.write('')
    st.markdown('---')


def graph_time_mes():
    df_filtrado_grafico = apply_filters(df, tipo_documento, date1, date2, eliminar_fechas=False)
    fecha_fin_grafico = date2
    fecha_inicio_grafico = pd.Timestamp(year=date2.year, month=1, day=1)
    fecha_fin_anterior = fecha_fin_grafico - pd.DateOffset(years=1)
    fecha_inicio_anterior = pd.Timestamp(year=fecha_fin_anterior.year, month=1, day=1)

    df_grafico = df_filtrado_grafico[(df_filtrado_grafico['FECHA'] >= fecha_inicio_grafico) & (df_filtrado_grafico['FECHA'] <= fecha_fin_grafico)].copy()
    df_grafico_anterior = df_filtrado_grafico[(df_filtrado_grafico['FECHA'] >= fecha_inicio_anterior) & (df_filtrado_grafico['FECHA'] <= fecha_fin_anterior)].copy()

    ventas_mensuales = aggregate_unique_transaction_amount(df_grafico, 'M')
    ventas_anterior = aggregate_unique_transaction_amount(df_grafico_anterior, 'M')

    meses_completos = pd.period_range(start=fecha_inicio_grafico.to_period('M'), end=fecha_fin_grafico.to_period('M'), freq='M')
    meses_completos_anterior = pd.period_range(start=fecha_inicio_anterior.to_period('M'), end=fecha_fin_anterior.to_period('M'), freq='M')

    ventas_completas = fill_period_range(ventas_mensuales, meses_completos)
    ventas_completas['etiqueta_x'] = ventas_completas['period'].dt.strftime('%b')
    ventas_anterior_completas = fill_period_range(ventas_anterior, meses_completos_anterior)
    ventas_anterior_completas['etiqueta_x'] = ventas_anterior_completas['period'].dt.strftime('%b')

    st.subheader('📈 Ventas Mensuales')
    fig_time_mes = go.Figure()
    fig_time_mes.add_trace(go.Scatter(
        x=ventas_completas['etiqueta_x'],
        y=ventas_completas['TOTAL (ITEM)'],
        mode='lines+markers',
        name=f'Año {date2.year}',
        line=dict(color='#FFD700', width=2),
        marker=dict(color='#FFD700', size=8, line=dict(color='white', width=0.5)),
        customdata=ventas_completas[['etiqueta_x', 'TOTAL (ITEM)']].values,
        hovertemplate=f'Año - Mes : {date2.year} - ' + '%{customdata[0]}<br>' + 'Ventas =  S/ %{customdata[1]:,.2f}<br>' + '<extra></extra>',
    ))
    fig_time_mes.add_trace(go.Scatter(
        x=ventas_anterior_completas['etiqueta_x'],
        y=ventas_anterior_completas['TOTAL (ITEM)'],
        mode='lines+markers',
        name=f'Año {date2.year-1}',
        line=dict(color='#1E88E5', width=2),
        marker=dict(color='#1E88E5', size=8, line=dict(color='white', width=0.5)),
        customdata=ventas_anterior_completas[['etiqueta_x', 'TOTAL (ITEM)']].values,
        hovertemplate=f'Año - Mes : {date2.year-1} - ' + '%{customdata[0]}<br>' + 'Ventas =  S/ %{customdata[1]:,.2f}<br>' + '<extra></extra>',
    ))

    fig_time_mes.update_layout(
        title=f'⏳ Comparativa: {date2.year-1} vs {date2.year}',
        xaxis_title='Mes',
        xaxis_title_font_size=19,
        yaxis_title='Ventas (S/)',
        yaxis_title_font_size=19,
        template='gridon',
        legend=dict(yanchor='top', y=1.20, xanchor='right', x=0.96),
        margin=dict(l=10, r=10, t=0, b=10),
        width=1000,
    )
    fig_time_mes.update_xaxes(tickangle=0, tickmode='array', tickvals=ventas_completas['etiqueta_x'], ticktext=ventas_completas['etiqueta_x'])
    st.plotly_chart(fig_time_mes, use_container_width=True, config={"staticPlot": True,"displayModeBar": False})

    cl1, cl2 = st.columns(2)
    with cl1:
        with st.expander('Ver Datos - Ventas por Mes', expanded=False):
            df_combinado = pd.DataFrame({
                'Mes': ventas_completas['etiqueta_x'],
                f'Ventas (S/) - {date2.year-1}': ventas_anterior_completas['TOTAL (ITEM)'],
                f'Ventas (S/) - {date2.year}': ventas_completas['TOTAL (ITEM)'],
            })
            styled_df = df_combinado.style.background_gradient(cmap='cividis', subset=[f'Ventas (S/) - {date2.year}', f'Ventas (S/) - {date2.year-1}']).format({f'Ventas (S/) - {date2.year}': '{:,.2f}', f'Ventas (S/) - {date2.year-1}': '{:,.2f}'})
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            csv_ventas_mes = df_combinado.copy()
            csv_ventas_mes[f'Ventas (S/) - {date2.year}'] = csv_ventas_mes[f'Ventas (S/) - {date2.year}'].map('{:.2f}'.format)
            csv_ventas_mes[f'Ventas (S/) - {date2.year-1}'] = csv_ventas_mes[f'Ventas (S/) - {date2.year-1}'].map('{:.2f}'.format)
            csv = csv_ventas_mes.to_csv(index=False).encode('utf-8')
            st.download_button('📥 Descargar Data', data=csv, file_name='ventas_por_mes.csv', mime='text/csv', help='Click aqui para descargar los datos en un archivo CSV', use_container_width=True)
    st.write('')
    st.markdown('---')


def graph_categoria():
    df_filtrado = apply_filters(df, tipo_documento, date1, date2)
    df_categoria = aggregate_sales_by_key(df_filtrado, 'CATEGORÍA (ITEM)')
    df_categoria = df_categoria[['CATEGORÍA (ITEM)', 'IMPORTE TOTAL DEL COMPROBANTE', 'CANTIDAD (ITEM)', 'NÚMERO']]
    df_categoria.rename(columns={
        'CATEGORÍA (ITEM)': 'Categoría',
        'IMPORTE TOTAL DEL COMPROBANTE': 'Total Ventas',
        'NÚMERO': 'N° Transacciones',
        'CANTIDAD (ITEM)': 'N° Items',
    }, inplace=True)
    df_categoria = df_categoria.sort_values('Total Ventas', ascending=False).reset_index(drop=True).head(10)

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
            text='Total Ventas',
        )
        fig_categoria.update_traces(
            texttemplate='S/ %{x:,.2f}',
            textposition='inside',
            marker=dict(line=dict(color='white', width=1)),
            customdata=df_categoria[['Categoría', 'Total Ventas', 'N° Items']].values,
            hovertemplate='Cantidad = %{customdata[2]}<extra></extra>',
        )
        fig_categoria.update_layout(
            title=f"🧭 Período: {fecha_inicio.strftime('%d-%m-%Y')} a {fecha_fin.strftime('%d-%m-%Y')}",
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, title='Ventas (S/)', title_font_size=19),
            yaxis=dict(title='Categoría', categoryorder='total ascending', title_font_size=19),
            margin=dict(l=10, r=10, t=50, b=10),
            height=422,
        )
        st.plotly_chart(fig_categoria, use_container_width=True, config={"staticPlot": True,"displayModeBar": False})

    with col2:
        st.subheader('➡ Resumen')
        total_ventas = df_categoria['Total Ventas'].sum()
        total_cantidad = df_categoria['N° Items'].sum()
        total_transacciones = df_categoria['N° Transacciones'].sum()
        df_categoria_con_totales = df_categoria.copy()
        df_categoria_con_totales.loc['TOTAL'] = {
            'Categoría': 'TOTAL',
            'Total Ventas': total_ventas,
            'N° Items': total_cantidad,
            'N° Transacciones': total_transacciones,
        }
        st.dataframe(
            df_categoria_con_totales.style.format({'Total Ventas': 'S/ {:,.2f}', 'N° Items': '{:,.0f}', 'N° Transacciones': '{:,.0f}'}).background_gradient(cmap='Greens', subset=['Total Ventas']),
            use_container_width=True,
            hide_index=True,
            height=422,
        )
    st.write('')
    st.markdown('---')


def graph_vendedor():
    df_filtrado = apply_filters(df, tipo_documento, date1, date2)
    left, right = st.columns(2)
    with left:
        st.subheader('👨‍💻 Ventas por Vendedor')
        df_vendedor = aggregate_sales_by_key(df_filtrado, 'VENDEDOR')
        df_vendedor = df_vendedor[['VENDEDOR', 'IMPORTE TOTAL DEL COMPROBANTE', 'CANTIDAD (ITEM)', 'NÚMERO']]
        df_vendedor.rename(columns={
            'VENDEDOR': 'Vendedor',
            'IMPORTE TOTAL DEL COMPROBANTE': 'Total Ventas',
            'NÚMERO': 'N° Transacciones',
            'CANTIDAD (ITEM)': 'N° Items',
        }, inplace=True)
        df_vendedor = df_vendedor.sort_values('Total Ventas', ascending=False).reset_index(drop=True)
        fig_vendedor = px.pie(df_vendedor, values='Total Ventas', names='Vendedor', template='gridon', hole=0.5)
        fig_vendedor.update_traces(
            textposition='outside',
            textinfo='label+percent',
            texttemplate='%{label}<br>%{percent:.2%}',
            marker=dict(line=dict(color='white', width=2)),
            customdata=df_vendedor[['Vendedor', 'Total Ventas']].values,
            hovertemplate='<b>%{label}</b><br>' + 'Ventas: S/ %{value:,.2f}<br>' + '<extra></extra>',
        )
        fig_vendedor.update_layout(title=f"🧭 Período: {fecha_inicio.strftime('%d-%m-%Y')} a {fecha_fin.strftime('%d-%m-%Y')}", showlegend=False, height=400)
        st.plotly_chart(fig_vendedor, use_container_width=True, config={"staticPlot": True,"displayModeBar": False})

    with right:
        st.subheader('➡ Resumen')
        df_vendedor.columns = ['Vendedor', 'Total Ventas', 'N° Items', 'N° Transacciones']
        st.dataframe(df_vendedor.style.format({'Total Ventas': 'S/ {:,.2f}'}).background_gradient(cmap='Oranges', subset=['Total Ventas']), use_container_width=True, hide_index=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            total_ventas = df_vendedor['Total Ventas'].sum()
            st.markdown(f"""
                <div style='text-align: center'>
                    <div style='font-size: 0.9rem; color: #fff;'>Total Ventas</div>
                    <div style='font-size: 1.4rem; font-weight: bold; color: #fff; text-align: center'>S/ {total_ventas:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            total_items = df_vendedor['N° Items'].sum()
            st.markdown(f"""
                <div style='text-align: center'>
                    <div style='font-size: 0.9rem; color: #fff;'>Total Items</div>
                    <div style='font-size: 1.4rem; font-weight: bold; color: #fff; text-align: center'>{total_items:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            total_transacciones = df_vendedor['N° Transacciones'].sum()
            st.markdown(f"""
                <div style='text-align: center'>
                    <div style='font-size: 0.9rem; color: #fff;'>Total Transacciones</div>
                    <div style='font-size: 1.4rem; font-weight: bold; color: #fff; text-align: center'>{total_transacciones:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown('---')


def graph_tipo_pago():
    if 'DOCUMENTOS' not in df_dos.columns:
        st.error(f"df_dos no tiene la columna 'DOCUMENTOS'. Columnas disponibles: {list(df_dos.columns)}")
        return

    df_filtrado_dos = apply_filters(df_dos, tipo_documento, date1, date2)
    df_tipo_pago = aggregate_sales_by_key_without_items(df_filtrado_dos, 'MÉTODO (PAGO)')
    df_tipo_pago.rename(columns={
        'MÉTODO (PAGO)': 'Método de Pago',
        'IMPORTE TOTAL DEL COMPROBANTE': 'Total Ventas',
        'NÚMERO': 'N° Transacciones',
    }, inplace=True)
    df_tipo_pago = df_tipo_pago.sort_values('Total Ventas', ascending=False).reset_index(drop=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader('💳 Ventas por Método de Pago')
        fig = px.bar(
            df_tipo_pago,
            x='Método de Pago',
            y='Total Ventas',
            text=['S/ {:,.2f}'.format(x) for x in df_tipo_pago['Total Ventas']],
            template='plotly_white',
            color='Método de Pago',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            title=f"🧭 Período: {fecha_inicio.strftime('%d-%m-%Y')} a {fecha_fin.strftime('%d-%m-%Y')}",
        )
        fig.update_traces(
            textposition='outside',
            textfont=dict(color='white', size=12, family='Arial'),
            hoverinfo='skip',
            hovertemplate=None,
        )
        fig.update_layout(
            xaxis_title='Método de Pago',
            yaxis_title='Ventas (S/)',
            xaxis_title_font=dict(size=14, color='white', family='Arial'),
            yaxis_title_font=dict(size=14, color='white', family='Arial'),
            showlegend=False,
            height=300,
            margin=dict(l=10, r=10, t=50, b=10),
            xaxis=dict(showgrid=False, title='Método de Pago', title_font_size=18),
            yaxis=dict(title='Ventas (S/)', categoryorder='total ascending', title_font_size=18),
        )
        st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True,"displayModeBar": False})

    with col2:
        st.subheader('➡ Resumen')
        st.dataframe(df_tipo_pago.style.format({'Total Ventas': 'S/ {:,.2f}'}).background_gradient(cmap='Blues', subset=['Total Ventas']), use_container_width=True, hide_index=True)
        col1, col2, col3 = st.columns(3)
        with col2:
            total_ventas = df_tipo_pago['Total Ventas'].sum()
            st.markdown(f"""
                <div style='text-align: center'>
                    <div style='font-size: 0.9rem; color: #fff;'>Total Ventas</div>
                    <div style='font-size: 1.4rem; font-weight: bold; color: #fff; text-align: center'>S/ {total_ventas:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            total_transacciones = df_tipo_pago['N° Transacciones'].sum()
            st.markdown(f"""
                <div style='text-align: center'>
                    <div style='font-size: 0.9rem; color: #fff;'>Total Transacciones</div>
                    <div style='font-size: 1.4rem; font-weight: bold; color: #fff; text-align: center'>{total_transacciones:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)
    st.write('')
    st.markdown('---')


def graph_anulados():
    df_filtrado = apply_filters(df, tipo_documento, date1, date2, eliminar_anulados=False)
    left, right = st.columns(2)
    with left:
        st.subheader('🛑 Ventas Anuladas por Vendedor')
        df_anulados = df_filtrado[df_filtrado['ESTADO'] == 'Anulado']
        if df_anulados.empty:
            st.info('No hay ventas anuladas en el período seleccionado')
            return
        df_items = df_anulados.groupby('VENDEDOR').agg({'CANTIDAD (ITEM)': 'sum', 'NÚMERO': 'nunique'}).reset_index()
        df_importe = df_anulados.drop_duplicates(subset=['NÚMERO']).groupby('VENDEDOR').agg({'IMPORTE TOTAL DEL COMPROBANTE': 'sum'}).reset_index()
        df_anulados = df_importe.merge(df_items, on='VENDEDOR', how='left')
        df_anulados.rename(columns={
            'VENDEDOR': 'Vendedor',
            'IMPORTE TOTAL DEL COMPROBANTE': 'Total Ventas',
            'CANTIDAD (ITEM)': 'N° Items',
            'NÚMERO': 'N° Transacciones',
        }, inplace=True)
        df_anulados = df_anulados.sort_values('Total Ventas', ascending=False).reset_index(drop=True)
        fig_anulados = px.pie(df_anulados, values='Total Ventas', names='Vendedor', template='plotly_white', hole=0.0)
        fig_anulados.update_traces(
            textposition='outside',
            textinfo='label+percent',
            texttemplate='%{label}<br>%{percent:.1%}',
            marker=dict(line=dict(color='white', width=2)),
            customdata=df_anulados[['Total Ventas', 'N° Items', 'N° Transacciones']].to_numpy(),
            hovertemplate='<b>%{label}</b><br>' + '💸 Ventas Anuladas: S/ %{customdata[0][0]:,.2f}<br>' + '📦 N° Items: %{customdata[0][1]:,.0f}<br>' + '📄 N° Transacciones: %{customdata[0][2]:,.0f}<br>' + '<extra></extra>',
        )
        fig_anulados.update_layout(title=f"🧭 Período: {fecha_inicio.strftime('%d-%m-%Y')} a {fecha_fin.strftime('%d-%m-%Y')}", showlegend=False, height=400)
        st.plotly_chart(fig_anulados, use_container_width=True, config={"staticPlot": True,"displayModeBar": False}, key='grafico_anulados_vendedor')

    with right:
        st.subheader('💸 Descuentos por Vendedor')
        df_descuentos = df_filtrado[df_filtrado['DESCUENTO GLOBAL CON IGV'] > 0]
        if df_descuentos.empty:
            st.info('No hay descuentos en el período seleccionado')
            return
        df_items = df_descuentos.groupby('VENDEDOR').agg({'CANTIDAD (ITEM)': 'sum', 'NÚMERO': 'nunique'}).reset_index()
        df_importe = df_descuentos.drop_duplicates(subset=['NÚMERO']).groupby('VENDEDOR').agg({'DESCUENTO GLOBAL CON IGV': 'sum'}).reset_index()
        df_descuentos = df_importe.merge(df_items, on='VENDEDOR', how='left')
        df_descuentos.rename(columns={
            'VENDEDOR': 'Vendedor',
            'DESCUENTO GLOBAL CON IGV': 'Total Descuentos',
            'CANTIDAD (ITEM)': 'N° Items',
            'NÚMERO': 'N° Transacciones',
        }, inplace=True)
        df_descuentos = df_descuentos.sort_values('Total Descuentos', ascending=False).reset_index(drop=True)
        fig_descuentos = px.pie(df_descuentos, values='Total Descuentos', names='Vendedor', template='plotly_white', hole=0.0)
        fig_descuentos.update_traces(
            textposition='outside',
            textinfo='label+percent',
            texttemplate='%{label}<br>%{percent:.1%}',
            marker=dict(line=dict(color='white', width=2)),
            customdata=df_descuentos[['Total Descuentos', 'N° Items', 'N° Transacciones']].to_numpy(),
            hovertemplate='<b>%{label}</b><br>' + '💸 Total Descuentos: S/ %{customdata[0][0]:,.2f}<br>' + '📦 N° Items: %{customdata[0][1]:,.0f}<br>' + '📄 N° Transacciones: %{customdata[0][2]:,.0f}<br>' + '<extra></extra>',
        )
        fig_descuentos.update_layout(title=f"🧭 Período: {fecha_inicio.strftime('%d-%m-%Y')} a {fecha_fin.strftime('%d-%m-%Y')}", showlegend=False, height=400)
        st.plotly_chart(fig_descuentos, use_container_width=True, config={"staticPlot": True,"displayModeBar": False}, key='grafico_descuentos_vendedor')
    st.write('')
    st.markdown('---')


def graph_productos():
    df_filtrado = apply_filters(df, tipo_documento, date1, date2)
    izquierda, derecha = st.columns(2)
    with izquierda:
        st.markdown('#### ⬆ Top 10 de Productos más Vendidos')
        with st.expander(f"🧭 Período: {fecha_inicio.strftime('%d-%m-%Y')} a {fecha_fin.strftime('%d-%m-%Y')}"):
            productos_mas = (
                df_filtrado.groupby('DESCRIPCIÓN (ITEM)')[['CANTIDAD (ITEM)']].sum().sort_values('CANTIDAD (ITEM)', ascending=False).head(10).reset_index()
            )
            productos_mas.columns = ['Descripción', 'Cantidad']
            productos_mas['Cantidad'] = productos_mas['Cantidad'].map('{:,.0f}'.format)
            styled_df = productos_mas.style.background_gradient(cmap='Greens', subset=['Cantidad']).set_table_styles([{'selector': 'th', 'props': [('background-color', '#1E3A8A'), ('color', 'white')]}])
            st.dataframe(styled_df, column_config={
                'Descripción': st.column_config.Column('Descripción', width='large'),
                'Cantidad': st.column_config.Column('Cant', width='small'),
            }, use_container_width=True, hide_index=True)

    with derecha:
        st.markdown('#### ⬇ Bottom 10 de Productos menos Vendidos')
        with st.expander(f"🧭 Período: {fecha_inicio.strftime('%d-%m-%Y')} a {fecha_fin.strftime('%d-%m-%Y')}"):
            productos_mas = (
                df_filtrado.groupby('DESCRIPCIÓN (ITEM)')[['CANTIDAD (ITEM)']].sum().sort_values('CANTIDAD (ITEM)', ascending=True).head(10).reset_index()
            )
            productos_mas.columns = ['Descripción', 'Cantidad']
            productos_mas['Cantidad'] = productos_mas['Cantidad'].map('{:,.0f}'.format)
            styled_df = productos_mas.style.background_gradient(cmap='Reds', subset=['Cantidad']).set_table_styles([{'selector': 'th', 'props': [('background-color', '#1E3A8A'), ('color', 'white')]}])
            st.dataframe(styled_df, column_config={
                'Descripción': st.column_config.Column('Descripción', width='large'),
                'Cantidad': st.column_config.Column('Cant', width='small'),
            }, use_container_width=True, hide_index=True)


def graph_time_dia_vendedores():
    df_filtrado_grafico = apply_filters(df, tipo_documento, date1, date2, eliminar_fechas=False)
    fecha_fin_grafico = date2
    fecha_inicio_grafico = (date2 - pd.Timedelta(days=12)).normalize()
    df_grafico = df_filtrado_grafico[(df_filtrado_grafico['FECHA'] >= fecha_inicio_grafico) & (df_filtrado_grafico['FECHA'] <= fecha_fin_grafico)].copy()
    if df_grafico.empty:
        st.warning('No hay datos para el período seleccionado')
        return

    df_importe_unico = df_grafico.drop_duplicates(subset=['NÚMERO']).copy()
    df_importe_unico['fecha_dia'] = df_importe_unico['FECHA'].dt.to_period('D')
    ventas_por_vendedor = df_importe_unico.groupby(['fecha_dia', 'VENDEDOR'])['IMPORTE TOTAL DEL COMPROBANTE'].sum().reset_index()
    dias_completos = pd.period_range(start=fecha_inicio_grafico.to_period('D'), end=fecha_fin_grafico.to_period('D'), freq='D')
    vendedores = ventas_por_vendedor['VENDEDOR'].unique()
    df_completo = pd.DataFrame()
    for vendedor in vendedores:
        df_vendedor = ventas_por_vendedor[ventas_por_vendedor['VENDEDOR'] == vendedor].copy()
        df_vendedor = df_vendedor.set_index('fecha_dia').reindex(dias_completos, fill_value=0).reset_index()
        df_vendedor.columns = ['fecha_dia', 'VENDEDOR', 'IMPORTE TOTAL DEL COMPROBANTE']
        df_vendedor['VENDEDOR'] = vendedor
        df_vendedor['etiqueta_x'] = df_vendedor['fecha_dia'].dt.strftime('%d/%m')
        df_completo = pd.concat([df_completo, df_vendedor], ignore_index=True)

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
            hovertemplate='Vendedor: %{customdata[2]}<br>' + 'Día: %{customdata[0]}<br>' + 'Ventas: S/ %{customdata[1]:,.2f}<br>' + '<extra></extra>',
        ))
    if len(vendedores) > 0:
        fig_time_dia_vendedores.update_xaxes(tickangle=0, tickmode='array', tickvals=df_completo[df_completo['VENDEDOR'] == vendedores[0]]['etiqueta_x'].unique(), ticktext=df_completo[df_completo['VENDEDOR'] == vendedores[0]]['etiqueta_x'].unique())
    fig_time_dia_vendedores.update_layout(
        title=f"⏳ Del {fecha_inicio_grafico.strftime('%d/%m')} al {fecha_fin_grafico.strftime('%d/%m')}",
        xaxis_title='Días',
        yaxis_title='Ventas (S/)',
        showlegend=True,
        template='gridon',
        legend=dict(yanchor='top', y=1.15, xanchor='right', x=0.98, orientation='h'),
        margin=dict(l=10, r=10, t=50, b=10),
        height=500,
    )
    st.plotly_chart(fig_time_dia_vendedores, use_container_width=True, config={"staticPlot": True,"displayModeBar": False})

    with st.expander('Ver Datos - Ventas por Día y Vendedor', expanded=False):
        tabla_pivote = df_completo.pivot_table(index='etiqueta_x', columns='VENDEDOR', values='IMPORTE TOTAL DEL COMPROBANTE', fill_value=0).reset_index()
        format_dict = {col: '{:,.2f}' for col in tabla_pivote.columns if col != 'etiqueta_x'}
        styled_df = tabla_pivote.style.format(format_dict)
        st.dataframe(styled_df, use_container_width=True)
        csv = tabla_pivote.to_csv(index=False).encode('utf-8')
        st.download_button('📥 Descargar Data', data=csv, file_name='ventas_por_dia_vendedor.csv', mime='text/csv', help='Click aquí para descargar los datos', use_container_width=True)
    st.markdown('---')


def metricas_vendedor():
    df_filtrado = apply_filters(df, tipo_documento, date1, date2)
    if df_filtrado.empty:
        st.warning('No hay datos para mostrar')
        return
    df_limpio = df_filtrado.copy()
    df_limpio['VENDEDOR_LIMPIO'] = df_limpio['VENDEDOR'].apply(limpiar_nombre_vendedor)
    ventas_por_vendedor = df_limpio.drop_duplicates(subset=['NÚMERO']).groupby('VENDEDOR_LIMPIO')['IMPORTE TOTAL DEL COMPROBANTE'].sum()
    transacciones_por_vendedor = df_limpio.groupby('VENDEDOR_LIMPIO')['NÚMERO'].nunique()
    items_por_vendedor = df_limpio.groupby('VENDEDOR_LIMPIO')['CANTIDAD (ITEM)'].sum()
    ticket_promedio = (ventas_por_vendedor / transacciones_por_vendedor).fillna(0)
    items_x_transaccion = (items_por_vendedor / transacciones_por_vendedor).fillna(0)

    colores_tarjetas = [
        {'bg': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 'color': '#667eea'},
        {'bg': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', 'color': '#f093fb'},
        {'bg': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', 'color': '#4facfe'},
        {'bg': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', 'color': '#43e97b'},
        {'bg': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', 'color': '#fa709a'},
    ]

    st.subheader('📊 Métricas por Vendedor')
    vendedores = ventas_por_vendedor.index.tolist()
    cols = st.columns(len(vendedores))
    total_ventas_general = ventas_por_vendedor.sum()

    for idx, (col, vendedor) in enumerate(zip(cols, vendedores)):
        ventas = ventas_por_vendedor[vendedor]
        transacciones = transacciones_por_vendedor[vendedor]
        items = items_por_vendedor[vendedor]
        ticket = ticket_promedio[vendedor]
        items_x_trans = items_x_transaccion[vendedor]
        porcentaje = (ventas / total_ventas_general * 100) if total_ventas_general > 0 else 0
        icono = '👑' if vendedor.lower() == 'admin' else '⭐' if vendedor.lower() == 'briyic' else '👤'
        with col:
            st.markdown(
                f"""
                <div style='background: {colores_tarjetas[idx % len(colores_tarjetas)]['bg']};
                            border-radius: 20px;
                            padding: 20px;
                            margin: 10px 5px;
                            box-shadow: 0 8px 16px rgba(0,0,0,0.1);'>
                    <h2 style='color: white; text-align: center; margin-bottom: 15px; font-size: 1.5rem;'>{icono} {vendedor}</h2>
                    <hr style='margin: 15px 0; border-color: rgba(255,255,255,0.3);'>
                    <p style='color: white; margin: 12px 0; font-size: 1rem;'><strong>💰 Total Ventas:</strong><br><span style='font-size: 1.3rem;'>S/ {ventas:,.2f}</span></p>
                    <p style='color: white; margin: 12px 0; font-size: 1rem;'><strong>🛒 Transacciones:</strong><br><span style='font-size: 1.3rem;'>{transacciones:,.0f}</span></p>
                    <p style='color: white; margin: 12px 0; font-size: 1rem;'><strong>📦 Items Vendidos:</strong><br><span style='font-size: 1.3rem;'>{items:,.0f}</span></p>
                    <p style='color: white; margin: 12px 0; font-size: 1rem;'><strong>📊 Ticket Promedio:</strong><br><span style='font-size: 1.3rem;'>S/ {ticket:,.2f}</span></p>
                    <p style='color: white; margin: 12px 0; font-size: 1rem;'><strong>📁 Items x Transacción:</strong><br><span style='font-size: 1.3rem;'>{items_x_trans:.1f}</span></p>
                    <div style='background: rgba(255,255,255,0.2); border-radius: 10px; padding: 10px; margin-top: 15px; text-align: center;'><span style='color: white; font-size: 0.9rem;'>📈 Participación: {porcentaje:.1f}% del total</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.write('')
    st.write('')
    st.markdown('---')


def sidebar():
    with st.sidebar:
        selected = option_menu(
            menu_title='Main Menú',
            options=['Ventas', 'Compras', 'Productos', 'Vendedores'],
            icons=['cart4', 'bag', 'p-circle', 'people-fill'],
            menu_icon='cast',
            default_index=0,
        )
    if selected == 'Ventas':
        st.subheader(f'🛒 Página: {selected}')
        st.markdown('---')
        metricas()
        graph_time_dia()
        graph_time_mes()
        df_filtrado = apply_filters(df, tipo_documento, date1, date2)
        if len(df_filtrado) > 0:
            st.write(f'**Total de registros filtrados:** {len(df_filtrado)}')
            graph_categoria()
            graph_vendedor()
            graph_tipo_pago()
            graph_anulados()
            graph_productos()
        else:
            st.error('No hay datos para los filtros seleccionados')
    elif selected == 'Compras':
        st.subheader(f'Página: {selected}')
        st.markdown('---')
        st.info('🚧 Página en construcción')
    elif selected == 'Productos':
        st.subheader(f'Página: {selected}')
        st.markdown('---')
        st.info('🚧 Página en construcción')
    elif selected == 'Vendedores':
        st.subheader(f'Página: {selected}')
        st.markdown('---')
        metricas_vendedor()
        graph_time_dia_vendedores()


if __name__ == '__main__':
    sidebar()
