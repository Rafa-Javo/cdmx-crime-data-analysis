import os
import streamlit as st
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go
#import plotly.io as pio
#pio.templates.default = "plotly_dark"

#import seaborn as sns
#sns.set_style("darkgrid")

import matplotlib.pyplot as plt
from streamlit_folium import folium_static
import folium
from folium.plugins import HeatMap#, HeatMapWithTime
#import pydeck as pdk

month_days = {'Enero':31,
              'Febrero':28,'Marzo':31, 
              'Abril':30, 'Mayo':31,
              'Junio':30,'Julio':30,
              'Agosto':31,'Septiembre':30,
              'Octubre':31,'Noviembre':30,'Diciembre':30}

month_to_num = {key: i+1 for i,key in enumerate(month_days)}
num_to_month = {(i+1): key for i,key in enumerate(month_days)}

#! leemos los datos
DATA_URL = os.path.join(os.path.dirname(__file__), 'purged_carpetas_de_inv_fgj_cdmx_junio_2021.csv')
#DATA_URL = ("purged_carpetas_de_inv_pgj_cdmx.csv")
# DATA_URL = ("data/Delitos Alto Impacto municipio Morelia 2018-2019-2020.xlsx")


st.title("Carpetas de Investigación CDMX - datos de la FGJ")


@st.cache(persist=False)
def load_data():
    data = pd.read_csv(DATA_URL,na_values='NaN')
    data.fecha_hechos = pd.to_datetime(data.fecha_hechos)
    data.rename(columns={'longitud':'lon','latitud':'lat'}, inplace=True)
    return data

data = load_data()




# ------------------------------------------------------------------------------------------------------ #
# FILTRANDO DATOS
#data = data[data['fecha_hechos'].notna()]
data = data.dropna()
st.sidebar.markdown('# Filtros')
st.sidebar.markdown('## Delitos')
choice = st.sidebar.multiselect('Escoge delito(s)', (sorted(list(data.delito.unique()))), default = ['ROBO A REPARTIDOR CON VIOLENCIA','ROBO A REPARTIDOR SIN VIOLENCIA','ROBO A REPARTIDOR Y VEHICULO CON VIOLENCIA','ROBO A REPARTIDOR Y VEHICULO SIN VIOLENCIA'], key='54')

st.sidebar.markdown("## Horario/Meses/Años")
if not st.sidebar.checkbox("Todo el día", True,key='2'):
    #start = st.sidebar.number_input('Hora inicio', min_value=0, max_value=23, value=5, step=1)
    #end = st.sidebar.number_input('Hora fin', min_value=0, max_value=23, value=8, step=1)
    #hour = st.sidebar.slider('Hora del día', 0,23)
    #if start < end:
    #    hour = list(range(start,end))
    #    st.sidebar.markdown('Horas: ['+str(start)+','+str(end)+')')
    #else:
    #    hour = list(range(start,24)) + list(range(0,end))
    #    st.sidebar.markdown('Horas: ['+str(start)+','+'24'+')'+' U '+'[0,'+str(end)+')')
    
    #hour = [hour]
    hour = st.sidebar.multiselect('Horas:', list(range(24)), default=[5,6,7,8])
    
else:
    hour = list(range(24))

