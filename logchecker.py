import os
import datetime
import zipfile

# Define the keyphrases to search for
keyphrases = ["error occurred", "failed to start", "warning issued"]

# Get the directory from the user
user_input = input("Enter the directory path to search for log files (or type 'here' to use the current directory): ")
current_directory = os.path.dirname(os.path.abspath(__file__)) if user_input.lower() == "here" else user_input

# Get the current timestamp
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

# Initialize dictionaries and counters
keyphrase_counts = {keyphrase: 0 for keyphrase in keyphrases}
file_keyphrase_counts = {}
files_checked = 0
files_with_keyphrases = 0

# Function to process a file
def process_file(file_path):
    global files_checked, files_with_keyphrases
    files_checked += 1
    file_keyphrase_counts[file_path] = {keyphrase: [] for keyphrase in keyphrases}
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    file_has_keyphrases = False
    unique_keyphrases = set()
    for i, line in enumerate(lines):
        for keyphrase in keyphrases:
            if keyphrase in line:
                if keyphrase not in unique_keyphrases:
                    keyphrase_counts[keyphrase] += 1
                file_keyphrase_counts[file_path][keyphrase].append((i + 1, line.strip()))
                file_has_keyphrases = True
                unique_keyphrases.add(keyphrase)
    
    if file_has_keyphrases:
        files_with_keyphrases += 1

# Iterate over all files in the current directory and subdirectories
for root, dirs, files in os.walk(current_directory):
    for filename in files:
        file_path = os.path.join(root, filename)
        if filename.endswith(".txt") and "log" and "logcheck" not in filename:
            process_file(file_path)
        elif filename.endswith(".zip"):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                for zip_info in zip_ref.infolist():
                    if zip_info.filename.endswith(".txt"):
                        with zip_ref.open(zip_info) as file:
                            lines = file.readlines()
                            files_checked += 1
                            internal_file_path = f"{file_path} -> {zip_info.filename}"
                            file_keyphrase_counts[internal_file_path] = {keyphrase: [] for keyphrase in keyphrases}
                            file_has_keyphrases = False
                            unique_keyphrases = set()
                            for i, line in enumerate(lines):
                                line = line.decode('utf-8')
                                for keyphrase in keyphrases:
                                    if keyphrase in line:
                                        if keyphrase not in unique_keyphrases:
                                            keyphrase_counts[keyphrase] += 1
                                        file_keyphrase_counts[internal_file_path][keyphrase].append((i + 1, line.strip()))
                                        file_has_keyphrases = True
                                        unique_keyphrases.add(keyphrase)
                            if file_has_keyphrases:
                                files_with_keyphrases += 1

# Calculate percentages
percentage_files_with_keyphrases = (files_with_keyphrases / files_checked) * 100 if files_checked > 0 else 0
keyphrase_percentages = {keyphrase: (count / files_checked) * 100 if files_checked > 0 else 0 for keyphrase, count in keyphrase_counts.items()}

# Prepare the output file
output_filename_txt = f"logcheck_{timestamp}.txt"
output_filename_html = f"logcheck_{timestamp}.html"

# Write to the text file
with open(os.path.join(current_directory, output_filename_txt), 'w') as output_file:
    # Write the header
    header = "Log Check Report"
    output_file.write("="*100 + "\n")
    output_file.write(f"{header:^{100}}\n")
    output_file.write("="*100 + "\n")
    human_readable_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_file.write(f"{'Report created:':<50}{human_readable_timestamp:>50}\n")
    output_file.write("="*100 + "\n\n")
    
    # Write the summary of keyphrase occurrences
    total_keyphrases_found = sum(keyphrase_counts.values())
    unique_keyphrases_found = sum(1 for count in keyphrase_counts.values() if count > 0)
    summary_header = "Summary of Keyphrase Occurrences"
    output_file.write("="*100 + "\n")
    output_file.write(f"{summary_header:^{100}}\n")
    output_file.write("="*100 + "\n")
    output_file.write(f"{'Files Checked:':<50}{files_checked:>50}\n")
    output_file.write(f"{'Total Keyphrases Found:':<50}{total_keyphrases_found:>50}\n")
    output_file.write(f"{'Unique Keyphrases Found:':<50}{unique_keyphrases_found:>50}\n")
    files_with_keyphrases_str = f"{files_with_keyphrases} ({percentage_files_with_keyphrases:.2f}%)"
    output_file.write(f"{'Files with Keyphrases:':<50}{files_with_keyphrases_str:>50}\n")
    output_file.write("-"*100 + "\n")
    for keyphrase, count in keyphrase_counts.items():
        keyphrase_str = f"{'Keyphrase:':<25}{keyphrase:<50}{'Files:'}{count:>10} ({keyphrase_percentages[keyphrase]:.2f}%)"
        output_file.write(f"{keyphrase_str:<100}\n")
        # Add the first file link for each keyphrase
        for file_path, keyphrases_dict in file_keyphrase_counts.items():
            if keyphrase in keyphrases_dict and keyphrases_dict[keyphrase]:
                output_file.write(f"{'First occurrence in file:':<25}{file_path}\n")
                break
        output_file.write("\n")
    output_file.write("="*100 + "\n\n")
    
    # Write the results per logfile
    detailed_header = "Detailed Log File Analysis"
    output_file.write("="*100 + "\n")
    output_file.write(f"{detailed_header:^{100}}\n")
    output_file.write("="*100 + "\n\n")
    
    result_number = 1
    for file_path, keyphrases_dict in file_keyphrase_counts.items():
        if any(len(lines) > 0 for lines in keyphrases_dict.values()):
            output_file.write("*"*100 + "\n")
            output_file.write(f"{'Result Number:':<25}{result_number}\n")
            output_file.write(f"{'File:':<15}{file_path}\n")
            output_file.write("-"*100 + "\n")
            # Add summary of which keywords were found
            found_keyphrases = [keyphrase for keyphrase, lines in keyphrases_dict.items() if lines]
            output_file.write(f"{'Keyphrases Found:':<25}{', '.join(found_keyphrases)}\n")
            output_file.write("-"*100 + "\n")
            for keyphrase, lines in keyphrases_dict.items():
                if lines:
                    keyphrase_header = f"  {'Keyphrase:':<25}{keyphrase:<50}{'Occurrences:':<15}{len(lines):>10}"
                    output_file.write(f"{keyphrase_header:<100}\n")
                    output_file.write("  " + "-"*48 + "\n")
                    for line_num, line in lines:
                        truncated_line = (line[:90] + '...') if len(line) > 90 else line
                        output_file.write(f"    {'Line':<5}{line_num:<5}: {truncated_line}\n")
                    output_file.write("  " + "-"*48 + "\n")
            output_file.write("="*100 + "\n\n")
            result_number += 1

