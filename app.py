import streamlit as st
import pandas as pd
import plotly.express as px


# Cargar datos
data_path = "data/data.csv"  # Cambia al nombre correcto de tu archivo
df = pd.read_csv(data_path)

# Convertir wash_date a formato de fecha
df['wash_date'] = pd.to_datetime(df['wash_date'])

# Configuración de la página
st.set_page_config(page_title="IFCO Dashboard", layout="wide")

# Mostrar el logo
logo_path = "images/ifco-logo.png"  # Cambia a la ruta donde se encuentra el logo
st.image(logo_path, width=150)

# Título principal
st.title("IFCO Dashboard")
st.markdown("Esta es una plantilla donde podemos insertar gráficos y visualizaciones respetando el diseño base.")

# Barra lateral con filtros
st.sidebar.title("Filters")

# Filtro por país con opción "Seleccionar todos"
all_countries = df["site_country"].unique()
countries = st.sidebar.multiselect(
    "Select Country",
    options=["Select All"] + list(all_countries),
    default=["Select All"],
    help="Choose one or more countries to filter the data."
)

# Lógica para "Seleccionar todos" en países
if "Select All" in countries:
    selected_countries = all_countries
else:
    selected_countries = countries

# Filtro por sitio con opción "Seleccionar todos"
all_sites = df[df["site_country"].isin(selected_countries)]["site_name"].unique()
sites = st.sidebar.multiselect(
    "Select Site",
    options=["Select All"] + list(all_sites),
    default=["Select All"],
    help="Choose one or more sites to filter the data."
)

# Lógica para "Seleccionar todos" en sitios
if "Select All" in sites:
    selected_sites = all_sites
else:
    selected_sites = sites

# Filtro por rango de fechas
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(df["wash_date"].min(), df["wash_date"].max()),
    help="Select the range of dates to filter."
)

# Aplicar filtros
filtered_df = df[
    (df["site_country"].isin(selected_countries)) &
    (df["site_name"].isin(selected_sites)) &
    (df["wash_date"].between(pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])))
]

# Calcular totales para Scanner y SAP
total_scanner_volume = filtered_df["scanner_wash_volume"].sum()
total_sap_volume = filtered_df["sap_wash_volume"].sum()

# Mostrar tarjetas con métricas
st.markdown("### Overview Metrics")
metrics_col1, metrics_col2, metrics_col3 = st.columns([1, 2, 1])

with metrics_col2:  # Centrar las métricas
    col1, col2 = st.columns(2)
    col1.metric(label="Scanner Wash Volume", value=f"{total_scanner_volume/1e6:.2f}M")
    col2.metric(label="SAP Wash Volume", value=f"{total_sap_volume/1e6:.2f}M")

# Agregar selector de granularidad
st.sidebar.markdown("### Granularity")
granularity = st.sidebar.radio(
    "Select Granularity",
    options=["Daily", "Monthly", "Yearly", "Quarterly"],
    help="Choose the granularity for the data."
)

# Agregar columna de granularidad
if granularity == "Monthly":
    filtered_df["granularity"] = filtered_df["wash_date"].dt.to_period("M").dt.start_time
elif granularity == "Yearly":
    filtered_df["granularity"] = filtered_df["wash_date"].dt.to_period("Y").dt.start_time
elif granularity == "Quarterly":
    filtered_df["granularity"] = filtered_df["wash_date"].dt.to_period("Q").dt.start_time
else:
    filtered_df["granularity"] = filtered_df["wash_date"]

# Calcular totales por granularidad
summary_df = filtered_df.groupby("granularity").agg({
    "scanner_wash_volume": "sum",
    "sap_wash_volume": "sum"
}).reset_index()

# Gráfico principal
st.subheader("Section 1")
st.markdown(f"### Comparison of Wash Volume: Scanner vs SAP ({granularity})")

# Crear gráfico con Plotly
fig = px.bar(
    summary_df,
    x="granularity",
    y=["scanner_wash_volume", "sap_wash_volume"],
    barmode="group",
    labels={"granularity": "Date", "value": "Volume", "variable": "Source"},
    title=f"Comparison of Wash Volume: Scanner vs SAP ({granularity})"
)

# Mostrar valores en las barras
fig.update_traces(texttemplate="%{y:.2s}", textposition="outside")
fig.update_layout(uniformtext_minsize=8, uniformtext_mode="hide")

# Mostrar el gráfico
st.plotly_chart(fig, use_container_width=True)