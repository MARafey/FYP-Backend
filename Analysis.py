import os
import subprocess
import csv
import re
import glob
import pandas as pd
from Parinomo import indent_cpp_code, LoopBlocks


def get_Insights(parallel, cpp_file, input_dir):
    executable = "./output_file"
    output_csv = "Results/Results" + str(parallel) + ".csv"

    # Compile C++ Code
    if parallel == False:
        compile_command = f"g++ {cpp_file} -o {executable} -O2"
    else:
        compile_command = f"g++ {cpp_file} -o {executable} -O2 -fopenmp"
    compilation = subprocess.run(compile_command, shell=True, capture_output=True, text=True)

    if compilation.returncode != 0:
        print("Compilation failed:", compilation.stderr)
        exit(1)
    else:
        print("Compilation successful.")

    # CSV Headers
    csv_header = [
        "Input File", "Instruction References (I refs)", "User Time (s)", "System Time (s)",
        "CPU Usage (%)", "Elapsed Time (s)", "Max RSS (KB)", "Major Page Faults",
        "Minor Page Faults", "Voluntary Context Switches", "Involuntary Context Switches",
        "File System Inputs", "File System Outputs"
    ]
    results = []

    # Process each input file
    for file in sorted(os.listdir(input_dir)):
        if file.endswith(".txt"):
            input_path = os.path.join(input_dir, file)
            print("Processing file:", file)
            command = f"/usr/bin/time -v valgrind --tool=callgrind {executable} < {input_path}"
            # print("Command:", command)
            
            # Run command
            process = subprocess.run(command, shell=True, capture_output=True, text=True)
            # print("Return Code:", process.returncode)
            stdout, stderr = process.stdout, process.stderr

            # Extract Callgrind instructions (I refs)
            instruction_refs = re.search(r"I\s+refs:\s+([\d,]+)", stdout)
            instruction_refs = instruction_refs.group(1).replace(",", "") if instruction_refs else "N/A"

            # Extract time and memory stats from stderr
            metrics = {
                "User Time (s)": re.search(r"User time \(seconds\):\s+([\d.]+)", stderr),
                "System Time (s)": re.search(r"System time \(seconds\):\s+([\d.]+)", stderr),
                "CPU Usage (%)": re.search(r"Percent of CPU this job got:\s+([\d]+)%", stderr),
                "Elapsed Time (s)": re.search(r"Elapsed \(wall clock\) time.*?:\s+([\d:.]+)", stderr),
                "Max RSS (KB)": re.search(r"Maximum resident set size \(kbytes\):\s+(\d+)", stderr),
                "Major Page Faults": re.search(r"Major \(requiring I/O\) page faults:\s+(\d+)", stderr),
                "Minor Page Faults": re.search(r"Minor \(reclaiming a frame\) page faults:\s+(\d+)", stderr),
                "Voluntary Context Switches": re.search(r"Voluntary context switches:\s+(\d+)", stderr),
                "Involuntary Context Switches": re.search(r"Involuntary context switches:\s+(\d+)", stderr),
                "File System Inputs": re.search(r"File system inputs:\s+(\d+)", stderr),
                "File System Outputs": re.search(r"File system outputs:\s+(\d+)", stderr)
            }

            # Convert extracted values to text or default to "N/A"
            extracted_data = [metrics[key].group(1) if metrics[key] else "N/A" for key in metrics]

            # Save results
            results.append([file, instruction_refs] + extracted_data)
            # print(f"Processed {file}")

            # Find all files matching the pattern
            files = glob.glob("callgrind.out.*")

            # Remove each file
            for file in files:
                os.remove(file)


    # Write to CSV
    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)
        writer.writerows(results)

    # print(f"Results saved in {output_csv}")

    # making into a dataframe
    df = pd.read_csv(output_csv)

    # remove the output file
    os.remove(output_csv)
    return df


def detect_input_type(code):
    # Regex patterns for loop structures
    loop_pattern = re.compile(r'\b(for|while|do)\b[^{]*{')
    
    # Regex patterns for input types
    one_d_array = re.compile(r'\bcin\s*>>\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\[\s*[a-zA-Z0-9_]+\s*\]')
    two_d_array = re.compile(r'\bcin\s*>>\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\[\s*[a-zA-Z0-9_]+\s*\]\s*\[\s*[a-zA-Z0-9_]+\s*\]')
    graph = re.compile(r'\bcin\s*>>\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*>>\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*;')
    weighted_graph = re.compile(r'\bcin\s*>>\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*>>\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*>>\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*;')
    
    # Find all loops
    loop_blocks = loop_pattern.findall(code)
    
    # Checking inside loop bodies
    for match in re.finditer(loop_pattern, code):
        loop_body_start = match.end()
        loop_body = code[loop_body_start:]
        
        # Find first closing brace to extract only loop content
        brace_count = 1
        for i, char in enumerate(loop_body):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    loop_body = loop_body[:i]
                    break
        
        # Check input type
        if re.search(two_d_array, loop_body):
            return "2 D Array"
        elif re.search(one_d_array, loop_body):
            return "1 D Array"
        elif re.search(weighted_graph, loop_body):
            return "Weighted Graph"
        elif re.search(graph, loop_body):
            return "Graph"
    
    return "Unknown"

def Calling_for_analysis(Code,Type):

    Code = indent_cpp_code(Code)
    Loops = LoopBlocks(Code)
    # saving the Code string in a cpp file
    with open("Code.cpp", "w") as file:
        file.write(Code)

    # finding the input type where will be cin statements
    Loop_found = ''
    for loop in Loops:
        if detect_input_type(loop) == True:
            Loop_found = loop
            break


    # getting the insights
    df = get_Insights(Type, "Code.cpp", "Inputs/" + Loop_found)
    
    # deleting the Code.cpp file
    os.remove("Code.cpp")

    return df