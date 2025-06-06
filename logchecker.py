import os
import datetime
import zipfile
import json
import random
import time
import subprocess
import tkinter as tk
from tkinter import messagebox
import webbrowser
import csv

# Function to create a config file with example common phrases if it does not exist
def create_filenames_config(config_path):
    example_filenames = {
        "filenames": ["log", "error", "warning"]
    }
    with open(config_path, 'w') as config_file:
        json.dump(example_filenames, config_file, indent=4)

# Function to load common phrases from a config file
def load_filenames_from_config(config_path):
    if os.path.exists(config_path):
        with open(config_path, 'r') as config_file:
            config_data = json.load(config_file)
            return config_data.get("filenames", [])
    return []

# Function to create a config file with example keyphrases if it does not exist
def create_keyphrases_config(config_path):
    example_keyphrases = {
        "keyphrases": ["error occurred", "failed to start", "warning issued"]
    }
    with open(config_path, 'w') as config_file:
        json.dump(example_keyphrases, config_file, indent=4)

# Function to load keyphrases from a config file
def load_keyphrases_from_config(config_path):
    if os.path.exists(config_path):
        with open(config_path, 'r') as config_file:
            config_data = json.load(config_file)
            return config_data.get("keyphrases", [])
    return []

# Function to create a config file with example zip names if it does not exist
def create_zipnames_config(config_path):
    example_zipnames = {
        "zipnames": ["archive", "logs", "backup"]
    }
    with open(config_path, 'w') as config_file:
        json.dump(example_zipnames, config_file, indent=4)

# Function to load zip names from a config file
def load_zipnames_from_config(config_path):
    if os.path.exists(config_path):
        with open(config_path, 'r') as config_file:
            config_data = json.load(config_file)
            return config_data.get("zipnames", [])
    return []

# Function to generate a list of colors
def generate_colors(num_colors):
    colors = []
    for _ in range(num_colors):
        color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        colors.append(color)
    return colors

# Function to generate a list of colors in shades of red, orange, and yellow
def generate_highlight_colors(num_colors):
    colors = []
    for i in range(num_colors):
        hue = (i * 30) % 360  # Adjust the hue to get different shades
        color = f"hsl({hue}, 100%, 50%)"
        colors.append(color)
    return colors

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
        print("   *****Keyphrases found in logfile: ", unique_keyphrases)
    else:
        print("   *****No keyphrases found in logfile")
    print("-----------------------------------------------------------------------")


# Get the directory from the user
user_input = input("Enter the directory path to search for log files (the report will be generated in this path): ")
current_directory = os.path.dirname(os.path.abspath(__file__)) if user_input.strip() == "" else user_input

# Ask the user if they want to use a custom date range
use_custom_date_range = input("Do you want to use a custom date range for the search? (yes/no): ").strip().lower() == "yes"

if use_custom_date_range:
    while True:
        try:
            start_date_input = input("Enter the start date (YYYY-MM-DD): ").strip()
            end_date_input = input("Enter the end date (YYYY-MM-DD): ").strip()
            start_date = datetime.datetime.strptime(start_date_input, "%Y-%m-%d")
            end_date = datetime.datetime.strptime(end_date_input, "%Y-%m-%d")
            if start_date > end_date:
                print("Error: Start date cannot be after the end date. Please try again.")
                continue
            if end_date > datetime.datetime.now():
                print("Error: End date cannot be in the future. Please try again.")
                continue
            break
        except ValueError:
            print("Error: Invalid date format. Please use YYYY-MM-DD.")
else:
    start_date = None
    end_date = None

# Define the path to the config files in the script's directory
script_directory = os.path.dirname(os.path.abspath(__file__))
filenames_config_path = os.path.join(script_directory, "filenames_config.json")
keyphrases_config_path = os.path.join(script_directory, "keyphrases_config.json")
zipnames_config_path = os.path.join(script_directory, "zipnames_config.json")

# Create the config files with example values if they do not exist
if not os.path.exists(filenames_config_path):
    create_filenames_config(filenames_config_path)
