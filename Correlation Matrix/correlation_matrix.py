##### IMPORTS #####

#Imports for data manipulation
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sklearn

#Necessary for accessing APIs
import json
import requests

##### VARIABLE DECLARATIONS #####
JHU_df = pd.DataFrame();
COVID_df = pd.DataFrame(columns=['FIPS', 'County_Name', 'Combined_Key', 'Confirmed', 'Date', 'Deaths', 'State', 'Month_Case_Progression', '2016_E_Party', 'Governer_Party', 'Lat', 'Lng']);

##### DATA IMPORTS #####

# JHU COVID case data by county

def JHUDataFetch():

    global JHU_df
    global COVID_df
    #Create list of 15 most recent days in decending order
    base = datetime.datetime.today()
    date_list = [base - datetime.timedelta(days=x+1) for x in range(32)]

    #Iterates through date list and extracts a day, month, and year from each datetime object, then reads the corresponding csv file and attaches the information to the DataFrame
    for i in date_list:
        day = i.strftime('%d')
        month = i.strftime('%m')
        year = i.strftime('%Y')

        #Using string interpolation
        link=f'../JHU_CSVs/{month}-{day}-{year}.csv'

        try:
            #Reads csv files and appends to the main JHU_df
            data=pd.read_csv(link, error_bad_lines=False)
            #Adds a date column
            data['Date'] = datetime.datetime(int(year), int(month), int(day))
            JHU_df = JHU_df.append(data, sort=True)
            print(f'{month}-{day}-{year}.csv successfully loaded into JHU_df dataframe.')
        except Exception as e:
            print(f'WARNING: Exception when uploading JHU file: {link}. \nException: {e}')

    JHU_df = JHU_df.loc[JHU_df['Country_Region']=='US']
    grouped = JHU_df.groupby(['FIPS'])
    for i in JHU_df.FIPS.unique():
        try:
            d = grouped.get_group(i)
        except Exception as e:
            print(f'WARNING: Exception for location with FIPS code {i} in JHUDataFetch. \nException: {e}')

        dr = d[::-1]
        dr['Day_Cases'] = dr['Confirmed'].sub(dr['Confirmed'].shift())
        dr['Day_Cases'].iloc[0] = np.NaN
        
        d0 = d.iloc[0]
        new_row = {'FIPS': d0['FIPS'], 'County_Name': d0['Admin2'], 'Combined_Key': d0['Combined_Key'], 'Confirmed': d0['Confirmed'], 'Date': d0['Date'], 'Deaths': d0['Deaths'], 'State': d0['Province_State'], 'Month_Case_Progression': dr['Day_Cases'].values, 'Lat': d0['Lat'], 'Lng': d0['Long_']}
        COVID_df = COVID_df.append(new_row, ignore_index=True)
        
    COVID_df.to_csv('COVID_df.csv', encoding='utf-8')

# MIT 2016 county election data

def presElectionDataFetch():
    
    global COVID_df
    COVID_df = pd.read_csv('./COVID_df.csv')
    
    data = pd.read_csv('./countypres_2000-2016.csv')
    presData_2016 = data.loc[data['year']==2016]
    grouped = presData_2016.groupby(['FIPS'])

    for i in presData_2016.FIPS.unique():
        try:
            p = grouped.get_group(i)
            party = p.iloc[p.index==p['candidatevotes'].idxmax()]['party'].values[0]
        except Exception as e:
            print(f'WARNING: Exception for location with FIPS code {i} in presElectionDataFetch when identifying party. \nException: {e}')
        
        try:
            COVID_df.loc[COVID_df['FIPS']==i, ['2016_E_Party']] = party
            print(f'Party {party} successfully added for location with FIPS {i}')
        except Exception as e:
            print(f'WARNING: Exception for location with FIPS code {i} in presElectionDataFetch when pushing to COVID_df. \nException: {e}')

# Current governer political party

# Population density

# Income index

# Race index

# Age index

# Education index

# Geography of state

# Weather

##### DATA ACQUISITION CALLS #####

#JHUDataFetch();
presElectionDataFetch()