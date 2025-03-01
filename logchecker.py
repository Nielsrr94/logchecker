import os
import datetime

# Define the keywords to search for
keywords = ["error", "fail", "warning"]

# Get the directory from the user
user_input = input("Enter the directory path to search for log files (or type 'here' to use the current directory): ")
if user_input.lower() == "here":
    current_directory = os.path.dirname(os.path.abspath(__file__))
else:
    current_directory = user_input

# Get the current timestamp
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

# Initialize a dictionary to keep track of keyword occurrences
keyword_counts = {keyword: 0 for keyword in keywords}

# Initialize a counter for the number of files checked
files_checked = 0

# Initialize a dictionary to keep track of keyword occurrences per file
file_keyword_counts = {}

# Iterate over all files in the current directory
for filename in os.listdir(current_directory):
    if filename.endswith(".txt") and "log" and "logcheck" not in filename:
        files_checked += 1
        file_keyword_counts[filename] = {keyword: [] for keyword in keywords}
        with open(os.path.join(current_directory, filename), 'r') as file:
            lines = file.readlines()
        
        for i, line in enumerate(lines):
            for keyword in keywords:
                if f" {keyword} " in line or line.startswith(f"{keyword} ") or line.endswith(f" {keyword}") or line == keyword:
                    keyword_counts[keyword] += 1
                    file_keyword_counts[filename][keyword].append((i + 1, line.strip()))

# Prepare the output file
output_filename = f"logcheck_{timestamp}.txt"
with open(os.path.join(current_directory, output_filename), 'w') as output_file:
    # Write the header
    output_file.write("="*40 + "\n")
    output_file.write(f"{'Log Check Report':^40}\n")
    output_file.write("="*40 + "\n")
    human_readable_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_file.write(f"{'Reported created:':<20}{human_readable_timestamp:>20}\n")
    output_file.write(f"{'Files Checked:':<20}{files_checked:>20}\n")
    output_file.write("="*40 + "\n\n")
    
    # Write the summary of keyword occurrences
    total_keywords_found = sum(keyword_counts.values())
    output_file.write("="*40 + "\n")
    output_file.write(f"{'Summary of Keyword Occurrences':^40}\n")
    output_file.write("="*40 + "\n")
    output_file.write(f"{'Total Keywords Found:':<30}{total_keywords_found:>10}\n")
    output_file.write("-"*40 + "\n")
    for keyword, count in keyword_counts.items():
        output_file.write(f"{'Keyword:':<20}{keyword:<10}{'Occurrences:':<10}{count:>5}\n")
    output_file.write("="*40 + "\n\n")
    
    # Write the results per logfile
    output_file.write("="*40 + "\n")
    output_file.write(f"{'Detailed Log File Analysis':^40}\n")
    output_file.write("="*40 + "\n\n")
    
    result_number = 1
    for filename, keywords_dict in file_keyword_counts.items():
        filepath = os.path.join(current_directory, filename)
        output_file.write("*"*40 + "\n")
        output_file.write(f"{'Result Number:':<15}{result_number}\n")
        output_file.write(f"{'File:':<10}{filepath}\n")
        output_file.write("-"*40 + "\n")
        for keyword, lines in keywords_dict.items():
            if lines:
                output_file.write(f"  {'Keyword:':<10}{keyword:<10}{'Occurrences:':<10}{len(lines):>5}\n")
                output_file.write("  " + "-"*38 + "\n")
                for line_num, line in lines:
                    output_file.write(f"    {'Line':<5}{line_num:<5}: {line}\n")
                output_file.write("  " + "-"*38 + "\n")
        output_file.write("="*40 + "\n\n")
        result_number += 1