if not os.path.exists(keyphrases_config_path):
    create_keyphrases_config(keyphrases_config_path)
if not os.path.exists(zipnames_config_path):
    create_zipnames_config(zipnames_config_path)

# Load common phrases and keyphrases from the config files
filenames = load_filenames_from_config(filenames_config_path)
zipnames = load_zipnames_from_config(zipnames_config_path)

# Ask the user if they want to use a custom keyphrase list
use_custom_keyphrases = input("Use custom keyphrase list instead of config file? (yes/no): ").strip().lower() == "yes"

if use_custom_keyphrases:
    custom_keyphrases = input("Enter custom keyphrases separated by commas: ").strip().split(',')
    keyphrases = [keyphrase.strip() for keyphrase in custom_keyphrases]
else:
    keyphrases = load_keyphrases_from_config(keyphrases_config_path)

# Generate colors for keyphrases
keyphrase_colors = {keyphrase: color for keyphrase, color in zip(keyphrases, generate_colors(len(keyphrases)))}

# Get the current timestamp
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

# Initialize dictionaries and counters
keyphrase_counts = {keyphrase: 0 for keyphrase in keyphrases}
file_keyphrase_counts = {}
files_checked = 0
files_with_keyphrases = 0

# Capture the start time
start_time = time.time()

# Print that the script is running
print("***********************************************************************")
print("* scanning for log files... This might take a while, please wait...   *")
print("* A pop-up will appear once the scan is completed.                    *")
print("***********************************************************************")
print()

# Iterate over all files in the current directory and subdirectories
for root, dirs, files in os.walk(current_directory):
    print ("fetching files from directory...")
    for filename in files:
        file_path = os.path.join(root, filename)
        if filename.endswith(".log") and any(phrase in filename for phrase in filenames) and "logcheck" not in filename:
            
            if start_date and end_date:
                print("scanning for logs in date range...")
                if " -> " in file_path:
                    zip_path, internal_file = file_path.split(" -> ")
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_info = next((info for info in zip_ref.infolist() if info.filename == internal_file), None)
                        if zip_info:
                            file_mod_time = datetime.datetime(*zip_info.date_time)
                        else:
                            continue
                else:
                    file_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                if start_date <= file_mod_time.replace(tzinfo=None) <= (end_date + datetime.timedelta(days=1)):
                    print("New Logfile found in date range! (",files_checked+1,")")
                    print("***** Filepath:", file_path)
                    print("***** Filename:", filename)
                    process_file(file_path)
            else:
                print("New Logfile found! (",files_checked+1,")")
                print("***** Filepath:", file_path)
                print("***** Filename:", filename)
                process_file(file_path)
        elif filename.endswith(".zip") and any(phrase in filename for phrase in zipnames):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                for zip_info in zip_ref.infolist():
                    if zip_info.filename.endswith(".log") and any(phrase in zip_info.filename for phrase in filenames)and "logcheck" not in filename:
                        if start_date and end_date:
                            print("scanning for logs in date range...")
                            file_mod_time = datetime.datetime(*zip_info.date_time)
                            if start_date <= file_mod_time.replace(tzinfo=None) <= (end_date + datetime.timedelta(days=1)):
                                print("New Logfile found in date range! (",files_checked+1,")")
                                print("***** Filepath:", file_path)
                                print("***** Filename:", zip_info.filename)
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
                                        print("***** Keyphrases found! -  ",unique_keyphrases)
                                    else:
                                        print("***** No Keyprhases found.")
                                    print("-----------------------------------------------------------------------")
                                            
                        else:
                            print("New Logfile found! (",files_checked+1,")")
                            print("***** Filepath:", file_path)
                            print("***** Filename:", zip_info.filename)
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
                                    print("***** Keyphrases found! - ",unique_keyphrases)
                                else:
                                    print("***** No Keyprhases found.")
                                print("-----------------------------------------------------------------------")

# Calculate total keyphrases found
total_keyphrases_found = sum(keyphrase_counts.values())

