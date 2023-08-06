# Hofund - Proto Recommendor

Python based tool which recommends the common proto messages/fields that can be used as replacements for clevertap fields.

## Requirements

If you want to install using pip, you would need - 
- python 3.9
- pip3.9

## Installation

Hofund can be installed by either using `pip` or `brew`. `brew` is the recommended package manager.

### Using brew
If you don't have `brew` installed in your laptop, follow the instructions [here](https://brew.sh/)

After installing `brew` you would need to add your ssh keys to Gitlab(ignore if already done). If you don't have ssh keys you can generate one by following the instructions [here](https://docs.gitlab.com/ee/ssh/#generate-an-ssh-key-pair). To add your keys keys to Gitlab you can follow the instructions [here](https://docs.gitlab.com/ee/ssh/#add-an-ssh-key-to-your-gitlab-account)

Once the setup is done, run the following command to install the tool.
```
brew update
brew tap gojek/de git@source.golabs.io:asgard/lib/homebrew-tap
brew install hofund
```

### Using pip

To install latest version of hofund
```
pip install hofund
```

### Quickstart
The input to the tool is a csv which should contain a column that has the context for properties that needs mapping. The column name is given as input while runing the tool.

Example - We have a [sheet](https://docs.google.com/spreadsheets/d/14_nQyKqIcWIrpD8gwk1QpzPklNLUcTKDMwvNUMsNweI/edit?usp=sharing) that contains the common format for proto mapping. In this sheet we have a column named `Context/Meaning` which has to be populated by the user manually and then the sheet should be downloaded as a `csv`. The context should contain keywords seperated by spaces ` ` that helps in identifying the given property. Users can find the download option under `File` menu.   

Run `hofund --f <csv_file> --ctx-col <context_column_name> `, you can also give parameter `--ctx-col-num <context_col_num>` as column number of the context column. Here, `csv_file` is the location of the downloaded file in your laptop and `context_column_name` will be `Context/Meaning`.s

After the successful execution, the tool adds two columns at the end of the csv file. Column `Recommended Protos` are the recommended proto names and `Recommended Fields` are the recommended proto fields based on the given context.

## Working
The tool works on the context specified by the user. It searches all the proto definitions and the comments by each keyword in the context column. Ensure that it is concise, preferabbly in one or two words seperated by a delimeter. By default the delimeter is a space ` `.
For example if the context is `App version` then tool searches for all proto definitions that contains either `app` or `version` in the name or comments.

## Usage    

To begin using the tool first user needs to export stencil token, this is used to contect with Stencil service. For token contact @Ramey/@Chakravarthy V P
```
export HOFUND_STENCIL_TOKEN="<token>" 
```

The input to the tool is a csv which should contain a column that has the context for properties that needs mapping. The column name is given as input while runing the tool.

Example - We have a [sheet](https://docs.google.com/spreadsheets/d/14_nQyKqIcWIrpD8gwk1QpzPklNLUcTKDMwvNUMsNweI/edit?usp=sharing) that contains the common format for proto mapping. In this sheet we have a column named `Context/Meaning` which has to be populated by the user manually and then the sheet should be downloaded as a `csv`. The context should contain keywords seperated by spaces ` ` that helps in identifying the given property. Users can find the download option under `File` menu.   

Run `hofund --f <csv_file> --ctx-col <context_column_name> `, you can also give parameter `--ctx-col-num <context_col_num>` as column number of the context column. Here, `csv_file` is the location of the downloaded file in your laptop and `context_column_name` will be `Context/Meaning`.s

After the successful execution, the tool adds two columns at the end of the csv file. Column `Recommended Protos` are the recommended proto names and `Recommended Fields` are the recommended proto fields based on the given context.

## Working
The tool works on the context specified by the user. It searches all the proto definitions and the comments by each keyword in the context column. Ensure that it is concise, preferabbly in one or two words seperated by a delimeter. By default the delimeter is a space ` `.
For example if the context is `App version` then tool searches for all proto definitions that contains either `app` or `version` in the name or comments.

## Usage    

To check the usage
```
hofund --help
``` 

## Params
* `--ctx-keys-del ` - context delimeter, by default it's space.
* `--out-msg-col` - column name that contains the name of the recommended proto definitions, by default it's `Recommended Protos`.
* `--out-field-col` - column name that contains the field names of the recommended proto definitions, by default `Recommended Fields`.