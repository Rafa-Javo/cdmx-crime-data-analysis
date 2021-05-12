import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_folium import folium_static
import folium
from folium.plugins import HeatMap#, HeatMapWithTime
import pydeck as pdk

month_days = {'Enero':31,
              'Febrero':28,'Marzo':31, 
              'Abril':30, 'Mayo':31,
              'Junio':30,'Julio':30,
              'Agosto':31,'Septiembre':30,
              'Octubre':31,'Noviembre':30,'Diciembre':30}

month_to_num = {key: i+1 for i,key in enumerate(month_days)}
num_to_month = {(i+1): key for i,key in enumerate(month_days)}

#! leemos los datos
DATA_URL = ("delitos.xlsx")
# DATA_URL = ("data/Delitos Alto Impacto municipio Morelia 2018-2019-2020.xlsx")


st.title("Delitos Alto Impacto municipio Morelia 2018-2019-2020")


@st.cache(persist=False)
def load_data():
    data = pd.read_excel(DATA_URL,na_values='NaN')
    data.FechaComision = pd.to_datetime(data.FechaComision)
    data.rename(columns={'Longitud':'lon','Latitud':'lat','Delito':'delito'}, inplace=True)
    return data

data = load_data()


crimenes_por_tipo = data['delito'].value_counts()
#crimenes_por_delegacion = crimenes_por_delegacion.loc[delegaciones]
#st.write(crimenes_por_delegacion)
crimenes_por_tipo = pd.DataFrame({'Tipo':crimenes_por_tipo.index, 'Crímenes':crimenes_por_tipo.values})

# ------------------------------------------------------------------------------------------------------ #

# HISTOGRAMA: (DELITOS x CATEGORÍA)
st.sidebar.markdown('## Crímenes por tipo')
if  not st.sidebar.checkbox("Ocultar", False,key='2sd'):
    st.markdown('## Crímenes por tipo')
    fig = px.bar(crimenes_por_tipo, x='Tipo', y='Crímenes', height=500) #, color='Crímenes'
    st.plotly_chart(fig)

# SERIE DE TIEMPO: (DELITOS x UNIDAD DE TIEMPO)
#   Poder agregar varios plots en los mismos ejes para comparar 2 o más años,meses, semanas, etc.
#   - Por ventana de tiempo específica - poder comparar con otra ventana de tiempo del *mismo tamaño
#   - Por año, por mes, por semana, por dia, por hora - '' del mismo tamaño

# ------------------------------------------------------------------------------------------------------ #

# MAPA (3 mapas)
st.sidebar.markdown('## Mapas')
choice = st.sidebar.multiselect('Escoge delito(s)', (sorted(list(data.delito.unique()))), key='54')

st.sidebar.markdown("### Horario")
if not st.sidebar.checkbox("Todo el día", True,key='2'):
    hour = st.sidebar.slider('Hora del día', 0,23)
    hour = [hour]
    
else:
    hour = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]

meses = st.sidebar.multiselect('Meses', 
('Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'), default=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'])

anios = st.sidebar.multiselect('Años', ('2018','2019','2020'), default = ['2018','2019','2020'])

subdata = data

# Filtrando por delito
if len(choice) > 0:
    subdata = subdata[subdata.delito.isin(choice)]

# Filtrando por rango de horas
subdata = subdata[subdata['FechaComision'].dt.hour.isin(hour)]

# Filtrando por meses
nums = []
for mes in meses:
    nums.append(month_to_num[mes])
subdata = subdata[subdata['FechaComision'].dt.month.isin(nums)]

# Filtrando por anio
subdata = subdata[subdata['FechaComision'].dt.year.isin(anios)]

# Especificando la cantidad de delitos en la visualización
st.markdown('## {} delitos cometidos con los parámetros especificados.'.format(subdata.shape[0]))



# Mapa con pydeck
coor = subdata[['lat','lon']]
st.pydeck_chart(
    pdk.Deck(
        map_style='mapbox://styles/mapbox/streets-v11',
        initial_view_state = pdk.ViewState(
            latitude = 19.70202427849626,
            longitude=-101.19298171815072,
            zoom=12,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data = coor,
                get_position='[lon,lat]',
                get_fill_color='[200,20,0,400]',
                get_radius= 25,
            ),
        ]
    )
)

#st.write(subdata)    # DA ERROR ESTA LÍNEA NO SÉ PORQUÉ


#Mapas con folium (coloreado y hotspots)
#print(subdata)
if st.checkbox("Mapa coloreado por tipo de crímen", False,key='asd2'):
    morelia = (19.70078, -101.18443)
    m = folium.Map(location = morelia, tiles = 'openstreetmap', zoom_start = 13) 
    for data in zip(subdata.lat, subdata.lon, subdata.FechaComision, subdata.delito):
        # print(data[0], data[1])
        p = data[2]
        c = 'black'
        if data[3] == 'Feminicidio':
            c = 'purple'
        elif data[3] == 'Homicidio doloso':
            c = 'red'
        elif data[3] == 'Robo a casa habitación':
            c = 'blue'
        elif data[3] == 'Robo a comercios':
            c = 'green'
        elif data[3] == 'Robo a transeúnte':
            c = 'yellow'
        elif data[3] == 'Robo de vehículo':
            c = 'grey'
        elif data[3] == 'Extorsión':
            c = 'orange'
        folium.CircleMarker(location=[data[0], data[1]], radius=2,popup = p, color = c).add_to(m)
    folium_static(m)

