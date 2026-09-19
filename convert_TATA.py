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

# Step 1: Read the Excel file, skipping the first 21 rows
df = pd.read_excel('Amend_32968_PRAVEENKUMAR.xlsx', skiprows=21)
logging.info('Excel file read.')

# Step 2: Rename 'City Code(s)' column to 'Prefix' and remove any hyphens
df['Prefix'] = df['City Code(s)'].str.replace('-', '', regex=False)

# Step 3: Convert 'Price($)' to numeric and create 'Price 1' and 'Price N' columns with a 11% margin
df['Price($)'] = pd.to_numeric(df['Price($)'], errors='coerce')
df['Price 1'] = df['Price($)'] * 1.11
df['Price N'] = df['Price($)'] * 1.11

# Step 4: Convert 'Effective Date' to 'Effective from' in the desired format
df['Effective Date'] = pd.to_datetime(df['Effective Date'], format='%d-%b-%y', errors='coerce')
df['Effective from'] = df['Effective Date'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Update 'Effective from' if the date is in the past
df.loc[df['Effective Date'] < pd.to_datetime(datetime.now()), 'Effective from'] = "ASAP"

# Step 5: Initialize 'Interval 1' and 'Interval N' columns as integers
df['Interval 1'] = 1
df['Interval N'] = 1

# Convert the 'Destination' column to lowercase and strip any unnecessary spaces
df['Destination'] = df['Destination'].str.split('-').str[0].str.strip().str.lower()

# Step 6: Set 'Interval 1' and 'Interval N' based on the destination country
countries_60_60 = ['united arab emirates', 'oman', 'qatar', 'algeria', 'american samoa', 'cook islands', 'emsat', 
                   'fiji', 'french polynesia', 'haiti', 'intl network', 'kiribati', 'lesotho', 'maldives', 
                   'mcp network', 'mexico', 'new caledonia', 'nauru', 'niue', 'onair', 'papua new guinea', 
                   'solomon islands', 'suriname', 'thuraya', 'tokelau', 'tonga', 'tuvalu', 'vanuatu', 
                   'western samoa', 'iridium', 'saudi arabia', 'india']
countries_60_1 = ['vietnam', 'indonesia', 'sri lanka', 'south korea', 'new zealand', 'singapore','thailand', 'brunei','nepal']
countries_30_6 = ['brazil']

# Apply the intervals accordingly
df.loc[df['Destination'].isin(countries_60_60), ['Interval 1', 'Interval N']] = 60
df.loc[df['Destination'].isin(countries_60_1), ['Interval 1', 'Interval N']] = [60, 1]
df.loc[df['Destination'].isin(countries_30_6), ['Interval 1', 'Interval N']] = [30, 6]

# Ensure 'Interval 1' and 'Interval N' remain as numeric types
df['Interval 1'] = pd.to_numeric(df['Interval 1'], downcast='integer')
df['Interval N'] = pd.to_numeric(df['Interval N'], downcast='integer')

# Step 7: Add new columns with default values
df['Country'] = ''
df['Description'] = ''
df['Rate Id'] = ''
df['Forbidden'] = 0
df['Discontinued'] = 0

# Step 8: Remove unnecessary columns
df = df.drop(columns=['Destination', 'City Code(s)', 'Price($)', 'Effective Date', 'Prime Assurance', 'Comments', 'Service Level'])

# Step 9: Reorder the columns for the final output
cols = ['Country', 'Description', 'Prefix', 'Effective from', 'Rate Id', 'Forbidden', 'Discontinued', 'Price 1', 'Price N', 'Interval 1', 'Interval N']
df = df[cols]

# Step 10: Filter out rows without a prefix (blank rows and footer notes)
df = df.dropna(subset=['Prefix'])

# Stop rather than upload rates whose date or price could not be read
invalid = df[df['Effective from'].isna() | df['Price 1'].isna()]
if not invalid.empty:
    logging.error(f'{len(invalid)} rows have an unreadable Effective Date or Price($), e.g. prefixes {invalid["Prefix"].head(5).tolist()}')
    raise SystemExit(1)

# Step 11: Get the current timestamp and write the data to a CSV file
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_filename = f'tcxc_prod_tata_price_list_{timestamp}.csv'
df.to_csv(output_filename, index=False)
logging.info(f'CSV file {output_filename} written in TCXC format.')

logging.info('Script finished.')
