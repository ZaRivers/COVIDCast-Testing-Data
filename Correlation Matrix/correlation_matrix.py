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

from state_abbreviations import us_state_abbrev

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
        

# MIT 2016 county election data

def presElectionDataFetch():
    
    global COVID_df
    #COVID_df = pd.read_csv('./COVID_df.csv')
    
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

def govPoliticalPartyFetch():
    
    global COVID_df
    #COVID_df = pd.read_csv('./COVID_df.csv')
    party_df = pd.read_csv('./party_df.csv')
    party_data = party_df.set_index('State')['Party'].to_dict()
    
    COVID_df['Governer_Party'] = COVID_df['State'].map(party_data)

# Population density

# Income index

# Education index

# Geography of state

# Weather

# Trump PCT

##### DATA EXTRACTION #####

def dataExtraction(fips):
    global COVID_df
    #COVID_df = pd.read_csv('./COVID_df.csv')
    return_df = pd.DataFrame()
    for i in fips:
        return_df = return_df.append(COVID_df.loc[COVID_df['FIPS']==i])
    return return_df

##### CSV Formatting #####

def CSVAbbreviationFormat():
    #COVID_df = pd.read_csv('./COVID_df.csv')
    COVID_df['State_Abrev'] = COVID_df['State'].map(us_state_abbrev)
    COVID_df['Full_County'] = ""

    for i in COVID_df.index:
        if type(COVID_df.iloc[i].County_Name) == str:
            lower_county = COVID_df.iloc[i].County_Name.lower()
            postal_lower = COVID_df.iloc[i]['State_Abrev'].lower()
            lower_county = lower_county.split(' ')
            lower_county.append('county')
            lower_county.append(postal_lower)
            cong_county = '-'.join(lower_county)
            COVID_df.at[i, 'Full_County'] = cong_county
        else:
            print('The following county name threw an error: ' + str(COVID_df.iloc[i].County_Name))

    counties_series = COVID_df['Full_County']
    counties_series.to_csv('counties_series.csv')
        

##### DATA ACQUISITION CALLS #####

JHUDataFetch()
presElectionDataFetch()
govPoliticalPartyFetch()

COVID_df.to_csv('COVID_df.csv', encoding='utf-8')

CSVAbbreviationFormat() 

sample_fips = pd.read_csv('../sample_fips.csv')
sample_fips = sample_fips.FIPS.values

sample_data = dataExtraction(sample_fips)
sample_data.sort_values('State')

sample_data.to_csv('sample_counties_COVID_data.csv')