# Write to the HTML file
with open(os.path.join(current_directory, output_filename_html), 'w') as output_file:
    # Write the header
    output_file.write("<html><head><title>Log Check Report</title></head><body>")
    output_file.write("<h1 style='text-align:center; color:blue;'>Log Check Report</h1>")
    human_readable_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_file.write(f"<p><strong>Report created:</strong> {human_readable_timestamp}</p>")
    output_file.write("<hr>")
    
    # Write the summary of keyphrase occurrences
    total_keyphrases_found = sum(keyphrase_counts.values())
    unique_keyphrases_found = sum(1 for count in keyphrase_counts.values() if count > 0)
    output_file.write("<h2 style='color:green;'>Summary of Keyphrase Occurrences</h2>")
    output_file.write(f"<p><strong>Files Checked:</strong> {files_checked}</p>")
    output_file.write(f"<p><strong>Total Keyphrases Found:</strong> {total_keyphrases_found}</p>")
    output_file.write(f"<p><strong>Unique Keyphrases Found:</strong> {unique_keyphrases_found}</p>")
    output_file.write(f"<p><strong>Files with Keyphrases:</strong> {files_with_keyphrases} ({percentage_files_with_keyphrases:.2f}%)</p>")
    output_file.write("<ul>")
    for keyphrase, count in keyphrase_counts.items():
        output_file.write(f"<li><strong>Keyphrase:</strong> {keyphrase} - <strong>Files:</strong> {count} ({keyphrase_percentages[keyphrase]:.2f}%)</li>")
        # Add the first file link for each keyphrase
        for file_path, keyphrases_dict in file_keyphrase_counts.items():
            if keyphrase in keyphrases_dict and keyphrases_dict[keyphrase]:
                if " -> " in file_path:
                    zip_path, internal_file = file_path.split(" -> ")
                    output_file.write(f"<li><strong>First occurrence in file:</strong> <a href='file:///{zip_path}'>{zip_path}</a> -> {internal_file}</li>")
                else:
                    output_file.write(f"<li><strong>First occurrence in file:</strong> <a href='file:///{file_path}'>{file_path}</a></li>")
                break
        output_file.write("<br>")
    output_file.write("</ul>")
    output_file.write("<hr>")
    
    # Write the results per logfile
    output_file.write("<h2 style='color:green;'>Detailed Log File Analysis</h2>")
    
    result_number = 1
    for file_path, keyphrases_dict in file_keyphrase_counts.items():
        if any(len(lines) > 0 for lines in keyphrases_dict.values()):
            output_file.write("<div style='border:1px solid #000; padding:10px; margin-bottom:10px;'>")
            output_file.write(f"<h3 style='color:blue;'>Result Number: {result_number}</h3>")
            if " -> " in file_path:
                zip_path, internal_file = file_path.split(" -> ")
                output_file.write(f"<p><strong>File:</strong> <a href='file:///{zip_path}'>{zip_path}</a> -> {internal_file}</p>")
            else:
                output_file.write(f"<p><strong>File:</strong> <a href='file:///{file_path}'>{file_path}</a></p>")
            # Add summary of which keywords were found
            found_keyphrases = [keyphrase for keyphrase, lines in keyphrases_dict.items() if lines]
            output_file.write(f"<p><strong>Keyphrases Found:</strong> {', '.join(found_keyphrases)}</p>")
            for keyphrase, lines in keyphrases_dict.items():
                if lines:
                    output_file.write(f"<p><strong>Keyphrase:</strong> {keyphrase} - <strong>Occurrences:</strong> {len(lines)}</p>")
                    output_file.write("<ul>")
                    for line_num, line in lines:
                        highlighted_line = line.replace(keyphrase, f"<span style='color:red;'>{keyphrase}</span>")
                        output_file.write(f"<li><strong>Line {line_num}:</strong> {highlighted_line}</li>")
                    output_file.write("</ul>")
            output_file.write("</div>")
            result_number += 1
    
    output_file.write("</body></html>")
