import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def clean_data() -> pd.DataFrame:
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
    

    #Nuevo dataset mas compacto con solo la mediana
    df_temp_med = df_temp_average['AverageTemperature'][['median']].reset_index()
    #Agrego una nueva columna 
    df_temp_med['date'] = df_temp_med['year'].dt.year
    #Renombro columnas
    df_temp_med.rename(columns={'median':'temperature', 'year':'date','date':'year'}, inplace=True)


    ''' Second Dataset '''
    df_agri = pd.read_csv('Datasets\API_AG.LND.AGRI.K2_DS2_en_csv_v2_3472200.csv', header=2)
    df_fore = pd.read_csv('Datasets\API_AG.LND.FRST.K2_DS2_en_csv_v2_3470755.csv', header=2)
    df_elec = pd.read_csv('Datasets\API_EG.USE.ELEC.KH.PC_DS2_en_csv_v2_3475310.csv', header=2)
    df_co2 = pd.read_csv('Datasets\API_EN.ATM.CO2E.KT_DS2_en_csv_v2_3470002.csv', header=2)
    df_pop = pd.read_csv('Datasets\API_SP.POP.TOTL_DS2_en_csv_v2_3469297.csv', header=2)

    #Formateo los dataframes para unirlos con el primero

    cols = ['Country Name', 'Country Code'] + list(map(str,range(1971,2015)))


    def func_formato(df, col=str) -> pd.DataFrame:
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
    
    return (df_merge)

def analisis_datos(df):
    '''Rutina de analisis de datos'''
    #Creo un sub dataframe para hacer una grafica de
    # La media de co2 en 10 paises 
    first_10 = df.groupby('Country')['co2'].median().sort_values(ascending=False).head(10).index
    df_max_co2 = df[df['Country'].isin(first_10)]
    #df_max_co2.set_index('Country').plot.scatter(x='population',y='co2',c='year',colormap='viridis')

    #Correlacion entre variables del dataframe
    #sns.heatmap(df.corr(), annot=True)
    #plt.show()

    #Analizo datos como uno solo y no por paises
    df_year = df.groupby('year').median()
    #sns.heatmap(df_year.corr(), annot=True)
    #plt.show()

    #Grafico analizando las variables vs ellas mismas (distribucion de probabilidad no parametrica)
    #pd.plotting.scatter_matrix(df,diagonal='kde',figsize=(7,7))
    #plt.show()

    #Grafico de coordenadas paralelas
    df_sudamerica = df[
                        df['Country'].isin(['Colombia', 'Argentina', 
                        'Bolivia', 'Mexico', 
                        'Peru', 'Chile'])
                        ][['Country', 'temperature',
                        'co2','agriculture', 'forest']]
                    

    pd.plotting.parallel_coordinates(df_sudamerica,'Country', colormap='viridis')
    plt.show()
    


if __name__ == '__main__':
    """"""
    df = clean_data()
    analisis_datos(df.dropna())
    
