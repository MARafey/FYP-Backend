import re
from collections import defaultdict

def Reduction_aaplication(Loop_Block):
    """
    Checks if reduction is possible in the given loop block.
    If reduction is possible, returns a list of reduction calls.
    Otherwise, returns an empty list.

    Args:
        Loop_Block (str): The code block of a single loop.

    Returns:
        list: A list of reduction directives if applicable, or an empty list.
    """
    import re

    # Patterns to identify potential reductions
    reduction_patterns = [
        (r"(\w+)\s*\+=\s*[^\;]+;", "+"),  # sum: var += ...
        (r"(\w+)\s*\*=\s*[^\;]+;", "*"),  # product: var *= ...
        (r"(\w+)\s*=\s*\1\s*\+\s*[^\;]+;", "+"),  # sum: var = var + ...
        (r"(\w+)\s*=\s*\1\s*\*\s*[^\;]+;", "*"),  # product: var = var * ...
        (r"(\w+)\s*=\s*min\s*\(\s*\1\s*,", "min"),  # min: var = min(var, ...)
        (r"(\w+)\s*=\s*max\s*\(\s*\1\s*,", "max"),  # max: var = max(var, ...)
    ]

    # Store detected reductions
    detected_reductions = []

    # Check for reduction patterns
    for pattern, operation in reduction_patterns:
        matches = re.findall(pattern, Loop_Block)
        for match in matches:
            variable = match
            # Append reduction directive in OpenMP style
            detected_reductions.append(f"reduction({operation}:{variable})")

    return detected_reductions

def parallelizing_loop(Loop_Bloc):
    Parallelized_string = "#pragma omp parallel for"

    Reduction_line = Reduction_aaplication(Loop_Bloc)

    if Reduction_line:
        for line in Reduction_line:
            Parallelized_string += f" {line}"
    else:
        Parallelized_string += " schedule(static)"

    return Parallelized_string

# This function will return a list of all the loop blocks present in the given C or C++ file.
def LoopBlocks(Code_String):
    Loop_Blocks = []
    Loop_Stack = []
    i = 0  # Initialize the index manually

    while i < len(Code_String):
        # Check for the keyword 'for'
        if Code_String[i:i + 3] == 'for':
            start_index = i
            Block = ""

            # Find the start of the loop block, which is the next '{' after the 'for' keyword
            while Code_String[i] != '{' and i < len(Code_String):
                i += 1
            i += 1  # Move past the '{'

            Block += Code_String[start_index: i]

            Loop_Stack.append('{')
            # Find the end of the loop block
            while Loop_Stack and i < len(Code_String):
                if Code_String[i] == '{':
                    Loop_Stack.append('{')
                elif Code_String[i] == '}':
                    Loop_Stack.pop()
                Block += Code_String[i]
                i += 1

            Loop_Blocks.append(Block)
        else:
            i += 1  # Move to the next character if not a 'for' loop

    return Loop_Blocks

# This function will check what is the dependency of the given loop block on the variables
def analyze_data_dependency(code_snippet):
    # Regular expressions to capture read and write patterns
    write_pattern = re.compile(r'(\w+)\s*\[?.*?\]?\s*=')
    read_pattern = re.compile(r'=\s*(.*)')

    # Dictionaries to store read and write variables by line
    writes = defaultdict(set)
    reads = defaultdict(set)

    # Dependencies dictionary to track each variable's dependencies
    dependencies = defaultdict(lambda: {
        "True Dependency (Read after Write)": False,
        "Anti Dependency (Write after Read)": False,
        "Output Dependency (Write after Write)": False,
    })

    # Process each line in the code snippet
    lines = code_snippet.strip().splitlines()
    for line in lines:
        # Identify write variables
        write_match = write_pattern.search(line)
        if write_match:
            write_var = write_match.group(1)
            writes[write_var].add(line)

        # Identify read variables from the right side of assignments
        read_match = read_pattern.search(line)
        if read_match:
            rhs = read_match.group(1)
            # Find all variables on the right-hand side
            rhs_vars = re.findall(r'\b\w+\b', rhs)
            for read_var in rhs_vars:
                reads[read_var].add(line)

    # Check dependencies for each variable
    for write_var in writes:
        # True Dependency: read after write for the same variable
        if write_var in reads:
            dependencies[write_var]["True Dependency (Read after Write)"] = True

        # Anti Dependency: write after read for the same variable
        if write_var in reads:
            dependencies[write_var]["Anti Dependency (Write after Read)"] = True

        # Output Dependency: multiple writes to the same variable
        if len(writes[write_var]) > 1:
            dependencies[write_var]["Output Dependency (Write after Write)"] = True

    return dependencies

def writing_code_to_file(file_path, content):
    try:
        with open(file_path, 'w') as file:
            file.write(content)
    except IOError:
        print("An error occurred while writing to the file.")

def Replacing_Loop_Block(Loop_Block, Parallelized_Block, Code_String):
    '''
    This function will replace the loop block with the parallelized block in the code string.
        :param Loop_Block:
        :param Parallelized_Block:
        :param Code_String:
        :return: Parellized code string
    '''
    for i in range(len(Loop_Block)):
        Code_String = Code_String.replace(Loop_Block[i], Parallelized_Block[i])
    return Code_String

# This function will open the C or C++ file and get content from that file
def open_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            Loop_Blocks = LoopBlocks(content)
            parall_Loop_Block = []
            for Loop_Block in Loop_Blocks:
                parall_Loop_Block.append(parallelizing_loop(Loop_Block) + '\n' + Loop_Block)

            Parellel_code = Replacing_Loop_Block(Loop_Blocks, parall_Loop_Block, content)

            writing_code_to_file('parallelized_code.cpp', Parellel_code)
    except FileNotFoundError:
        print("File not found. Please check the file path.")
    except IOError:
        print("An error occurred while reading the file.")


if __name__ == "__main__":
    file_path = 'example.cpp'
    if file_path.endswith(('.c', '.cpp')):
        open_file(file_path)
    else:
        print("Please provide a valid C or C++ file.")
