import os
import subprocess
import csv
import re
import glob
import pandas as pd


def get_Insights(parallel, cpp_file, input_dir):
    executable = "./output_file"
    output_csv = "Results/Results" + parallel + ".csv"

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
            # print("Processing file:", file)
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


def Calling_for_analysis(Code,Type,Parallel):
    # saving the Code string in a cpp file
    with open("Code.cpp", "w") as file:
        file.write(Code)

    # getting the insights
    df = get_Insights(Parallel, "Code.cpp", "Inputs/"+Type)

    return df