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

# Get the directory from the user
user_input = input("Enter the directory path to search for log files (the report will be generated in this path): ")
current_directory = os.path.dirname(os.path.abspath(__file__)) if user_input.strip() == "" else user_input

# Ask the user if they want to use a custom date range
use_custom_date_range = input("Do you want to use a custom date range for the search? (yes/no): ").strip().lower() == "yes"

if use_custom_date_range:
    start_date_input = input("Enter the start date (YYYY-MM-DD): ")
    end_date_input = input("Enter the end date (YYYY-MM-DD): ")
    try:
        start_date = datetime.datetime.strptime(start_date_input, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date_input, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        exit()
else:
    start_date = None
    end_date = None

# Define the path to the config files in the script's directory
script_directory = os.path.dirname(os.path.abspath(__file__))
filenames_config_path = os.path.join(script_directory, "filenames_config.json")
keyphrases_config_path = os.path.join(script_directory, "keyphrases_config.json")

# Create the config files with example values if they do not exist
if not os.path.exists(filenames_config_path):
    create_filenames_config(filenames_config_path)
if not os.path.exists(keyphrases_config_path):
    create_keyphrases_config(keyphrases_config_path)

# Load common phrases and keyphrases from the config files
filenames = load_filenames_from_config(filenames_config_path)

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
print("Scanning Logs for keyphrases (a pop-up will appear once completed)...")

# Iterate over all files in the current directory and subdirectories
for root, dirs, files in os.walk(current_directory):
    for filename in files:
        file_path = os.path.join(root, filename)
        if filename.endswith(".log") and any(phrase in filename for phrase in filenames) and "logcheck" not in filename:
            if start_date and end_date:
                file_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                if start_date <= file_mod_time <= end_date:
                    process_file(file_path)
            else:
                process_file(file_path)
        elif filename.endswith(".zip"):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                for zip_info in zip_ref.infolist():
                    if zip_info.filename.endswith(".log") and any(phrase in zip_info.filename for phrase in filenames):
                        if start_date and end_date:
                            file_mod_time = datetime.datetime(*zip_info.date_time)
                            if start_date <= file_mod_time <= end_date:
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
                        else:
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
        .content { padding: 0 18px; display: block; overflow: hidden; background-color: #1e1e1e; } /* Changed display to block */
        .highlight { background-color: #444; }
        a { color: #1e90ff; }
        .watermark { position: fixed; bottom: 10px; right: 10px; color: #555; font-size: 12px; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .header-title { flex-grow: 1; text-align: left; }
        @media print {
            body { background-color: #ffffff; color: #000000; }
            .collapsible, .watermark, button { display: none; }
            h1, h2 { page-break-after: avoid; }
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
                contents[i].style.display = expand ? "block" : "block"; /* Ensures all fields are visible */
            }
            document.getElementById(buttonId).innerText = expand ? "Collapse All" : "Expand All";
        }

        function exportToPDF() {
            window.print();
        }

        document.addEventListener("DOMContentLoaded", function() {
            var coll = document.getElementsByClassName("collapsible");
            for (var i = 0; i < coll.length; i++) {
                coll[i].addEventListener("click", function() {
                    this.classList.toggle("active");
                    var content = this.nextElementSibling;
                    content.style.display = content.style.display === "block" ? "block" : "block"; /* Ensures visibility */
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
        # Add the file link with the most occurrences for each keyphrase
        max_occurrences = 0
        max_occurrence_file = None
        for file_path, keyphrases_dict in file_keyphrase_counts.items():
            if keyphrase in keyphrases_dict and len(keyphrases_dict[keyphrase]) > max_occurrences:
                max_occurrences = len(keyphrases_dict[keyphrase])
                max_occurrence_file = file_path
        if max_occurrence_file:
            if " -> " in max_occurrence_file:
                zip_path, internal_file = max_occurrence_file.split(" -> ")
                output_file.write(f"<li><strong>File with most occurrences:</strong> <a href='file:///{zip_path}'>{zip_path}</a> -> {internal_file}</li>")
            else:
                output_file.write(f"<li><strong>File with most occurrences:</strong> <a href='file:///{max_occurrence_file}'>{max_occurrence_file}</a></li>")
        output_file.write("<br>")
    output_file.write("</ul>")
    output_file.write("<hr>")

    # Write the results per logfile
    output_file.write("<div class='analysis-title'>")
    output_file.write("<h2 style='color:#00ff00;'>Detailed Log File Analysis</h2>")
    output_file.write("</div>")
    output_file.write("<button id='detailedToggle' onclick='toggleSection(\"detailed-content\", \"detailedToggle\")'>Expand All</button>")

    result_number = 1
    max_occurrences = {keyphrase: 0 for keyphrase in keyphrases}
    max_occurrence_result = {keyphrase: None for keyphrase in keyphrases}

    for file_path, keyphrases_dict in file_keyphrase_counts.items():
        if any(len(lines) > 0 for lines in keyphrases_dict.values()):
            keyphrases_found = [keyphrase for keyphrase, lines in keyphrases_dict.items() if lines]
            keyphrases_summary = " - ".join([f"<span style='color:{keyphrase_colors[keyphrase]};'>{keyphrase}</span>" for keyphrase in keyphrases_found])
            most_frequent_keyphrase = max(keyphrases_dict, key=lambda k: len(keyphrases_dict[k]))
            keyphrases_summary = keyphrases_summary.replace(f"<span style='color:{keyphrase_colors[most_frequent_keyphrase]};'>{most_frequent_keyphrase}</span>", f"<strong><span style='color:{keyphrase_colors[most_frequent_keyphrase]};'>{most_frequent_keyphrase}</span></strong>")
            background_color = "#444" if result_number % 2 == 0 else "#555"
            output_file.write(f"<button class='collapsible' style='background-color:{background_color};'>Logfile #{result_number} - Keyphrases: {keyphrases_summary}</button>")
            output_file.write("<div class='content detailed-content'>")
            output_file.write(f"<h3>Detailed Results for Logfile #{result_number}</h3>")  # Add title for individual detailed results
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
                        highlighted_line = line.replace(keyphrase, f"<span style='color:{keyphrase_colors[keyphrase]};'>{keyphrase}</span>")
                        output_file.write(f"<li><strong>Line {line_num}:</strong> {highlighted_line}</li>")
                    output_file.write("</ul>")
                    if len(lines) > max_occurrences[keyphrase]:
                        max_occurrences[keyphrase] = len(lines)
                        max_occurrence_result[keyphrase] = result_number
            output_file.write("</div>")
            result_number += 1

    try:
        version = subprocess.check_output(["git", "describe", "--tags"], cwd=script_directory).strip().decode()
    except Exception:
        version = f"Branch: {subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=script_directory).strip().decode()}, Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    output_file.write(f"<div class='watermark'>Log Checker - by Niels Dobbelaar, EF-465 - Version {version}</div>")
    output_file.write("</body></html>")

def show_popup():
    def open_report():
        webbrowser.open(f"file:///{os.path.join(current_directory, output_filename_html)}")
        root.destroy()
        exit()  # Stop the script after showing the popup

    def close_popup():
        root.destroy()
        exit()  # Stop the script after showing the popup

    root = tk.Tk()
    root.withdraw()  # Hide the root window

    popup = tk.Toplevel(root)
    popup.title("Log Checker")
    popup.geometry("300x150")

    # Center the popup window
    popup.update_idletasks()
    width = popup.winfo_width()
    height = popup.winfo_height()
    x = (popup.winfo_screenwidth() // 2) - (width // 2)
    y = (popup.winfo_screenheight() // 2) - (height // 2)
    popup.geometry(f'{300}x{150}+{x}+{y}')

    # Bring the popup window to the front
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

    # Play a positive alert sound
    root.bell()

    root.mainloop()

show_popup()