# Calculate percentages
percentage_files_with_keyphrases = (files_with_keyphrases / files_checked) * 100 if files_checked > 0 else 0
keyphrase_percentages = {keyphrase: (count / files_checked) * 100 if files_checked > 0 else 0 for keyphrase, count in keyphrase_counts.items()}

# Prepare the output file
output_filename_html = f"logcheck_{timestamp}.html"

# Generate colors for keyphrases in shades of red, orange, and yellow
keyphrase_colors = {keyphrase: color for keyphrase, color in zip(keyphrases, generate_highlight_colors(len(keyphrases)))}

# Calculate the duration of the analysis
end_time = time.time()
duration = end_time - start_time
hours, remainder = divmod(duration, 3600)
minutes, seconds = divmod(remainder, 60)

# Write to the HTML file
html_file_path = os.path.join(current_directory, output_filename_html)
with open(html_file_path, 'w') as output_file:
    # Write the header
    output_file.write("<html><head><title>Log Check Report</title>")
    output_file.write("""
    <style>
        body { background-color: #121212; color: #e0e0e0; font-family: Arial, sans-serif; }
        .collapsible { background-color: #333; color: #e0e0e0; cursor: pointer; padding: 10px; width: 100%; border: none; text-align: left; outline: none; font-size: 15px; }
        .active, .collapsible:hover { background-color: #555; }
        .content { padding: 0 18px; display: none; overflow: hidden; background-color: #1e1e1e; }
        .highlight { background-color: #444; }
        a { color: #1e90ff; }
        .watermark { position: fixed; bottom: 10px; right: 10px; color: #555; font-size: 12px; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .header-title { flex-grow: 1; text-align: left; }
        @media print {
            body { background-color: #ffffff; color: #000000; }
            .collapsible, .watermark, button { display: none; }
            h1, h2 { page-break-after: avoid; }
            .content { display: block !important; } /* Ensure expanded view is printed */
        }
    </style>
    <script>
        function toggleSection(sectionClass, buttonId) {
            var contents = document.getElementsByClassName(sectionClass);
            var allExpanded = true;
            for (var i = 0; i < contents.length; i++) {
                if (contents[i].style.display !== "block") {
                    allExpanded = false;
                    break;
                }
            }
            var expand = !allExpanded;
            for (var i = 0; i < contents.length; i++) {
                contents[i].style.display = expand ? "block" : "none";
            }
            document.getElementById(buttonId).innerText = expand ? "Collapse All" : "Expand All";
        }

        function exportToPDF() {
            // Expand all sections before printing
            var contents = document.getElementsByClassName("content");
            for (var i = 0; i < contents.length; i++) {
                contents[i].style.display = "block";
            }
            window.print();
        }

        document.addEventListener("DOMContentLoaded", function() {
            var coll = document.getElementsByClassName("collapsible");
            for (var i = 0; i < coll.length; i++) {
                coll[i].addEventListener("click", function() {
                    this.classList.toggle("active");
                    var content = this.nextElementSibling;
                    content.style.display = content.style.display === "block" ? "none" : "block";
                });
            }
        });
    </script>
    </head><body>
    """)

    output_file.write("<div class='header'>")
    output_file.write("<h1 class='header-title' style='color:#ffffff;'>Log Check Report</h1>")
    output_file.write("<button onclick='exportToPDF()' style='background-color:#1e90ff; color:#ffffff; border:none; padding:10px; cursor:pointer;'>Export to PDF</button>")
    output_file.write("</div>")

    report_status = "PASSED" if total_keyphrases_found == 0 else "FAILED"
    report_status_color = "#00ff00" if total_keyphrases_found == 0 else "#ff0000"
    output_file.write(f"<h2 style='text-align:left; color:#ffffff; page-break-after: avoid;'>Verdict: <span style='color:{report_status_color};'>{report_status}</span></h2>")

    # Write the metadata section
    output_file.write("<button class='collapsible'>Metadata</button>")
    output_file.write("<div class='content metadata-content'>")
    human_readable_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    milliseconds = int((duration - int(duration)) * 1000)
    output_file.write(f"<p><strong>Report created:</strong> {human_readable_timestamp}</p>")
    output_file.write(f"<p><strong>Analysis duration:</strong> {int(hours):02}:{int(minutes):02}:{int(seconds):02}.{milliseconds:03}</p>")
    output_file.write(f"<p><strong>Logchecker file used:</strong> <a href='file:///{os.path.abspath(__file__)}'>{os.path.abspath(__file__)}</a></p>")
    output_file.write(f"<p><strong>Directory checked:</strong> <a href='file:///{current_directory}'>{current_directory}</a></p>")
    if start_date and end_date:
        output_file.write(f"<p><strong>Date range checked:</strong> {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}</p>")
    else:
        output_file.write(f"<p><strong>Date range checked:</strong> <= {datetime.datetime.now().strftime('%Y-%m-%d')}</p>")
    output_file.write(f"<p><strong>Filename config used:</strong> <a href='file:///{filenames_config_path}'>{filenames_config_path}</a></p>")
    keyphrase_config_used = 'Custom keyphrases entered by user' if use_custom_keyphrases else f"<a href='file:///{keyphrases_config_path}'>{keyphrases_config_path}</a>"
    output_file.write(f"<p><strong>Keyphrase config used:</strong> {keyphrase_config_used}</p>")
    output_file.write(f"<p><strong>Keyphrases checked:</strong> {', '.join(keyphrases)}</p>")
    
    # Add a list of all file paths checked
    output_file.write(f"<p><strong>Files checked:</strong> ({files_checked})</p>")
    output_file.write("<ul>")
    for file_path in file_keyphrase_counts.keys():
        output_file.write(f"<li><a href='file:///{file_path}'>{file_path}</a></li>")
    output_file.write("</ul>")
    
    output_file.write("</div>")
    output_file.write("<hr>")

    # Write the summary of keyphrase occurrences
    total_keyphrases_found = sum(keyphrase_counts.values())
    unique_keyphrases_found = sum(1 for count in keyphrase_counts.values() if count > 0)
    output_file.write("<h2 style='color:#00ff00;'>Summary of Keyphrase Occurrences</h2>")
    output_file.write(f"<p><strong>Files Checked:</strong> {files_checked}</p>")
    output_file.write(f"<p><strong>Files with Keyphrases:</strong> {files_with_keyphrases} ({percentage_files_with_keyphrases:.2f}%)</p>")
    output_file.write(f"<p><strong>Unique Keyphrases Found:</strong> {unique_keyphrases_found}/{len(keyphrases)}</p>")
    output_file.write("<ul>")

    # Sort keyphrases by occurrence count in descending order
    sorted_keyphrases = sorted(keyphrase_counts.items(), key=lambda item: item[1], reverse=True)

    for keyphrase, count in sorted_keyphrases:
        output_file.write(f"<li><strong>Keyphrase:</strong> <span style='color:{keyphrase_colors[keyphrase]};'>{keyphrase}</span> - <strong>Files:</strong> {count} ({keyphrase_percentages[keyphrase]:.2f}%)</li>")
        
        # Find the file with the most occurrences of this keyphrase
        max_occurrences = 0
        file_with_most_occurrences = None
        for file_path, keyphrases_dict in file_keyphrase_counts.items():
            if keyphrase in keyphrases_dict:
                # Check if the file is within the date range
                if start_date and end_date:
                    try:
                        if " -> " in file_path:
                            # Handle zip files
                            zip_path, internal_file = file_path.split(" -> ")
                            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                                zip_info = next((info for info in zip_ref.infolist() if info.filename == internal_file), None)
                                if zip_info:
                                    file_mod_time = datetime.datetime(*zip_info.date_time)
                                else:
                                    continue
                        else:
                            # Handle regular files
                            file_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                        
                        if not (start_date <= file_mod_time <= end_date):
                            continue
                    except Exception as e:
                        print(f"Error processing file modification time for {file_path}: {e}")
                        continue
                occurrences = len(keyphrases_dict[keyphrase])
                if occurrences > max_occurrences:
                    max_occurrences = occurrences
                    file_with_most_occurrences = file_path

        if file_with_most_occurrences:
            output_file.write(f"<p><strong>File with most occurrences:</strong> <a href='file:///{file_with_most_occurrences}'>{file_with_most_occurrences}</a> ({max_occurrences} occurrences)</p>")
            
            # Print 20 lines before and after the keyphrase for the first occurrence
            lines_to_display = 20
            if keyphrase in file_keyphrase_counts[file_with_most_occurrences]:
                occurrences = file_keyphrase_counts[file_with_most_occurrences][keyphrase]
                if occurrences:
                    first_occurrence_line = occurrences[0][0]  # Line number of the first occurrence
                    if " -> " in file_with_most_occurrences:
                        # Handle zip files
                        zip_path, internal_file = file_with_most_occurrences.split(" -> ")
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            with zip_ref.open(internal_file) as file:
                                all_lines = file.readlines()
                                all_lines = [line.decode('utf-8').strip() for line in all_lines]
                                start_line = max(0, first_occurrence_line - lines_to_display - 1)
                                end_line = min(len(all_lines), first_occurrence_line + lines_to_display)
                                
                                # Make the block collapsible
                                output_file.write("<button class='collapsible'>View Context (20 lines before and after)</button>")
                                output_file.write("<div class='content'>")
                                output_file.write("<pre style='background-color:#1e1e1e; color:#e0e0e0; padding:10px;'>")
                                for i in range(start_line, end_line):
                                    line_content = all_lines[i]
                                    if keyphrase in line_content:
                                        highlighted_line = line_content.replace(keyphrase, f"<span style='color:{keyphrase_colors[keyphrase]};'>{keyphrase}</span>")
                                        output_file.write(f"<strong>Line {i + 1}:</strong> {highlighted_line}<br>")
                                    else:
                                        output_file.write(f"Line {i + 1}: {line_content}<br>")
                                output_file.write("</pre>")
                                output_file.write("</div>")
                    else:
                        # Handle regular files
                        with open(file_with_most_occurrences, 'r') as file:
                            all_lines = file.readlines()
                            start_line = max(0, first_occurrence_line - lines_to_display - 1)
                            end_line = min(len(all_lines), first_occurrence_line + lines_to_display)
                            
                            # Make the block collapsible
                            output_file.write("<button class='collapsible'>View Context (20 lines before and after)</button>")
                            output_file.write("<div class='content'>")
                            output_file.write("<pre style='background-color:#1e1e1e; color:#e0e0e0; padding:10px;'>")
                            for i in range(start_line, end_line):
                                line_content = all_lines[i].strip()
                                if keyphrase in line_content:
                                    highlighted_line = line_content.replace(keyphrase, f"<span style='color:{keyphrase_colors[keyphrase]};'>{keyphrase}</span>")
                                    output_file.write(f"<strong>Line {i + 1}:</strong> {highlighted_line}<br>")
                                else:
                                    output_file.write(f"Line {i + 1}: {line_content}<br>")
                            output_file.write("</pre>")
                            output_file.write("</div>")
        # Add a spacer between results for each keyphrase
        output_file.write("<hr style='border: 1px solid #555;'>")
    output_file.write("</ul>")
    output_file.write("<hr>")

    # Write the results per logfile
    output_file.write("<div class='analysis-title'>")
    output_file.write("<h2 style='color:#00ff00;'>Detailed Log File Analysis</h2>")
    output_file.write("</div>")
    output_file.write("<button id='detailedToggle' onclick='toggleSection(\"detailed-content\", \"detailedToggle\")'>Expand All</button>")

    result_number = 1
    for file_path, keyphrases_dict in file_keyphrase_counts.items():
        if any(len(lines) > 0 for lines in keyphrases_dict.values()):
            keyphrases_found = [keyphrase for keyphrase, lines in keyphrases_dict.items() if lines]
            keyphrases_summary = " - ".join([f"<span style='color:{keyphrase_colors[keyphrase]};'>{keyphrase}</span>" for keyphrase in keyphrases_found])
            background_color = "#444" if result_number % 2 == 0 else "#555"
            output_file.write(f"<button class='collapsible' style='background-color:{background_color};'>Logfile #{result_number} - Keyphrases: {keyphrases_summary}</button>")
            output_file.write("<div class='content detailed-content'>")
            output_file.write(f"<h3>Detailed Results for Logfile #{result_number}</h3>")
            if " -> " in file_path:
                zip_path, internal_file = file_path.split(" -> ")
                output_file.write(f"<p><strong>File:</strong> <a href='file:///{zip_path}'>{zip_path}</a> -> {internal_file}</p>")
            else:
                output_file.write(f"<p><strong>File:</strong> <a href='file:///{file_path}'>{file_path}</a></p>")
            for keyphrase, lines in keyphrases_dict.items():
                if lines:
                    output_file.write(f"<p><strong>Keyphrase:</strong> {keyphrase} - <strong>Occurrences:</strong> {len(lines)}</p>")
                    output_file.write("<ul>")
                    for line_num, line in lines:
                        highlighted_line = line.replace(keyphrase, f"<span style='color:{keyphrase_colors[keyphrase]};'>{keyphrase}</span>")
                        output_file.write(f"<li><strong>Line {line_num}:</strong> {highlighted_line}</li>")
                    output_file.write("</ul>")
            output_file.write("</div>")
            result_number += 1

    output_file.write(f"<div class='watermark'>Log Checker | Niels Dobbelaar | EF-465 </div>")
    output_file.write("</body></html>")

    # Write a simple JSON file with keyphrases and the files they were found in
    output_filename_json = f"logcheck_{timestamp}.json"
    json_file_path = os.path.join(current_directory, output_filename_json)

    keyphrase_summary = {}
    for keyphrase, count in keyphrase_counts.items():
        if count > 0:  # Only include keyphrases that were actually found
            keyphrase_summary[keyphrase] = []
            for file_path, keyphrases_dict in file_keyphrase_counts.items():
                if keyphrase in keyphrases_dict and keyphrases_dict[keyphrase]:
                    keyphrase_summary[keyphrase].append(file_path)

    with open(json_file_path, 'w') as json_file:
        json.dump(keyphrase_summary, json_file, indent=4)

