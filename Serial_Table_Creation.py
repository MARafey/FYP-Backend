import re
import pandas as pd

# Function to extract time information (real, user, sys)
def extract_time_info(lines):
    time_info = {}
    for line in lines:
        if line.startswith("real"):
            time_info['real'] = line.split()[1]
        elif line.startswith("user"):
            time_info['user'] = line.split()[1]
        elif line.startswith("sys"):
            time_info['sys'] = line.split()[1]
    return time_info

# Function to parse the output file and build a structured table
def parse_output(file_path):
    data = []
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Split the content based on tasks (Graph, Matrix, etc.)
    tasks = ['Graph', 'Matrix', 'Multiplication', 'Search', 'Sorting', 'Substring']
    task_data = []
    current_task = None
    task_lines = []

    lines = content.splitlines()

    # Iterate over all lines in the file
    for line in lines:
        line = line.strip()
        if line in tasks:
            if current_task:
                # Extract and store the previous task data
                time_info = extract_time_info(task_lines)
                task_data.append([current_task, time_info.get('real', 'N/A'), time_info.get('user', 'N/A'), time_info.get('sys', 'N/A')])
            current_task = line
            task_lines = []
        else:
            task_lines.append(line)
    
    # After the loop, add the data for the last task
    if current_task:
        time_info = extract_time_info(task_lines)
        task_data.append([current_task, time_info.get('real', 'N/A'), time_info.get('user', 'N/A'), time_info.get('sys', 'N/A')])

    # Append data for the tasks
    for task in task_data:
        data.append([task[0], task[1], task[2], task[3]])

    return data

# Function to convert the parsed data into a DataFrame and display it as a table
def generate_table(parsed_data):
    df = pd.DataFrame(parsed_data, columns=['Task', 'Real Time', 'User Time', 'Sys Time'])
    return df

# Main function to run the parser and generate the table
def main():
    file_path = 'Serial bin/output.txt'  # Path to your output file
    parsed_data = parse_output(file_path)
    table = generate_table(parsed_data)
    # Optionally, you can save the table as an Excel or CSV file
    table.to_csv('Serial execution times.csv', index=True)

if __name__ == '__main__':
    main()
