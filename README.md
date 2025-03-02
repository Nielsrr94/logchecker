# LogChecker

## Purpose
The `logchecker.py` script is designed to help users efficiently search through log files for specific keyphrases. This tool simplifies the process of identifying important information within large log files.

## Keyphrases
The keyphrases that the `logchecker.py` script searches for are defined in the `keyphrases_config.json` file. These keyphrases can be customized by the user to match the specific terms or patterns they are interested in finding within their log files.

## Changing the Keyphrases Config
To change the keyphrases, simply edit the `keyphrases_config.json` file. This file is structured in a straightforward JSON format, allowing users to add, remove, or modify the keyphrases as needed. After updating the file, the `logchecker.py` script will use the new keyphrases for its searches.

## Changing the Search Directory and using custom Keyphrases directly
When running the `logchecker.py` script, the user is prompted to enter the directory path, in which it should check for files that include the word "log". Just pressing enter will execute the script in the directory that it is placed in.

In a second prompt the user is asked if they want to give a list of keyphrases instead of using the config file. Answering 'yes' will prompt the user to give a list, separated by commas. Any other input (such as just pressing enter) will lead to the config file being used.

