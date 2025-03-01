import os
import datetime
import zipfile

# Define the keywords to search for
keywords = ["error", "fail", "warning"]

# Get the directory from the user
user_input = input("Enter the directory path to search for log files (or type 'here' to use the current directory): ")
current_directory = os.path.dirname(os.path.abspath(__file__)) if user_input.lower() == "here" else user_input

# Get the current timestamp
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

# Initialize dictionaries and counters
keyword_counts = {keyword: 0 for keyword in keywords}
file_keyword_counts = {}
files_checked = 0
files_with_keywords = 0

# Function to process a file
def process_file(file_path, filename):
    global files_checked, files_with_keywords
    files_checked += 1
    file_keyword_counts[filename] = {keyword: [] for keyword in keywords}
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    file_has_keywords = False
    unique_keywords = set()
    for i, line in enumerate(lines):
        for keyword in keywords:
            if f" {keyword} " in line or line.startswith(f"{keyword} ") or line.endswith(f" {keyword}") or line == keyword:
                file_keyword_counts[filename][keyword].append((i + 1, line.strip()))
                file_has_keywords = True
                unique_keywords.add(keyword)
    
    for keyword in unique_keywords:
        keyword_counts[keyword] += 1
    
    if file_has_keywords:
        files_with_keywords += 1

# Iterate over all files in the current directory
for filename in os.listdir(current_directory):
    file_path = os.path.join(current_directory, filename)
    if filename.endswith(".txt") and "log" and "logcheck" not in filename:
        process_file(file_path, filename)
    elif filename.endswith(".zip"):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            for zip_info in zip_ref.infolist():
                if zip_info.filename.endswith(".txt"):
                    with zip_ref.open(zip_info) as file:
                        lines = file.readlines()
                        files_checked += 1
                        file_keyword_counts[zip_info.filename] = {keyword: [] for keyword in keywords}
                        file_has_keywords = False
                        unique_keywords = set()
                        for i, line in enumerate(lines):
                            line = line.decode('utf-8')
                            for keyword in keywords:
                                if f" {keyword} " in line or line.startswith(f"{keyword} ") or line.endswith(f" {keyword}") or line == keyword:
                                    file_keyword_counts[zip_info.filename][keyword].append((i + 1, line.strip()))
                                    file_has_keywords = True
                                    unique_keywords.add(keyword)
                        for keyword in unique_keywords:
                            keyword_counts[keyword] += 1
                        if file_has_keywords:
                            files_with_keywords += 1

# Calculate percentages
percentage_files_with_keywords = (files_with_keywords / files_checked) * 100 if files_checked > 0 else 0
keyword_percentages = {keyword: (count / files_checked) * 100 if files_checked > 0 else 0 for keyword, count in keyword_counts.items()}

# Prepare the output file
output_filename_txt = f"logcheck_{timestamp}.txt"
output_filename_html = f"logcheck_{timestamp}.html"

# Write to the text file
with open(os.path.join(current_directory, output_filename_txt), 'w') as output_file:
    # Write the header
    output_file.write("="*60 + "\n")
    output_file.write(f"{'Log Check Report':^40}\n")
    output_file.write("="*60 + "\n")
    human_readable_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_file.write(f"{'Reported created:':<20}{human_readable_timestamp:>20}\n")
    output_file.write("="*60 + "\n\n")
    
    # Write the summary of keyword occurrences
    total_keywords_found = sum(keyword_counts.values())
    output_file.write("="*60 + "\n")
    output_file.write(f"{'Summary of Keyword Occurrences':^40}\n")
    output_file.write("="*60 + "\n")
    output_file.write(f"{'Files Checked:':<30}{files_checked:>10}\n")
    output_file.write(f"{'Total Keywords Found:':<30}{total_keywords_found:>10}\n")
    output_file.write(f"{'Files with Keywords:':<30}{files_with_keywords:>10} ({percentage_files_with_keywords:.2f}%)\n")
    output_file.write("-"*60 + "\n")
    for keyword, count in keyword_counts.items():
        output_file.write(f"{'Keyword:':<20}{keyword:<10}{'Occurrences:':<10}{count:>5} ({keyword_percentages[keyword]:.2f}%)\n")
    output_file.write("="*60 + "\n\n")
    
    # Write the results per logfile
    output_file.write("="*60 + "\n")
    output_file.write(f"{'Detailed Log File Analysis':^40}\n")
    output_file.write("="*60 + "\n\n")
    
    result_number = 1
    for filename, keywords_dict in file_keyword_counts.items():
        if any(len(lines) > 0 for lines in keywords_dict.values()):
            output_file.write("*"*40 + "\n")
            output_file.write(f"{'Result Number:':<15}{result_number}\n")
            output_file.write(f"{'File:':<10}{filename}\n")
            output_file.write("-"*60 + "\n")
            for keyword, lines in keywords_dict.items():
                if lines:
                    output_file.write(f"  {'Keyword:':<10}{keyword:<10}{'Occurrences:':<10}{len(lines):>5}\n")
                    output_file.write("  " + "-"*38 + "\n")
                    for line_num, line in lines:
                        output_file.write(f"    {'Line':<5}{line_num:<5}: {line}\n")
                    output_file.write("  " + "-"*38 + "\n")
            output_file.write("="*60 + "\n\n")
            result_number += 1

# Write to the HTML file
with open(os.path.join(current_directory, output_filename_html), 'w') as output_file:
    # Write the header
    output_file.write("<html><head><title>Log Check Report</title></head><body>")
    output_file.write("<h1 style='text-align:center;'>Log Check Report</h1>")
    human_readable_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_file.write(f"<p><strong>Report created:</strong> {human_readable_timestamp}</p>")
    output_file.write("<hr>")
    
    # Write the summary of keyword occurrences
    total_keywords_found = sum(keyword_counts.values())
    output_file.write("<h2>Summary of Keyword Occurrences</h2>")
    output_file.write(f"<p><strong>Files Checked:</strong> {files_checked}</p>")
    output_file.write(f"<p><strong>Total Keywords Found:</strong> {total_keywords_found}</p>")
    output_file.write(f"<p><strong>Files with Keywords:</strong> {files_with_keywords} ({percentage_files_with_keywords:.2f}%)</p>")
    output_file.write("<ul>")
    for keyword, count in keyword_counts.items():
        output_file.write(f"<li><strong>Keyword:</strong> {keyword} - <strong>Occurrences:</strong> {count} ({keyword_percentages[keyword]:.2f}%)</li>")
    output_file.write("</ul>")
    output_file.write("<hr>")
    
    # Write the results per logfile
    output_file.write("<h2>Detailed Log File Analysis</h2>")
    
    result_number = 1
    for filename, keywords_dict in file_keyword_counts.items():
        if any(len(lines) > 0 for lines in keywords_dict.values()):
            output_file.write("<div style='border:1px solid #000; padding:10px; margin-bottom:10px;'>")
            output_file.write(f"<h3>Result Number: {result_number}</h3>")
            output_file.write(f"<p><strong>File:</strong> {filename}</p>")
            for keyword, lines in keywords_dict.items():
                if lines:
                    output_file.write(f"<p><strong>Keyword:</strong> {keyword} - <strong>Occurrences:</strong> {len(lines)}</p>")
                    output_file.write("<ul>")
                    for line_num, line in lines:
                        output_file.write(f"<li><strong>Line {line_num}:</strong> {line}</li>")
                    output_file.write("</ul>")
            output_file.write("</div>")
            result_number += 1
    
    output_file.write("</body></html>")
