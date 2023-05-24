"""
Script for processing Bharti Airtel rate table
Author: Ameed Jamous
Company: Telecomsxchange.com
Copyright (c) 2023 Telecomsxchange.com
"""

import pandas as pd
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, filename='airtel_log.log')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)
logging.info('Starting Airtel rate conversion script.')

# Determine the file type and read the file accordingly
file_name = 'Airtel.xlsx'
logging.info(f'Reading file: {file_name}')
if file_name.endswith('.csv'):
    df = pd.read_csv(file_name, skiprows=14)
elif file_name.endswith('.xlsx'):
    df = pd.read_excel(file_name, skiprows=14)

# Step 2: Rename the 'Complete Code' column to 'Prefix'
logging.info('Renaming and adjusting columns.')
df = df.rename(columns={'Complete Code': 'Prefix'})

# Step 3: Duplicate 'Rates (USD / Min)' column to 'Price 1' and 'Price N'
df['Price 1'] = df['Rates (USD / Min)']
df['Price N'] = df['Rates (USD / Min)']

# Step 4: Convert the 'Valid From' column to 'Effective from' in the desired format
df['Valid From'] = pd.to_datetime(df['Valid From'], format='%d/%m/%Y')
df['Effective from'] = df['Valid From'].apply(lambda x: 'ASAP' if x.date() < datetime.now().date() else x.strftime('%Y-%m-%d %H:%M:%S'))

# Step 5: Split 'Pulse' into 'Interval 1' and 'Interval N'
pulse_df = df['Pulse'].str.split('/', expand=True)
df['Interval 1'] = pulse_df[0]
df['Interval N'] = pulse_df[1]

# Step 6: Add new columns and set their default values
df['Country'] = ''
df['Description'] = ''
df['Rate Id'] = ''
df['Forbidden'] = 0
df['Discontinued'] = 0

# Step 7: Remove unnecessary columns
df = df.drop(columns=['Destination', 'Valid From', 'Pulse', 'Rates (USD / Min)', 'Rate Change.1', 'Area Code Change'])

# Step 8: Reorder the columns
cols = ['Country', 'Description', 'Prefix', 'Effective from', 'Rate Id', 'Forbidden', 'Discontinued', 'Price 1', 'Price N', 'Interval 1', 'Interval N']
df = df[cols]

# Get the current timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Step 9: Write the data to a CSV file with a timestamp in its name
logging.info('Writing to CSV file.')
df.to_csv(f'tcxc_airtel_price_list_{timestamp}.csv', index=False)

logging.info('Airtel rate conversion script completed.')
