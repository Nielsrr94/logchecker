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

# Iterate over all files in the current directory
for filename in os.listdir(current_directory):
    if filename.endswith(".txt") and "log" and "logcheck" not in filename:
        with open(os.path.join(current_directory, filename), 'r') as file:
            lines = file.readlines()
        
        # Prepare the output file
        output_filename = f"logcheck_{timestamp}.txt"
        with open(os.path.join(current_directory, output_filename), 'w') as output_file:
            for i, line in enumerate(lines):
                for keyword in keywords:
                    if keyword in line:
                        output_file.write("="*40 + "\n")
                        output_file.write("LOG CHECKER REPORT\n")
                        output_file.write("="*40 + "\n\n")
                        output_file.write(f"Keyword: {keyword}\n")
                        output_file.write(f"Line: {line.strip()}\n")
                        output_file.write(f"File: {os.path.join(current_directory, filename)}\n")
                        output_file.write("\n")