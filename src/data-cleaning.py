#!/usr/bin/env python
# coding: utf-8
import pandas as pd
import numpy as np
import random
import argparse
import os

class DataProcessor:
    def __init__(self, data_path):
        self.data_path = data_path

    # ## Consolidating Demand Data
    def consolidate_demand(self):
        df_2017 = pd.read_csv(self.data_path+'/demanddata_2017.csv')
        df_2018 = pd.read_csv(self.data_path+'/demanddata_2018.csv')
        df_2019 = pd.read_csv(self.data_path+'/demanddata_2019.csv')
        df_2020 = pd.read_csv(self.data_path+'/demanddata_2020.csv')
        df_2021 = pd.read_csv(self.data_path+'/demanddata_2021.csv')
        df_2022 = pd.read_csv(self.data_path+'/demanddata_2022.csv')

        ## df_2022 has different date format compared to other Dfs hence changing its format.
        # Convert SETTLEMENT_DATE column in df_2022 to datetime
        df_2022['SETTLEMENT_DATE'] = pd.to_datetime(df_2022['SETTLEMENT_DATE'], format='%Y-%m-%d', errors='coerce')
        # Convert SETTLEMENT_DATE format to '01-JAN-2022'
        df_2022['SETTLEMENT_DATE'] = df_2022['SETTLEMENT_DATE'].dt.strftime('%d-%b-%Y').str.upper()

        # ### Combining all 6 years of data into 1 dataframe
        demand_df = pd.concat([df_2017, df_2018, df_2019, df_2020, df_2021, df_2022])

        demand_df['SETTLEMENT_DATE'] = pd.to_datetime(demand_df['SETTLEMENT_DATE'], format='%d-%b-%Y', errors='coerce').combine_first(pd.to_datetime(demand_df['SETTLEMENT_DATE'], format='%d-%b-%Y', errors='coerce'))
        # Resampling the demand data to 6 hour intervals since temperature data is avg of 6 hour temperatures.
        demand_df['timestamp'] = demand_df['SETTLEMENT_DATE'] + pd.to_timedelta((demand_df['SETTLEMENT_PERIOD'] - 1) * 30, unit='m')
        demand_df.set_index('timestamp', inplace=True)
        demand_6h = demand_df.resample('6H').mean()

        # #### Putting back SETTLEMENT_DATE
        demand_6h['SETTLEMENT_DATE'] = demand_6h.index.strftime('%d-%b-%Y')
        demand_6h = demand_6h.reset_index(drop=False)

        # ##### 2017 to 2019 and 2021 to 2022 = 365*5 + 366 for 2020 --> 2191 
        # ##### 4 data points each day for 6 hour intervals so 2191*4 --> 8764
        # ## Saving Cosolidated demand data as CSV
        demand_6h.to_csv(self.data_path+'/demanddata_2017-2022_6H.csv',index=False, float_format='%.2f')
        return demand_6h

    # ## Creating Temp Data
    def creating_temperature_data(self):
        df_temps = pd.read_csv(self.data_path+'/UK_Temperatures.csv')
        df_temps['observation_dtg_utc'] = pd.to_datetime(df_temps['observation_dtg_utc'])
        #Getting data for 2017-2022
        df_temps = df_temps[df_temps['observation_dtg_utc'] < '2023-01-01 00:00:00']

        df_temps.to_csv(self.data_path+'/temperaturedata-2017-2022-6H.csv',index=False, float_format='%.2f')
        return df_temps

    # ## Combining both data sets
    def combining_demand_temperature(self,demand_6h, df_temps):
        merged_df = pd.merge(demand_6h, df_temps, how = 'left',left_on='timestamp', right_on='observation_dtg_utc')
        #Interpolating missing data
        merged_df['temp_c'].interpolate(method = 'nearest',inplace=True)
        # ## Creating clean data frame containing TSD and temps only
        final_clean_df = merged_df[['SETTLEMENT_DATE', 'timestamp','temp_c','TSD' ]].copy()
        final_clean_df= final_clean_df.rename(columns={'timestamp':'observation_dtg_utc'})

        # ## Saving Cleaned dataframe with only demand, temp and date information as CSV
        final_clean_df.to_csv(self.data_path+'/cleaned-temp-dmnd-2017-2022.csv', index =False, float_format='%.2f')


# Create an ArgumentParser object
parser = argparse.ArgumentParser(description='Data Processing')

# Add an argument for the data path
parser.add_argument('--data_path', type=str, default='../data', help='Path to the data files')

if __name__ == '__main__':
    # Parse the command-line arguments
    args = parser.parse_args()

    # Access the data path from the parsed arguments
    data_path = args.data_path
    
    # Create an instance of the DataProcessor class
    data_processor = DataProcessor(data_path)
    
    # Call the consolidate_demand function
    demand_6h = data_processor.consolidate_demand()

    # Call the creating_temperature_data function
    df_temps = data_processor.creating_temperature_data()

    # Call the combining_demand_temperature function
    data_processor.combining_demand_temperature(demand_6h, df_temps)


