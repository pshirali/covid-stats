# COVID-19 India JSON-to-CSV Data Extractor


## The Datasource

[COVID 19 India](https://covid19india.org) maintains code and structured-data for COVID-19 statistics, pulled from multiple sources across India with regular updates. This data is made available by them in both [JSON](https://api.covid19india.org/) and [CSV](https://api.covid19india.org/documentation/csv/) formats through Github.

A comprehensive data-set among these, is the `data-all.json` ([https://api.covid19india.org/v4/data-all.json](https://api.covid19india.org/v4/data-all.json)) which contains district-wise and state-wise statistics for all districts and states in India, from 1st confirmed case (30th January 2020) till present day. The JSON scheme has `date [YYYY-MM-DD]` as the key, with stats in the `v4` ([https://api.covid19india.org/documentation/v4_data.html](https://api.covid19india.org/documentation/v4_data.html)) format as values.


## The _covid-stats.py_ script

The file `covid-stats.py` is a Python3 script usable as a command-line tool. This script can extract specific content of interest from `data-all.json` and save it into a CSV file. This CSV file could then be imported into Excel, Google-Sheets etc for further analysis.

The script provides the ability to:

1. Extract content either across India, or for a single state in India
1. Extract only selected metrics from the `data-all.json` file, and optionally extract within a date-range
1. Extract the names of all metrics (flattened json-keys) such that a _mapping_ could be created.
    * The _mapping_ allows you to then handpick metrics of interest, reorder them and supply custom column names for the CSV.
    * The _mapping_ can be stored on disk as a JSON.
1. Use a _mapping_ file as a guide/configuration to extract metrics of interest and store it into a CSV.


## Prerequisites & Theory

_NOTE: This section is verbose to help serve those who aren't familiar with Python 3, CLI or JSON. Advanced users may jump to sections of relevance directly_

This script requires Python 3 installed on a system. You'll also require the script [covid-stats.py]() and the [data-all.json]() files downloaded into a common folder on your system.

If you are on Windows, you'll need to run `python3 covid-stats.py` from the Windows Command Prompt in the folder where the above files are placed.

If you are on *nix (Linux, MacOS), you'll need to run `./covid-stats.py` from a Terminal. Remember to set execute permissions: `chmod +x ./covid-stats.py`

Instructions henceforth will use the *nix format (`./covid-stats.py`). Windows users; when you see this, use `python3 covid-stats.py`.

#### Viewing CLI switches

You can use the `-h` switch to see _help_, which lists all the switches.
```
> ./covid-stats.py -h

usage: covid-stats.py [-h] [-i INPUT_FILE] [-u URL] [-n] [-o OUTPUT]
                      [-x] -s STATE [-c] [-m MAPPING] [--na NA]
                      [--start START] [--end END]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input-file INPUT_FILE
                        Input json to fetch data from
  -u URL, --url URL     URL from which to source data
  -n, --net             Fetch data from a URL
  -o OUTPUT, --output OUTPUT
                        Set output file for CSV (optional) or mapping
                        JSON (mandatory).
  -x, --overwrite       Overwrite output file if it exists.
  -s STATE, --state STATE
                        Two character Indian state code for which stats
                        must be processed (Ex: KA, HP etc). Use 'IN'
                        for all-India.
  -c, --columns         Print only column names as a dict
  -m MAPPING, --mapping MAPPING
                        Path to key-mapping file
  --na NA               Replacement string for 'no-value'
  --start START         Include data on or after this date (YYYY-MM-DD)
  --end END             Exclude data beyond this date (YYYY-MM-DD)
```

#### Types of operations

At any given time, you can get the script to do one of the two operations:

1. Generate a "mapping" file (a JSON file) comprising of all _flattened keys_ for different metrics available in `data-all.json` filtered based on the supplied conditions. You can modify the mapping file, to further suit your convenience.
2. Generate a CSV file with data extracted from the `data-all.json` file, against filter conditions provided both on command line, and optionally from the "mapping" file.

Sections below talk about each step in detail

#### Mapping metrics of interest

The `data-all.json` has its data in a hierarchical structure. The target format is a CSV (_x*y_ grid without hierarchy)

If the hierarchy had to be _flattened_ such that each metric was represented as a independent column in a CSV, this would result in over 6700+ metrics (states-in-India * metrics-per-state, states-in-India->Districts-in-each-state->metrics-per-district etc). A likely scenario is that a subset of metrics are of interest, and the script could extract only those metrics which are required for analysis.

The script achieves this by generating a _"mapping"_ file for either a state in India, or for the whole of India. A _"mapping"_ file is a JSON file with _flattened keys_ dumped as `keys: values` in a new JSON. A _flattened key_ is a path leading to a value from the hierarchy in `data-all.json`, represented as a hyphen `-` separated string in the _"mapping"_ JSON.

Example:
```
A nested JSON:
1. "KA" is key at depth-1. It's value is another JSON object with two keys "Bengaluru" and "Total".
2. "KA"->"Bengaluru" is a key at depth-2. It's value is yet another JSON object, with one key "Confirmed"
3. "KA"->"Bengaluru"->"Confirmed" is a key at depth-3, with a value 1000
4. "KA"->"Total" is a key at depth-2, with a value 1000
{
    "KA": {
        "Bengaluru": {
            "Confirmed": 1000
        }
        "Total": 1000
    }
}

A flattened, representation would have:
{
    "KA-Bengaluru-Confirmed": 1000,
    "KA-Total": 1000
}

^^^ The flattened JSON has all keys at depth-1, with no hierarchy
```

#### What is the purpose of mapping

Mapping allows keys of interest to be filtered, ordered and renamed, such that data is extracted only for metrics of interest.
When the Mapping is used as reference to extract and write data to into the CSV, it is done based on the order in which it is found in the mapping, using the _values_ as column names.

Example: A mapping generated by the script would look like this:
```
{
    "KA-Bengaluru-Confirmed": "KA-Bengaluru-Confirmed",
    "KA-Total": "KA-Total"
}
```

The keys and values are the same in the _generated_ mapping. However, you are welcome to modify it.

The _key_ on the left is used to identify the metric from the `data-all.json`. So, this key must be left as is.

The _value_ on the right is the name you wish to provide to the _column_ in the CSV. So, this could be modified. You may also re-order the keys. The order in the _mapping_ JSON (top-to-bottom) determines the order in the CSV (left-to-right)

Example:
```
{
    "KA-Total": "KA-TOTAL"
    "KA-Bengaluru-Confirmed": "KA-BLR-CNF",
}
```

The mapping above will result in extraction of data `KA-Total` and `KA-Bengaluru-confirmed` from the `data-all.json`. However, in the CSV, they'll be written with `KA-TOTAL` as the first column, and `KA-BLR-CNF` as the 2nd column (to its right).


## Usage

#### How do the switches work?

The `-i` switch is used to supply the path to the `data-all.json` on your disk. By default, the script tries look for a `data-all.json` in your current working directly. If you have one, then you need not supply this switch. The recommended way to use this tool is to download the `data-all.json` ahead of time, place it alongside the script, and use the script locally.

> An advanced option is to use `-n` to point the script to download the latest copy of `data-all.json` from the default COVID-19-India's URL. You can additionally supply a `-u` option to override the default URL (likely unnecessary). NOTE: This requires the `requests` library to be installed (`pip3 install requests`)

The `-o` switch is used to define the output file. The output is used for writing both the CSV file as well as the _mapping_ file. By default, the script avoids accidental rewrites, and quits if the output file already exists on disk. Use `-x` to allow overwriting.

The `-c` switch gets the script to dump a _mapping_ file. When this is not supplied, it is assumed that you wish to write a CSV.

The `-s` switch indicates region. At this point, this is restricted to the two character codes of states in India (`KA`, `KL`, `TN`, etc.) or `IN` for the whole of India.

The `--start` and `--end` switches will restrict processing to dates which fall in between the start and end dates (both inclusive).

The `--na` switch allows defining a custom "empty" value, when an actual value is not found in the `data-all.json`. By default this is "0" as the metrics are _mostly_ numbers.

#### Usage Examples

_NOTE: In both examples `-i data-all.json` is optional if you have `data-all.json` stored locally in your current folder_

##### 1. Generate a mapping for the state of Karnataka

```
./covid-stats.py -i data-all.json -s KA -c -o KA-BLR.json
```
Note the `-c` being passed here to indicate dumping the mapping columns. The this command fetchs all keys related to Karnataka (KA) and dumps them in _flattened_ form into a mapping file `KA-BLR.json`

Once this is done, you can manually edit the `KA-BLR.json` file, remove entries that you don't require, rename the _values_ to your desired column names, or change the order of the entries. Save this file after your modifications.

A _modified_ [KA-BLR.json](https://github.com/pshirali/covid-stats/blob/main/KA-BLR.json) is available for reference.

##### 2. Use a mapping file to extract data into a CSV

```
./covid-stats.py -i data-all.json -s KA -m KA-BLR.json --start 2020-09-01 --end 2020-09-10 -o KA-DATA.csv
```
Note the lack of `-c` in the above command, which indicates that a CSV is being written and not a mapping file.

Also, note the `-m KA-BLR.json` which tells the script to _use_ the mapping file `KA-BLR.json` which was edited in the previous step. Only the metrics of interest from `KA-BLR.json` are fetched. Additionally, the data is fetched only for dates 1st September 2020 to 10th September 2020 (both dates inclusive), and written to `KA-DATA.csv`

The contents of `KA-DATA.csv` will be as follows:
```
"DATE","BLR-CNF","BLR-DEC","BLR-OTH","BLR-REC","BLR-TST","KA-CNF","KA-DEC","KA-OTH","KA-REC","KA-TST"
"2020-09-01","132092","2005","1","91180","892219","351481","5837","19","254626","2979477"
"2020-09-02","135512","2037","1","93563","919200","361341","5950","19","260913","3052794"
"2020-09-03","138701","2066","1","96194","947518","370206","6054","19","268035","3123918"
"2020-09-04","141664","2091","1","97926","978563","379486","6170","19","274196","3197110"
"2020-09-05","144757","2125","1","101152","1009349","389232","6298","19","283298","3273871"
"2020-09-06","147581","2163","1","105692","1038077","398551","6393","19","292873","3348255"
"2020-09-07","150523","2211","1","108642","1060813","404324","6534","19","300770","3393676"
"2020-09-08","153625","2266","1","110972","1060813","412190","6680","19","308573","3461119"
"2020-09-09","157044","2307","1","112536","1112090","421730","6808","19","315433","3531441"
"2020-09-10","160205","2340","1","114208","1137027","430947","6937","19","322454","3586150"
```

## Changelog

#### 0.0.2

1. Added version tracking in the code
1. Switches '-o/--output' with '-x' now apply to output of both CSV as well as mapping JSON depending on context.
1. In the mapping JSON, the custom column names used to be empty strings to allow custom names to be filled in. Now they are the same as the original column names, so, you can rename only those that you need.
1. The script prints on console about whether it wrote a CSV or a Mapping JSON.

#### 0.0.1

Initial release of the script

## License

[Apache 2.0 License](LICENSE) and [NOTICE](NOTICE.md)