def show_popup():
    def open_report():
        webbrowser.open(f"file:///{os.path.join(current_directory, output_filename_html)}")
        root.destroy()
        exit()

    def close_popup():
        root.destroy()
        exit()

    root = tk.Tk()
    root.withdraw()

    popup = tk.Toplevel(root)
    popup.title("Log Checker")
    popup.geometry("300x150")

    popup.update_idletasks()
    width = popup.winfo_width()
    height = popup.winfo_height()
    x = (popup.winfo_screenwidth() // 2) - (width // 2)
    y = (popup.winfo_screenheight() // 2) - (height // 2)
    popup.geometry(f'{300}x{150}+{x}+{y}')

    popup.attributes('-topmost', True)
    popup.after_idle(popup.attributes, '-topmost', False)

    label = tk.Label(popup, text="Log check completed!", font=("Segoe UI", 10))
    label.pack(pady=10)

    verdict_label = tk.Label(popup, text=f" {'No keyphrases found!' if total_keyphrases_found == 0 else 'Keyphrases found!'}", font=("Segoe UI", 10), fg="#00ff00" if total_keyphrases_found == 0 else "#ff0000")
    verdict_label.pack(pady=5)

    button_frame = tk.Frame(popup)
    button_frame.pack(pady=5)

    open_button = tk.Button(button_frame, text="Open Report", command=open_report, font=("Segoe UI", 9), width=10)
    open_button.pack(side=tk.LEFT, padx=5)

    ok_button = tk.Button(button_frame, text="Close", command=close_popup, font=("Segoe UI", 9), width=10)
    ok_button.pack(side=tk.RIGHT, padx=5)

    root.bell()
    root.mainloop()
print()
print("***********************************************************************")
print("*                      logcheck completed!                            *")
print("***********************************************************************")
show_popup()