meses = st.sidebar.multiselect('Meses', 
('Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'), default=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'])

list(data.fecha_hechos.dt.year.unique())
anios = st.sidebar.multiselect('Años', (list(range(2016,2022))), default = list(range(2016,2021)))

subdata = data

# Filtrando por delito
if len(choice) > 0:
    subdata = subdata[subdata.delito.isin(choice)]

# Filtrando por rango de horas
subdata = subdata[subdata['fecha_hechos'].dt.hour.isin(hour)]

# Filtrando por meses
nums = []
for mes in meses:
    nums.append(month_to_num[mes])
subdata = subdata[subdata['fecha_hechos'].dt.month.isin(nums)]

# Filtrando por anio
subdata = subdata[subdata['fecha_hechos'].dt.year.isin(anios)]

# Especificando la cantidad de carpetas en la visualización
st.markdown('## {} carpetas registradas*.'.format(subdata.shape[0]))

# ------------------------------------------------------------------------------------------------------ #


# HISTOGRAMA: (DELITOS x CATEGORÍA)
crimenes_por_tipo = subdata['delito'].value_counts()
crimenes_por_tipo = pd.DataFrame({'Tipo':crimenes_por_tipo.index, 'Carpetas':crimenes_por_tipo.values})
st.markdown('### Carpetas por tipo de delito')
fig = px.bar(crimenes_por_tipo, x='Tipo', y='Carpetas', height=500) #, color='Crímenes'
st.plotly_chart(fig)

# SERIE DE TIEMPO: (DELITOS x UNIDAD DE TIEMPO)
#   Poder agregar varios plots en los mismos ejes para comparar 2 o más años,meses, semanas, etc.
#   - Por ventana de tiempo específica - poder comparar con otra ventana de tiempo del *mismo tamaño
#   - Por año, por mes, por semana, por dia, por hora - '' del mismo tamaño

# ------------------------------------------------------------------------------------------------------ #
# MAPA (3 mapas)
# Mapa con pydeck
#coor = subdata[['lat','lon']]
#st.pydeck_chart(
#    pdk.Deck(
#        map_style='mapbox://styles/mapbox/streets-v11',
#        initial_view_state = pdk.ViewState(
#            latitude = 19.425821,
#            longitude= -99.1897989,
#            zoom=10,
#            pitch=50,
#        ),
#        layers=[
#           pdk.Layer(
#                'ScatterplotLayer',
#                data = coor,
#                get_position='[lon,lat]',
#                get_fill_color='[200,20,0,400]',
#                get_radius= 25,
#            ),
#        ]
#    )
#)

#st.write(subdata)    # DA ERROR ESTA LÍNEA NO SÉ PORQUÉ


#Mapas con folium (coloreado y hotspots)
#print(subdata)
#if st.checkbox("Mapa coloreado por tipo de crímen", False,key='asd2'):
#    morelia = (19.70078, -101.18443)
#    m = folium.Map(location = morelia, tiles = 'openstreetmap', zoom_start = 13) 
#    for data in zip(subdata.lat, subdata.lon, subdata.fecha_hechos, subdata.delito):
#        # print(data[0], data[1])
#        p = data[2]
#        c = 'black'
#        if data[3] == 'Feminicidio':
#            c = 'purple'
#        elif data[3] == 'Homicidio doloso':
#            c = 'red'
#        elif data[3] == 'Robo a casa habitación':
#            c = 'blue'
#        elif data[3] == 'Robo a comercios':
#            c = 'green'
#        elif data[3] == 'Robo a transeúnte':
#            c = 'yellow'
#        elif data[3] == 'Robo de vehículo':
#            c = 'grey'
#        elif data[3] == 'Extorsión':
#            c = 'orange'
#        folium.CircleMarker(location=[data[0], data[1]], radius=2,popup = p, color = c).add_to(m)
#    folium_static(m)

# Mapa 2 (heatmap)
#if st.checkbox("Mapa de calor", False,key='aasdfsd2'):
st.markdown('### Mapa de calor')
def mapa_calor(subdata):
    heat=subdata[['lat','lon']]
    heat.lat.fillna(0,inplace=True)
    heat.lon.fillna(0,inplace=True)
    m6=folium.Map(location=[19.425821, -99.1897989],tiles='Stamen Toner',zoom_start=10)
    HeatMap(data=heat,radius=9.5).add_to(m6)
    folium_static(m6)

if subdata.shape[0] > 200000:
    if st.checkbox("Mostrar mapa", False):
        mapa_calor(subdata)
else:
    mapa_calor(subdata)



# Mapa choropleth ..


# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# COMPARATIVA ANUAL
st.markdown('### Comparativa anual')
intmeses = [month_to_num[i] for i in meses]
for m in range(1,13):
    if m not in intmeses:
        st.markdown('### ¡Agrega todos los meses!')
        break
gra = pd.DataFrame()
gra['meses'] = [num_to_month[i][:3] for i in range(1,13)]
gra.set_index('meses',inplace=True)

for año in anios:
    time_series = subdata[['fecha_hechos']]#subdata.drop(columns=['lat','lon','Fiscalia','Municipio','Colonia','CalleNumero','Lugar','Arma','Violencia','FechaInicio'])
    #st.write(time_series)          # DA ERROR ESTA LÍNEA NO SÉ PORQUÉ
    time_series = time_series[time_series.fecha_hechos.dt.year == int(año)]
    time_series['meses'] = time_series.fecha_hechos.dt.month
    cri_mes = []
    mes_es = []
    for i in range(1,13):
        cri_mes.append(len(time_series[time_series.meses == i]))
        mes_es.append(num_to_month[i][:3])

    gra[año] = cri_mes

#st.set_option('deprecation.showPyplotGlobalUse', False)
#ax = sns.lineplot(data=gra)
#ax.set(ylabel = "Crímenes")
#st.write(gra)
#st.pyplot()
# ------------------------------------------------------------------------------------------------------ #
# COMPARATIVA ANUAL 2
fig = px.line(gra,labels={
                     "value": "carpetas",
                     "variable": "año",
                     "meses": "mes"
                 })

st.plotly_chart(fig)
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #


#Crimenes por violencia
#st.markdown('## Comparativa de crímenes con violencia')

# print(subdata)
#st.set_option('deprecation.showPyplotGlobalUse', False)
#if len(choice) >= 4 or len(choice) == 0:
#    fig, axs = plt.subplots(figsize=(15,7.5))
#ax = sns.countplot(x = 'delito', hue = 'Violencia', data=subdata)
#ax.set(ylabel = "Crímenes")
#ax.set(xlabel = "Dellito")

#st.pyplot()

# SERIE DE TIEMPO: (DELITOS x UNIDAD DE TIEMPO)
#   ** Hay que discretizar los valores por un rango de tiempo
#   Poder agregar varios plots en los mismos ejes para comparar 2 o más años,meses, semanas, etc.
#   - Por ventana de tiempo específica - poder comparar con otra ventana de tiempo del *mismo tamaño
#   - Por año, por mes, por semana, por dia, por hora - '' del mismo tamaño

# Ejemplo 1: Mostrar línea de tiempo de un año discretizado por meses
#   1. Sumar filas por cada mes y ponerle a esa fila una nueva columna que diga el número de crímenes o guardarlo en una lista
#   2. Graficar
#   ** Voy a usar los datos sólo de 1 año:



###                 PARTE NUEVA                     ###


# DISTRIBUCIÓN DE CRÍMENES POR HORA
#st.sidebar.markdown("### Usando parámetros especificados:")
#st.sidebar.markdown("### Distribución por hora")
#if st.sidebar.checkbox("Mostrar", False, key='dcph'):
st.markdown("### Distribución por hora")
horas = [i for i in range(0,24)]
distribucion = []
for i,h in enumerate(horas):
    subd = subdata[subdata['fecha_hechos'].dt.hour == h]
    distribucion.append( subd.shape[0])
df = pd.DataFrame(
                    {'hora': horas,
                    'carpetas': distribucion
                    })
fig = px.bar(df, x='hora', y='carpetas', height=500) #, color='Crímenes'
st.plotly_chart(fig)


# DISTRIBUCIÓN DE CRÍMENES POR DIA DE LA SEMANA
#st.sidebar.markdown("### Distribución por día de la semana")
#if st.sidebar.checkbox("Mostrar", False, key='dcpds'):
st.markdown("### Distribución por día de la semana")
dia_semana = [i for i in range(0,7)]
dia_str = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']
distribucion = []
for i,d in enumerate(dia_semana):
    subd = subdata[subdata['fecha_hechos'].dt.dayofweek == d]
    distribucion.append( subd.shape[0])
df = pd.DataFrame(
                    {'dia': dia_str,
                    'carpetas': distribucion
                    })
fig = px.bar(df, x='dia', y='carpetas', height=500) #, color='Crímenes'
st.plotly_chart(fig)


# DISTRIBUCIÓN DE CRÍMENES POR MES
#st.sidebar.markdown("### Distribución por mes")
#if st.sidebar.checkbox("Mostrar", False, key='dpm'):
st.markdown("### Distribución por mes")
mes = [i for i in range(1,13)]
mes_str = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
distribucion = []
for i,m in enumerate(mes):
    subd = subdata[subdata['fecha_hechos'].dt.month == m]
    distribucion.append( subd.shape[0])
df = pd.DataFrame(
                    {'mes': mes_str,
                    'carpetas': distribucion
                    })
fig = px.bar(df, x='mes', y='carpetas', height=500) #, color='Crímenes'
st.plotly_chart(fig)

## Stacked histogram ..
#fig = go.Figure()
#for delito in subdata.delito.unique():
#    fig.add_trace(go.Histogram(x=subdata[subdata.delito==delito].fecha_hechos.dt.month, name=delito[:50]))
## The two histograms are drawn on top of another
#fig.update_layout(barmode='stack')
#fig.update_yaxes(visible=False, showticklabels=True)
##fig.show()
#st.plotly_chart(fig)

# ------------------------------------------------------------------------------------------------------ #
# INFORMACIÓN

st.markdown("### Información")
st.markdown("- *Registros con valores válidos en los campos utilizados para las visualizaciones. \n- Los datos son de libre acceso y fueron obtenidos el 29 de julio de 2021 en [este link](https://datos.cdmx.gob.mx/dataset/carpetas-de-investigacion-fgj-de-la-ciudad-de-mexico). Solo abarcan hasta junio de 2021.    \n- El código de este proyecto está aquí: https://github.com/Rafa-Javo/cdmx-crime-data-analysis.     \n- Es importante señalar que los delitos denunciados/registrados representan solo una porción de los crímenes totales cometidos. En la [ENVIPE 2020](https://www.inegi.org.mx/contenidos/programas/envipe/2020/doc/envipe2020_mex.pdf) se estima que a nivel nacional, en 2019, se denunciaron 11% de los delitos. Y en 69.1% de los casos se inició una carpeta de investigación.    \n- La fecha utilizada en las visualizaciones es la fecha de los hechos, no la fecha del inicio de la carpeta de investigación. ")