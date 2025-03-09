# LogChecker

## 1. Purpose
The `logchecker.py` script is designed to help users efficiently search through log files for specific keyphrases. This tool simplifies the process of identifying important information within large log files.

## 2. Configuring the Script

### 2.1 Filenames
The Filenames that the `logchecker.py` script searches in are defined in the `filenames_config.json` file. These filenames can be customized by the user to match the specific files they are interested in searching for keywords in.

### 2.2 Changing the Filenames Config
To change the filenames, simply edit the `filenames_config.json` file. This file is structured in a straightforward JSON format, allowing users to add, remove, or modify the filenames as needed. After updating the file, the `logchecker.py` script will use the new filenames for its searches.

### 2.3 Keyphrases
The keyphrases that the `logchecker.py` script searches for are defined in the `keyphrases_config.json` file. These keyphrases can be customized by the user to match the specific terms or patterns they are interested in finding within their log files.

### 2.4 Changing the Keyphrases Config
To change the keyphrases, simply edit the `keyphrases_config.json` file. This file is structured in a straightforward JSON format, allowing users to add, remove, or modify the keyphrases as needed. After updating the file, the `logchecker.py` script will use the new keyphrases for its searches.

## 3. Running the Script
To run the `logchecker.py` script, use the following command:
```bash
python logchecker.py
```
Follow the prompts to specify the search directory and keyphrases as needed (see 3.1 Prompts).

### 3.1 Prompts
When running the `logchecker.py` script, the user is prompted to enter the directory path in which it should check for files that include the filenames defined in the `filenames_config.json` file. Just pressing enter will execute the script in the directory that it is placed in.

In a second prompt, the user is asked if they want to provide a list of keyphrases instead of using the config file. Answering 'yes' will prompt the user to provide a list, separated by commas. Any other input (such as just pressing enter) will lead to the config file being used.

The script will give a prompt stating that it is checking for logs once it starts searching.

## 4. Script Results

A pop-up will appear once the logcheck is completed, giving the user the option to open the report directly from the pop-up or to close the pop-up. A verdict stating whether keyphrases have been found will be shown in the pop-up as a summary.

The result of the `logchecker.py` is provided in an .html file with the prefix "logcheck_" followed by the date and time of execution. The file is created in the defined search directory (see 3.1 Prompts).
