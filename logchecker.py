import os
import datetime
import zipfile
import json
import random

# Function to create a config file with example keyphrases if it does not exist
def create_config_file_with_examples(config_path):
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
user_input = input("Enter the directory path to search for log files (or press Enter to use the current directory): ")
current_directory = os.path.dirname(os.path.abspath(__file__)) if user_input.strip() == "" else user_input

# Get the common phrase from the user
common_phrase = ""
while not common_phrase:
    common_phrase = input("Enter the common phrase included in the log files: ").strip()
    if not common_phrase:
        print("Common phrase cannot be empty. Please enter a valid common phrase.")

# Define the path to the config file
config_file_path = os.path.join(current_directory, "keyphrases_config.json")

# Create the config file with example keyphrases if it does not exist
if not os.path.exists(config_file_path):
    create_config_file_with_examples(config_file_path)

# Ask the user if they want to use the config file or enter keyphrases manually
use_config = input("Do you want enter a custom list of keyphrases instead of using the config file? (yes/no): ").strip().lower()

if use_config == "yes":
    keyphrases_input = input("Enter the keyphrases to search for, separated by commas: ")
    keyphrases = [phrase.strip() for phrase in keyphrases_input.split(",")]
else:
    keyphrases = load_keyphrases_from_config(config_file_path)

# Generate colors for keyphrases
keyphrase_colors = {keyphrase: color for keyphrase, color in zip(keyphrases, generate_colors(len(keyphrases)))}

# Get the current timestamp
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

# Initialize dictionaries and counters
keyphrase_counts = {keyphrase: 0 for keyphrase in keyphrases}
file_keyphrase_counts = {}
files_checked = 0
files_with_keyphrases = 0

# Iterate over all files in the current directory and subdirectories
for root, dirs, files in os.walk(current_directory):
    for filename in files:
        file_path = os.path.join(root, filename)
        if filename.endswith(".txt") and common_phrase in filename and "logcheck" not in filename:
            process_file(file_path)
        elif filename.endswith(".zip"):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                for zip_info in zip_ref.infolist():
                    if zip_info.filename.endswith(".txt") and common_phrase in zip_info.filename:
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
output_filename_txt = f"logcheck_{timestamp}.txt"
output_filename_html = f"logcheck_{timestamp}.html"

# Generate colors for keyphrases in shades of red, orange, and yellow
keyphrase_colors = {keyphrase: color for keyphrase, color in zip(keyphrases, generate_highlight_colors(len(keyphrases)))}

