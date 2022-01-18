import pandas as pd
import numpy as np


''' ### Cleaning Data  ### '''


''' First Dataset  '''
df_temp = pd.read_csv('Datasets\GlobalLandTemperaturesByCountry.csv')

#Transformo las variables dt de tipo texto a tipo datetime
df_temp['year'] = pd.to_datetime(df_temp['dt']) 

#Creo un filtro seleccionando todas las fechas siguientes a 1970
idx = df_temp['year'] > pd.to_datetime('1970-01-01')
df_temp = df_temp[idx]

#Agrupo por fecha y pais para encontrar un promedio de temperatura anual
df_temp_average = df_temp.groupby(['Country',
                pd.Grouper(key='year',freq='1Y')]
                ).agg({'AverageTemperature':[np.mean,np.median]})

#Ejemplo
def plotPais():
    '''Ejemplo de seleccion de temperatura promedio para un pais'''
    pais = input('Seleccione un pais:' )
    df_temp_average.xs(pais)['AverageTemperature'].plot()


#Nuevo dataset mas compacto con solo la mediana
df_temp_med = df_temp_average['AverageTemperature'][['median']].reset_index()
#Agrego una nueva columna 
df_temp_med['date'] = df_temp_med['year'].dt.year
#Renombro columnas
df_temp_med.rename(columns={'median':'temperature', 'year':'date','date':'year'}, inplace=True)

#Ejemplo BloxPlot:
def boxPlotPaises(num: int, num2: int):
    '''
    num: numero de paises como filas
    num2: numero de cabecera para ajustar pantalla
    '''
    df_t_pivot = df_temp_med.pivot_table(values='temperature', index='year', columns='Country')
    df_t_pivot.T.sample(num).head(num2).boxplot(rot=45)
    #print(df_t_pivot.T.sample(num).head(num2))



''' Second Dataset '''
df_agri = pd.read_csv('Datasets\API_AG.LND.AGRI.K2_DS2_en_csv_v2_3472200.csv', header=2)
df_fore = pd.read_csv('Datasets\API_AG.LND.FRST.K2_DS2_en_csv_v2_3470755.csv', header=2)
df_elec = pd.read_csv('Datasets\API_EG.USE.ELEC.KH.PC_DS2_en_csv_v2_3475310.csv', header=2)
df_co2 = pd.read_csv('Datasets\API_EN.ATM.CO2E.KT_DS2_en_csv_v2_3470002.csv', header=2)
df_pop = pd.read_csv('Datasets\API_SP.POP.TOTL_DS2_en_csv_v2_3469297.csv', header=2)

#Formateo los dataframes para unirlos con el primero

cols = ['Country Name', 'Country Code'] + list(map(str,range(1971,2015)))


def func_formato(df, col = 'agriculture'):
    '''
    Muevo los años a una columna, renombro columnas para que coincidan con el first dataset
    '''
    return df.loc[:,cols].melt(id_vars=['Country Name', 'Country Code']).rename(
        columns={'variable': 'year',
            'Country Name': 'Country',
            'Country Code': 'name',
            'value': col}
    )

df_agri = func_formato(df_agri, col = 'agriculture')
df_fore = func_formato(df_fore, col = 'forest')
df_elec = func_formato(df_elec, col = 'electricprod')
df_co2 = func_formato(df_co2, col = 'co2')
df_pop = func_formato(df_pop, col = 'population')

#Transformo year a tipo float
df_agri['year'] = df_agri['year'].astype('float')
df_fore['year'] = df_fore['year'].astype('float')
df_elec['year'] = df_elec['year'].astype('float')
df_co2['year'] = df_co2['year'].astype('float')
df_pop['year'] = df_pop['year'].astype('float')


''' Ahora todos los dataset tienen el mismo formato por lo que puedo convinarlos '''

df_merge = pd.merge(df_temp_med[['Country', 'temperature', 'year']], df_agri, on=['Country', 'year'], how='inner')
df_merge = pd.merge(df_merge, df_fore, on=['Country', 'name', 'year'], how='inner')
df_merge = pd.merge(df_merge, df_co2, on=['Country','name', 'year'], how='inner')
df_merge = pd.merge(df_merge, df_elec, on=['Country','name', 'year'], how='inner')
df_merge = pd.merge(df_merge, df_pop, on=['Country','name', 'year'], how='inner')



if __name__ == '__main__':
    """"""
    #print(df_temp)
    #plotPais()
    #boxPlotPaises(2,4)
    #print(df_merge)
    print(df_merge.dropna())
