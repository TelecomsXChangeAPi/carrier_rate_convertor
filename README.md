# Carrier Rate Converter

This repository contains Python scripts for converting Airtel and Tata rate tables into a standardized format for use with Telecomsxchange.com's platform.

## Contents

1. `convert_airtel.py`: Python script to convert Airtel's voice rate table
2. `convert_tata.py`: Python script to convert Tata's voice rate table

## Usage

To use these scripts, follow these steps:

1. Place the rate table file (in Excel format) in the same directory as the script.

2. Run the Python script. 

```bash
python convert_airtel.py
python convert_tata.py
```


3. The script will generate a CSV file with the converted rate table. The name of the output file will include the name of the carrier and a timestamp.

## Logging

The scripts provide logging functionality. They log both to the console and to a log file named `airtel_log.log` or `tata_log.log`. 

## Contributing

Contributions to improve these scripts are welcome. Please feel free to fork this repository, make changes, and submit a pull request.

## Authors

These scripts were created by Ameed Jamous for Telecomsxchange.com.

## License

These scripts are provided as-is under the MIT license. See `LICENSE` for more information.
