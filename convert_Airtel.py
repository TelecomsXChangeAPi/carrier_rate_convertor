"""
Script for processing Bharti Airtel rate table
Author: Ameed Jamous
Company: Telecomsxchange.com
Copyright (c) 2023 Telecomsxchange.com

Usage: python convert_Airtel.py [path/to/airtel_price_list.xlsx]
"""

import sys
import pandas as pd
import logging
from datetime import datetime

# Set up logging
log_format = '%(asctime)s:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.INFO, filename='airtel_log.log', format=log_format)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter(log_format))
logging.getLogger('').addHandler(console)
logging.info('Starting Airtel rate conversion script.')

# Step 1: Read the pricing sheet as raw rows so the header row can be located
file_name = sys.argv[1] if len(sys.argv) > 1 else 'Airtel.xlsx'
logging.info(f'Reading file: {file_name}')
if file_name.endswith('.csv'):
    raw = pd.read_csv(file_name, header=None, dtype=str)
else:
    raw = pd.read_excel(file_name, sheet_name=0, header=None, dtype=object)

# Find the header row by its column names; the rates header is an Excel formula
# whose cached text varies between exports, so match it by prefix only
def is_header(row):
    cells = [str(v).strip() for v in row.values]
    return {'Complete Code', 'Valid From', 'Pulse'}.issubset(cells) and any(c.startswith('Rates') for c in cells)

header_rows = raw.index[raw.apply(is_header, axis=1)]
if header_rows.empty:
    raise ValueError(f'No header row with Complete Code, Rates, Valid From and Pulse found in {file_name}')
header_row = header_rows[0]
headers = [str(h).strip() for h in raw.iloc[header_row]]
rate_col = next(h for h in headers if h.startswith('Rates'))
df = raw.iloc[header_row + 1:].copy()
df.columns = headers
df = df.dropna(subset=['Complete Code'])

# Step 2: Rename the 'Complete Code' column to 'Prefix'
logging.info('Renaming and adjusting columns.')
df['Prefix'] = df['Complete Code'].astype(str).str.strip()

# Step 3: Duplicate the rate column to 'Price 1' and 'Price N'
df['Price 1'] = pd.to_numeric(df[rate_col], errors='raise')
df['Price N'] = df['Price 1']

# Step 4: Convert the 'Valid From' column to 'Effective from' in the desired format
valid_from = pd.to_datetime(df['Valid From'], dayfirst=True)
df['Effective from'] = valid_from.apply(lambda x: 'ASAP' if x < datetime.now() else x.strftime('%Y-%m-%d %H:%M:%S'))

# Step 5: Split 'Pulse' into 'Interval 1' and 'Interval N'
pulse_df = df['Pulse'].astype(str).str.split('/', expand=True)
df['Interval 1'] = pulse_df[0].astype(int)
df['Interval N'] = pulse_df[1].astype(int)

# Step 6: Add new columns and set their default values
df['Country'] = ''
df['Description'] = ''
df['Rate Id'] = ''
df['Forbidden'] = 0
df['Discontinued'] = 0

# Step 7: Keep and reorder the TCXC columns
cols = ['Country', 'Description', 'Prefix', 'Effective from', 'Rate Id', 'Forbidden', 'Discontinued', 'Price 1', 'Price N', 'Interval 1', 'Interval N']
df = df[cols]

# Get the current timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Step 8: Write the data to a CSV file with a timestamp in its name
output_filename = f'tcxc_airtel_price_list_{timestamp}.csv'
logging.info(f'Writing {len(df)} rows to {output_filename}.')
df.to_csv(output_filename, index=False)

logging.info('Airtel rate conversion script completed.')
