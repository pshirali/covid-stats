# COVID-19 India JSON-to-CSV Stats Extractor

## The Datasource

[COVID 19 India](https://covid19india.org) maintains code and structured-data for COVID-19 statistics, pulled from multiple sources across India with regular updates. This data is made available by them in both [JSON](https://api.covid19india.org/) and [CSV](https://api.covid19india.org/documentation/csv/) formats through Github.

A comprehensive data-set among these, is the `data-all.json` ([https://api.covid19india.org/v4/data-all.json](https://api.covid19india.org/v4/data-all.json)) which contains district-wise and state-wise statistics for all districts and states in India, from 1st confirmed case (30th January 2020) till present day. The JSON scheme has `date [YYYY-MM-DD]` as the key, with stats in the `v4` ([https://api.covid19india.org/documentation/v4_data.html](https://api.covid19india.org/documentation/v4_data.html)) format as values.

## The `covid-stats.py` script

The file `covid-stats.py` is a Python3 script usable as a command-line tool. This script can extract specific content of interest from `data-all.json` and save it into a CSV file. This CSV file could then be imported into Excel, Google-Sheets etc for further analysis.

The script provides the ability to:

1. Extract content either across India, or for a single state in India
1. Extract only selected metrics from the `data-all.json` file, and optionally extract within a date-range
1. Extract the names of all metrics (flattned json-keys) such that a _mapping_ could be created.
    * The _mapping_ allows you to then handpick metrics of interest, reorder them and supply custom column names for the CSV.
    * The _mapping_ can be stored on disk as a JSON.
1. Use a _mapping_ file as a guide/configuration to extract metrics of interest and store it into a CSV.

## Tutorial

The [TUTORIAL.md](TUTORIAL.md) covers all instructions on how to get started and how to use this script in detail.

## License

[Apache 2.0 License](LICENSE) and [NOTICE](NOTICE.md)
