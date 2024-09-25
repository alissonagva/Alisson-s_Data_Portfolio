import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib as plt
import os
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="EDA Alisson Superstore", page_icon=":bar_chart:", layout="wide")
st.title(":bar_chart: Sample Superstore EDA")

#st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

fl=st.file_uploader(":file_folder: Upload a file", type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename, encoding="ISO-8859-1")
else:
    os.chdir(r"C:\Users\graci\Desktop\Streamlit_test")
    df = pd.read_csv("Superstore.csv", encoding="ISO-8859-1")

col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])

#Get the min and max of the column
startDate= pd.to_datetime(df["Order Date"]).min()
endDate= pd.to_datetime(df["Order Date"]).max()

with col1:
    date1= pd.to_datetime(st.date_input("Fecha Inicio", startDate))
with col2:
    date2= pd.to_datetime(st.date_input("Fecha Final", endDate))

df=df[(df["Order Date"]>= date1) & (df["Order Date"]<= date2)].copy()

st.sidebar.header("Seleccione un filtro")
region = st.sidebar.multiselect("Escoga una región", df["Region"].unique())

#Create for region
if not region:
    df2 = df.copy()
else: 
    df2 = df[df["Region"].isin(region)]

#Create for state
state = st.sidebar.multiselect("Escoga un estado", df2["State"].unique())
if not state:
    df3 = df2.copy()
else: 
    df3 = df2[df2["State"].isin(state)]

#Create for city
city = st.sidebar.multiselect("Escoga una ciudad", df3["City"].unique())

#Filter the db based on region, state and city
if not region and not state and not city:
    filtered_df = df
elif not state and not city: 
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(state)]
elif region and state:
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:  
    filtered_df = df3[df3["City"].isin(city)]
else: 
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]


category_df = filtered_df.groupby(by= ["Category"], as_index = False)["Sales"].sum()

with col1:
    st.subheader("Ventas por categoría")
    fig = px.bar(category_df, x = "Category", y = "Sales", text = ['${:,.2f}'.format(x) for x in category_df["Sales"]], template="seaborn")
    st.plotly_chart(fig, use_container_width=True, height = 200)


with col2:
    st.subheader("Ventas por región")
    fig = px.pie(filtered_df, values = "Sales", names = "Region", hole=0.5)
    fig.update_traces(text= filtered_df["Region"], textposition = "outside")
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Datos por Categoría"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv=category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Descargar Datos", data=csv, file_name="Categoría.csv", mime="text/csv", help="Dar click para descargar los datos en un archivo csv")

with cl2:
    with st.expander("Datos por Región"):
        region = filtered_df.groupby(by= "Region", as_index = False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv=region.to_csv(index=False).encode('utf-8')
        st.download_button("Descargar Datos", data=csv, file_name="Región.csv", mime="text/csv", help="Dar click para descargar los datos en un archivo csv")

filtered_df["Mes_Año"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader("Análisis de Series de Tiempo") 

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["Mes_Año"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x="Mes_Año", y = "Sales", labels={"Sales": "Monto"}, height=500, width=1000, template="gridon")

st.plotly_chart(fig2, use_container_width=True)


with st.expander("Ver datos de la Serie de Tiempo:") :
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv=linechart.to_csv(index=False).encode('utf-8')
    st.download_button("Descargar datos", data=csv, file_name="Serie de Tiempo.csv", mime="text/csv")

#Crear un tree map basado por Región, Categoria, sub-categoria
st.subheader("Vista Jerárquica de las Ventas usando Diagramas en Árbol(TreeMap)")
fig3 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales", hover_data=["Sales"], color="Sub-Category")

fig3.update_layout(width = 800, height=650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader("Ventas por segmento")
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(text=filtered_df["Segment"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader("Ventas por categoría")
    fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    fig.update_traces(text=filtered_df["Category"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":point_right: Resumen de Ventas Mensuales por Sub-Categoría")
with st.expander("Tabla Resumen"):
    df_sample = df[0:5][["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
    fig = ff.create_table(df_sample, colorscale="Cividis")
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("Tabla Mensual por Sub-Categoría")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_year = pd.pivot_table(data=filtered_df, values= "Sales", index=["Sub-Category"], columns="month")
    st.write(sub_category_year.style.background_gradient(cmap="Blues"))

# Crear un Diagrama de dispersion entre Ventas e Ingresos

data1 = px.scatter(filtered_df, x = "Sales", y = "Profit", size="Quantity")
data1['layout'].update(title="Diagrama de Dispersión entre Ventas y Ganancias", titlefont= dict(size=20), 
                       xaxis = dict(title="Sales", titlefont=dict(size=19)), yaxis = dict(title="Profit", titlefont=dict(size=19)))

st.plotly_chart(data1, use_container_width=True)

with st.expander("Ver Datos"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Greys"))


#Descargar la base de datos original

csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Descargar los datos", data=csv, file_name="Datos.csv", mime="text/csv")