# Mapa 2 (heatmap)
if st.checkbox("Mapa de calor", False,key='aasdfsd2'):
    heat=subdata[['lat','lon']]
    heat.lat.fillna(0,inplace=True)
    heat.lon.fillna(0,inplace=True)
    m6=folium.Map(location=[19.70078, -101.18443],tiles='Stamen Toner',zoom_start=13)
    HeatMap(data=heat,radius=9.5).add_to(m6)
    folium_static(m6)



# ------------------------------------------------------------------------------------------------------ #


# COMPARATIVA ANUAL
st.markdown('## Comparativa anual con los parámetros especificados')
intmeses = [month_to_num[i] for i in meses]
for m in range(1,13):
    if m not in intmeses:
        st.markdown('### ¡Agrega todos los meses!')
        break
gra = pd.DataFrame()
gra['meses'] = [num_to_month[i][:3] for i in range(1,13)]
gra.set_index('meses',inplace=True)
sns.set_style("darkgrid")
for año in anios:
    time_series = subdata.drop(columns=['lat','lon','Fiscalia','Municipio','Colonia','CalleNumero','Lugar','Arma','Violencia','FechaInicio'])
    #st.write(time_series)          # DA ERROR ESTA LÍNEA NO SÉ PORQUÉ
    time_series = time_series[time_series.FechaComision.dt.year == int(año)]
    time_series['meses'] = time_series.FechaComision.dt.month
    cri_mes = []
    mes_es = []
    for i in range(1,13):
        cri_mes.append(len(time_series[time_series.meses == i]))
        mes_es.append(num_to_month[i][:3])

    gra[año] = cri_mes

st.set_option('deprecation.showPyplotGlobalUse', False)
ax = sns.lineplot(data=gra)
ax.set(ylabel = "Crímenes")

st.pyplot()
# ------------------------------------------------------------------------------------------------------ #


#Crimenes por violencia
st.markdown('## Comparativa de crímenes con violencia')

# print(subdata)
st.set_option('deprecation.showPyplotGlobalUse', False)
if len(choice) >= 4 or len(choice) == 0:
    fig, axs = plt.subplots(figsize=(15,7.5))
ax = sns.countplot(x = 'delito', hue = 'Violencia', data=subdata)
ax.set(ylabel = "Crímenes")
ax.set(xlabel = "Dellito")

st.pyplot()

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
st.sidebar.markdown("### Distribución por hora")
if st.sidebar.checkbox("Mostrar", False, key='dcph'):
	st.markdown("### Distribución por hora")
	horas = [i for i in range(0,24)]
	distribucion = []
	for i,h in enumerate(horas):
		subd = subdata[subdata['FechaComision'].dt.hour == h]
		distribucion.append( subd.shape[0])
	df = pd.DataFrame(
						{'hora': horas,
						'delitos': distribucion
						})
	fig = px.bar(df, x='hora', y='delitos', height=500) #, color='Crímenes'
	st.plotly_chart(fig)


# DISTRIBUCIÓN DE CRÍMENES POR DIA DE LA SEMANA
st.sidebar.markdown("### Distribución por día de la semana")
if st.sidebar.checkbox("Mostrar", False, key='dcpds'):
	st.markdown("### Distribución por día de la semana")
	dia_semana = [i for i in range(0,7)]
	dia_str = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']
	distribucion = []
	for i,d in enumerate(dia_semana):
		subd = subdata[subdata['FechaComision'].dt.dayofweek == d]
		distribucion.append( subd.shape[0])
	df = pd.DataFrame(
						{'dia': dia_str,
						'delitos': distribucion
						})
	fig = px.bar(df, x='dia', y='delitos', height=500) #, color='Crímenes'
	st.plotly_chart(fig)


# DISTRIBUCIÓN DE CRÍMENES POR MES
st.sidebar.markdown("### Distribución por mes")
if st.sidebar.checkbox("Mostrar", False, key='dpm'):
	st.markdown("### Distribución por mes")
	mes = [i for i in range(1,13)]
	mes_str = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
	distribucion = []
	for i,m in enumerate(mes):
		subd = subdata[subdata['FechaComision'].dt.month == m]
		distribucion.append( subd.shape[0])
	df = pd.DataFrame(
						{'mes': mes_str,
						'delitos': distribucion
						})
	fig = px.bar(df, x='mes', y='delitos', height=500) #, color='Crímenes'
	st.plotly_chart(fig)
