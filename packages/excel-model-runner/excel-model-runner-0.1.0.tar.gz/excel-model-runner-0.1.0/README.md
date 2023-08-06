# excel-model-runner

This tool will take an Excel model (.xlsx), update any parameters as defined in the parameters file
and calculate all cells, resulting in an Excel spreadsheet resembling the original, but with all
formula cells replaced by the calculated values.

The parameter file can be either JSON file or a CSV file in the following format:

<br> 

## Config file

JSON:
```
{
   "Sheet name.Cell1": "Replacement value string",
   "Sheet name.Cell2": Replacement value float
}
```

Example: `params.json`
```
{
    "Variables.C2": "red",
    "Variables.C3": 0.8
}
```

<br> 
<br> 

CSV:
```
Sheet name.Cell1,Replacement value string
Sheet name.Cell2,Replacement value float
```

Example: `params.csv`
```
Variables.C2,red
Variables.C3,0.8
```
NOTE: Do NOT include a header row in the CSV

<br> 
<br> 

## Usage:

```
usage: run-excel-model [-h] [--output_dir OUTPUT_DIR] [--run_dir RUN_DIR] source_file parameter_file

positional arguments:
  source_file           Excel (xlsx) file that contains
  parameter_file        Path to json or csv parameter file

optional arguments:
  -h, --help            show this help message and exit
  --output_dir OUTPUT_DIR
                        Optional output location. (Default: output)
  --run_dir RUN_DIR     Optional directory to store intermediate files. (Default: runs)
```
