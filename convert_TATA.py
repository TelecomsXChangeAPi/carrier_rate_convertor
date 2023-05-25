"""
Script for processing TATA rate table
Author: Ameed Jamous
Company: Telecomsxchange.com
Copyright (c) 2023 Telecomsxchange.com
"""


import pandas as pd
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(filename='tata_log.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

logging.info('Script started.')



df = pd.read_excel('Amend_32968_USHAMAURYA.xlsx', skiprows=21)
logging.info('Excel file read.')

# Step 2: Rename 'City Code(s)' column to 'Prefix' and remove '-'
df['Prefix'] = df['City Code(s)'].str.replace('-', '')


# Step 3: Rename 'Price($)' to 'Price 1' and 'Price N'
df['Price($)'] = pd.to_numeric(df['Price($)'], errors='coerce')  # Convert to numeric values
df['Price 1'] = df['Price($)'] * 1.05  # Add 5% margin to Price 1
df['Price N'] = df['Price($)'] * 1.05  # Add 5% margin to Price N



# Step 4: Convert 'Effective Date' to 'Effective from' in the desired format
df['Effective Date'] = pd.to_datetime(df['Effective Date'], format='%d-%b-%y')
df['Effective from'] = df['Effective Date'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Update 'Effective from' if date is in the past
df.loc[df['Effective Date'] < pd.to_datetime(datetime.now()), 'Effective from'] = "ASAP"

# Step 5: Set 'Interval 1' and 'Interval N' to 1 as default
df['Interval 1'] = 1
df['Interval N'] = 1

# Split the 'Destination' column on '-' and only keep the first part (the country name)
df['Destination'] = df['Destination'].str.split('-').str[0].str.strip().str.lower()

# Step 6: Set 'Interval 1' and 'Interval N' based on the country of the destination
countries_60_60 = ['american samoa', 'cook islands', 'emsat', 'fiji', 'french polynesia', 'haiti', 'intl network', 'kiribati', 'lesotho', 'maldives', 'mcp network', 'mexico', 'new caledonia', 'nauru', 'niue', 'onair', 'papua new guinea', 'solomon islands', 'suriname', 'thuraya', 'tokelau', 'tonga', 'tuvalu', 'vanuatu', 'western samoa', 'iridium']
countries_60_1 = ['vietnam']
countries_30_6 = ['brazil']

# Match and update 'Interval 1' and 'Interval N' accordingly
df.loc[df['Destination'].isin(countries_60_60), ['Interval 1', 'Interval N']] = 60
df.loc[df['Destination'].isin(countries_60_1), ['Interval 1', 'Interval N']] = [60, 1]
df.loc[df['Destination'].isin(countries_30_6), ['Interval 1', 'Interval N']] = [30, 6]


# Step 6: Set 'Interval 1' and 'Interval N' based on the country of the destination
countries_60_60 = ['American Samoa', 'Cook Islands', 'Emsat', 'Fiji', 'French Polynesia', 'Haiti', 'Intl network', 'Kiribati', 'Lesotho', 'Maldives', 'Mcp network', 'Mexico', 'New Caledonia', 'Nauru', 'Niue', 'Onair', 'Papua New Guinea', 'Solomon Islands', 'Suriname', 'Thuraya', 'Tokelau', 'Tonga', 'Tuvalu', 'Vanuatu', 'Western Samoa', 'Iridium']
countries_60_1 = ['Vietnam']
countries_30_6 = ['Brazil']

df.loc[df['Destination'].isin(countries_60_60), ['Interval 1', 'Interval N']] = '60'
df.loc[df['Destination'].isin(countries_60_1), 'Interval 1'] = '60'
df.loc[df['Destination'].isin(countries_60_1), 'Interval N'] = '1'
df.loc[df['Destination'].isin(countries_30_6), 'Interval 1'] = '30'
df.loc[df['Destination'].isin(countries_30_6), 'Interval N'] = '6'


# Step 6: Add new columns and set their default values
df['Country'] = ''
df['Description'] = ''
df['Rate Id'] = ''
df['Forbidden'] = 0
df['Discontinued'] = 0

# Step 7: Remove unnecessary columns
df = df.drop(columns=['Destination', 'City Code(s)', 'Price($)', 'Effective Date', 'Prime Assurance', 'Comments', 'Service Level'])

# Step 8: Reorder the columns
cols = ['Country', 'Description', 'Prefix', 'Effective from', 'Rate Id', 'Forbidden', 'Discontinued', 'Price 1', 'Price N', 'Interval 1', 'Interval N']
df = df[cols]

# Filter out empty rows
df = df.dropna(subset=['Prefix', 'Effective from'], how='all')

# Get the current timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Write the data to a CSV file with a timestamp in its name
df.to_csv(f'tcxc_tata_price_list_{timestamp}.csv', index=False)
logging.info(f'CSV file tcxc_tata_price_list_{timestamp}.csv written in TCXC format.')

logging.info('Script finished.')
