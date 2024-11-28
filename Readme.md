# Parinomo

This project automates the parallelization of loops in C or C++ code using OpenMP directives. Below is an explanation of each function included in the script.

---

### **Functions Overview**

1. **`Reduction_aaplication(Loop_Block)`**  
   Identifies potential reduction operations (e.g., summation, product) in a loop and generates corresponding OpenMP reduction directives.

2. **`parallelizing_loop(Loop_Bloc)`**  
   Generates an OpenMP parallel directive for a given loop, including reduction or scheduling clauses if applicable.

3. **`LoopBlocks(Code_String)`**  
   Extracts all loop blocks (`for` loops) from the provided C or C++ code as separate strings.

4. **`analyze_data_dependency(code_snippet)`**  
   Analyzes data dependencies in a code snippet, detecting true, anti, and output dependencies based on variable usage.

5. **`writing_code_to_file(file_path, content)`**  
   Writes the given content to a specified file.

6. **`Replacing_Loop_Block(Loop_Block, Parallelized_Block, Code_String)`**  
   Replaces identified loop blocks in the original code with their parallelized versions.

7. **`open_file(file_path)`**  
   Opens a C or C++ file, extracts loop blocks, parallelizes them, and writes the updated code to a new file (`parallelized_code.cpp`).

---

### **How to Use**

1. Place the target C or C++ file in the working directory.  
2. Update the `file_path` variable in the script to the file's name (e.g., `'example.cpp'`).  
3. Run the script.  
4. The parallelized code will be saved in a file named `parallelized_code.cpp`.

--- 

### **Requirements**

- Python 3.x  
- OpenMP directives must be supported in your target compiler.  