# Write to the HTML file
with open(os.path.join(current_directory, output_filename_html), 'w') as output_file:
    # Write the header
    output_file.write("<html><head><title>Log Check Report</title>")
    output_file.write("""
    <style>
        body {
            background-color: #121212;
            color: #e0e0e0;
            font-family: Arial, sans-serif;
        }
        .collapsible {
            background-color: #333;
            color: #e0e0e0;
            cursor: pointer;
            padding: 10px;
            width: 100%;
            border: none;
            text-align: left;
            outline: none;
            font-size: 15px;
        }
        .active, .collapsible:hover {
            background-color: #555;
        }
        .content {
            padding: 0 18px;
            display: none;
            overflow: hidden;
            background-color: #1e1e1e;
        }
        .highlight {
            background-color: #444;
        }
        a {
            color: #1e90ff;
        }
    </style>
    <script>
        function toggleAll(expand) {
            var contents = document.getElementsByClassName("content");
            for (var i = 0; i < contents.length; i++) {
                contents[i].style.display = expand ? "block" : "none";
            }
        }
        document.addEventListener("DOMContentLoaded", function() {
            var coll = document.getElementsByClassName("collapsible");
            for (var i = 0; i < coll.length; i++) {
                coll[i].addEventListener("click", function() {
                    this.classList.toggle("active");
                    var content = this.nextElementSibling;
                    if (content.style.display === "block") {
                        content.style.display = "none";
                    } else {
                        content.style.display = "block";
                    }
                });
            }
        });
    </script>
    </head><body>
    """)
    report_status = "PASSED" if total_keyphrases_found == 0 else "FAILED"
    report_status_color = "#00ff00" if total_keyphrases_found == 0 else "#ff0000"
    output_file.write(f"<h1 style='text-align:center; color:#ffffff;'>Log Check Report</h1>")
    output_file.write(f"<h2 style='text-align:center; color:#ffffff;'>Verdict: <span style='color:{report_status_color};'>{report_status}</span></h2>")
    human_readable_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_file.write(f"<p><strong>Report created:</strong> {human_readable_timestamp}</p>")
    output_file.write(f"<p><strong>Logchecker file used:</strong> {os.path.abspath(__file__)}</p>")
    output_file.write(f"<p><strong>Directory checked:</strong> {current_directory}</p>")
    output_file.write(f"<p><strong>Keywords checked:</strong> {', '.join(keyphrases)}</p>")
    output_file.write("<hr>")
    
    # Write the summary of keyphrase occurrences
    total_keyphrases_found = sum(keyphrase_counts.values())
    unique_keyphrases_found = sum(1 for count in keyphrase_counts.values() if count > 0)
    output_file.write("<h2 style='color:#00ff00;'>Summary of Keyphrase Occurrences</h2>")
    output_file.write(f"<p><strong>Files Checked:</strong> {files_checked}</p>")
    output_file.write(f"<p><strong>Files with Keyphrases:</strong> {files_with_keyphrases} ({percentage_files_with_keyphrases:.2f}%)</p>")
    output_file.write(f"<p><strong>Unique Keyphrases Found:</strong> {unique_keyphrases_found}/{len(keyphrases)}</p>")
    output_file.write(f"<p><strong>Total Keyphrase Occurances:</strong> {total_keyphrases_found}</p>")
    output_file.write("<ul>")
    
    # Sort keyphrases by occurrence count in descending order
    sorted_keyphrases = sorted(keyphrase_counts.items(), key=lambda item: item[1], reverse=True)
    
    for keyphrase, count in sorted_keyphrases:
        output_file.write(f"<li><strong>Keyphrase:</strong> <span style='color:{keyphrase_colors[keyphrase]};'>{keyphrase}</span> - <strong>Files:</strong> {count} ({keyphrase_percentages[keyphrase]:.2f}%)</li>")
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
    output_file.write("<h2 style='color:#00ff00;'>Detailed Log File Analysis</h2>")
    output_file.write("<button onclick='toggleAll(true)'>Expand All</button>")
    output_file.write("<button onclick='toggleAll(false)'>Collapse All</button>")
    
    result_number = 1
    max_occurrences = {keyphrase: 0 for keyphrase in keyphrases}
    max_occurrence_result = {keyphrase: None for keyphrase in keyphrases}
    
    for file_path, keyphrases_dict in file_keyphrase_counts.items():
        if any(len(lines) > 0 for lines in keyphrases_dict.values()):
            keyphrases_found = [keyphrase for keyphrase, lines in keyphrases_dict.items() if lines]
            keyphrases_summary = " - ".join([f"<span style='color:{keyphrase_colors[keyphrase]};'>{keyphrase}</span>" for keyphrase in keyphrases_found])
            output_file.write(f"<button class='collapsible'>Logfile #{result_number} - Keyphrases: {keyphrases_summary}</button>")
            output_file.write("<div class='content'>")
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
    
    for keyphrase, result_num in max_occurrence_result.items():
        if result_num:
            output_file.write(f"<script>document.querySelectorAll('.collapsible')[{result_num - 1}].classList.add('highlight');</script>")
            output_file.write(f"<script>document.querySelectorAll('.collapsible')[{result_num - 1}].innerHTML += ' - <strong>Most occurrences of keyphrase: {keyphrase}</strong>';</script>")
    
    output_file.write("</body></html>")
