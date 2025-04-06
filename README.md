## Detailed Usage and Output

### Command-Line Options

When running `logchecker.py`, you can use the following options to customize its behavior:

- `-k`, `--keyword`: Specify a keyword or pattern to search for in the log file. This can be a string or a regular expression.
    - Example: `python logchecker.py -k "ERROR" example.log`
- `-o`, `--output`: Specify a file to save the results. If not provided, the results will be displayed in the terminal.
    - Example: `python logchecker.py -o results.txt example.log`
- `-h`, `--help`: Display a help message with details about all available options.
    - Example: `python logchecker.py -h`
- `-f`, `--format`: Specify the output format. Supported formats include `text`, `json`, and `html`. The default is `text`.
    - Example: `python logchecker.py -f html -o results.html example.log`
- `-c`, `--case-sensitive`: Perform a case-sensitive search. By default, the search is case-insensitive.
    - Example: `python logchecker.py -k "Warning" -c example.log`

### HTML Output

If the `html` format is selected, the script generates an interactive HTML report. The HTML file includes the following features:

1. **Search Results Table**:
     - Displays all matches found in the log file.
     - Columns include the line number, timestamp (if detected), and the matching log entry.
     - Rows are color-coded to highlight errors (e.g., red for "ERROR") or warnings (e.g., yellow for "WARNING").

2. **Navigation Panel**:
     - A sidebar or top menu allows you to filter results by severity (e.g., "ERROR", "WARNING", "INFO").
     - Quick navigation to specific sections of the log file.

3. **Summary Section**:
     - Provides an overview of the log analysis, including:
         - Total number of matches.
         - Breakdown of matches by severity.
         - Most frequent keywords or patterns.

4. **Export Options**:
     - Buttons to export the results in other formats (e.g., CSV or JSON).
     - Option to print the report directly from the browser.

### Example HTML Workflow

1. Run the script with the `html` format:
     ```bash
     python logchecker.py -k "ERROR" -f html -o results.html example.log
     ```
2. Open the generated `results.html` file in a web browser.
3. Use the navigation panel to filter and explore the results.
4. Export the filtered results or print the report as needed.

### Additional Notes

- The HTML report is fully responsive and works on both desktop and mobile browsers.
- Custom styles or themes can be applied by modifying the included CSS file in the project.

By using these options and features, `logchecker.py` provides a flexible and user-friendly way to analyze log files and generate actionable insights.
