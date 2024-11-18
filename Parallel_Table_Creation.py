import re
import pandas as pd


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
    
    # Split the content based on "Threads: " section to handle each thread count separately
    thread_sections = content.split("Threads: ")[1:]  # First section is before the first "Threads:"

    for section in thread_sections:
        lines = section.splitlines()
        thread_count = lines[0].strip()
        task_data = []
        
        # Process each task (Graph, Matrix, etc.)
        tasks = ['Graph', 'Matrix', 'Multiplication', 'Search', 'Sorting', 'Substring']
        current_task = None
        task_lines = []

        for line in lines[1:]:
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

        # Append data for this thread count
        for task in task_data:
            data.append([thread_count] + task)

    return data


def generate_table(parsed_data):
    df = pd.DataFrame(parsed_data, columns=['Threads', 'Task', 'Real Time', 'User Time', 'Sys Time'])
    return df

# Main function to run the parser and generate the table
def main():
    file_path = 'parallel bin/output.txt'
    parsed_data = parse_output(file_path)
    table = generate_table(parsed_data)
    table.to_csv('Parallel execution times.csv', index=True)

if __name__ == '__main__':
    main()
