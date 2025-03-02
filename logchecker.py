import os
import datetime
import zipfile

# Define the keyphrases to search for
keyphrases = ["error occurred", "failed to start", "warning issued"]

# Get the directory from the user
user_input = input("Enter the directory path to search for log files (or press Enter to use the current directory): ")
current_directory = os.path.dirname(os.path.abspath(__file__)) if user_input.strip() == "" else user_input

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

# Write to the HTML file
with open(os.path.join(current_directory, output_filename_html), 'w') as output_file:
    # Write the header
    output_file.write("<html><head><title>Log Check Report</title>")
    output_file.write("""
    <style>
        .collapsible {
            background-color: #777;
            color: white;
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
            background-color: #f1f1f1;
        }
        .highlight {
            background-color: yellow;
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
    output_file.write("<button onclick='toggleAll(true)'>Expand All</button>")
    output_file.write("<button onclick='toggleAll(false)'>Collapse All</button>")
    
    result_number = 1
    keyphrase_colors = {
        "error occurred": "red",
        "failed to start": "orange",
        "warning issued": "purple"
    }
    max_occurrences = {keyphrase: 0 for keyphrase in keyphrases}
    max_occurrence_result = {keyphrase: None for keyphrase in keyphrases}
    
    for file_path, keyphrases_dict in file_keyphrase_counts.items():
        if any(len(lines) > 0 for lines in keyphrases_dict.values()):
            keyphrases_found = [keyphrase for keyphrase, lines in keyphrases_dict.items() if lines]
            keyphrases_summary = ", ".join(keyphrases_found)
            output_file.write(f"<button class='collapsible' style='color:{keyphrase_colors[keyphrases_found[0]]};'>Result Number: {result_number} - Keyphrases: {keyphrases_summary}</button>")
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
    
    output_file.write("</body></html>")
