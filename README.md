# DynamoDB to JSON/CSV converter for MSS Nexus data
_23 Jun 2021_

## Step 1: Installation Instructions
To install this application, ensure that `python >= 3.9.1`
> `pip3 install -r requirements.txt -v`

Ensure that `aws` is installed on the system, and that following values are configured:
* `ACCESS_KEY_ID`
* `SECRET_ACCESS_KEY`
* `REGION`

Link to get the `aws` CLI: https://aws.amazon.com/cli/

Last tested on `aws` CLI version `aws-cli/1.19.96` `botocore/1.20.96` (25 Jun 2021)

## Step 2: Configuration
Ensure that `tableName` variable is adjusted. (if no arguments provided)

A custom table name can be defined in the first argument (shown in Step 3).

## Step 3: Execution
To run this application where `tableName` is the default table:
> `python3 main.py`

To run this application where table is no default value, of `mytt-dev-project`
> `python3 main.py mytt-dev-project`

The files will be in the respective directory:
* CSV Files: `csv/(file).csv`
* JSON Files: `json/(file).json`
* Main script: `main.py`
* Custom table scripts: `customTables/`
  * These custom tables are derived off the main script.

License: MIT
