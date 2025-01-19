import re
from collections import defaultdict

def calculate_tile_size(ram_size, array_type, element_size=4, reserve_memory=0.1):
    """
    Calculate the tile size based on RAM, array dimension type, and element size.

    Args:
        ram_size (int): Total available RAM in bytes.
        array_type (str): The type of array ("1D array", "2D array", "3D array").
        element_size (int): The size of one element in bytes (default: 4 bytes for float).
        reserve_memory (float): Fraction of memory to reserve for system use (default: 10%).

    Returns:
        int: The tile size (number of elements per tile).
    """

    ram_size = ram_size * 1024**3  # Convert GB to bytes

    # Calculate usable memory
    usable_memory = ram_size * (1 - reserve_memory)
    
    # Depending on the array type, calculate the size of one tile
    if array_type == "1D array":
        # For a 1D array, the tile size is just a number of elements
        tile_size = usable_memory // element_size
    elif array_type == "2D array":
        # For a 2D array, assume a square submatrix (tile)
        # Calculate the number of elements that can fit in the available memory
        side_length = int((usable_memory // (element_size * element_size))**0.5)  # sqrt of memory fitting a square
        tile_size = side_length * side_length
    elif array_type == "3D array":
        # For a 3D array, assume a cubic submatrix (tile)
        side_length = int((usable_memory // (element_size * element_size * element_size))**(1/3))  # cube root
        tile_size = side_length * side_length * side_length
    else:
        tile_size = 0  # No valid array type
        print("Invalid array type")
    
    return tile_size

def determine_array_access_type(loop_string):
    """
    Determines if the loop accesses a 1D, 2D, 3D array, or single variables.
    Returns the highest dimension array access found.

    Args:
        loop_string (str): The string containing the loop code.

    Returns:
        str: The type of array access ("1D array", "2D array", "3D array", or "Single variables").
    """
    # Regular expressions to detect different array access patterns
    pattern_3d = r'[A-Za-z_]+\s*\[[A-Za-z0-9_]+\]\s*\[[A-Za-z0-9_]+\]\s*\[[A-Za-z0-9_]+\]'
    pattern_2d = r'[A-Za-z_]+\s*\[[A-Za-z0-9_]+\]\s*\[[A-Za-z0-9_]+\]'
    pattern_1d = r'[A-Za-z_]+\s*\[[A-Za-z0-9_]+\]'
    pattern_nd = r'[A-Za-z_]+\s*\[[A-Za-z0-9_]+\]'
    
    # Check for array accesses from highest to lowest dimension
    if re.search(pattern_3d, loop_string):
        return "3D array"
    elif re.search(pattern_2d, loop_string):
        return "2D array"
    elif re.search(pattern_1d, loop_string):
        return "1D array"
    elif re.search(pattern_nd, loop_string):
        # finding the value for nD array
        # return "nD array"
        n = 0
        for match in re.finditer(pattern_nd, loop_string):
            n += 1
        return f"{n}D array"
    else:
        return "Single variables"

def generate_tiled_loop(loop_string, tile_size):
    """
    Converts a nested loop string into a tiled version.

    Args:
        loop_string (str): The original loop as a string.
        tile_size (int): The size of the tile for tiling.

    Returns:
        str: The loop tiled version.
    """
    # Match the loop pattern using regex
    loop_pattern = re.compile(
        r"for\s*\((int\s+)?(?P<var>[a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(?P<start>\d+);\s*" 
        r"(?P=var)\s*<\s*(?P<end>\d+);\s*(?P=var)\+\+\)"
    )

    # Find all loops in the input string
    loops = loop_pattern.findall(loop_string)
    
    if not loops:
        return "Invalid or no loop found in the input string."

    # Generate tiled version
    tiled_loops = []
    current_level = 0
    pos = 0

    while pos < len(loop_string):
        match = loop_pattern.search(loop_string, pos)
        if not match:
            tiled_loops.append(loop_string[pos:])
            break

        # Add content before the loop
        tiled_loops.append(loop_string[pos:match.start()])

        var, start, end = match.group("var"), match.group("start"), match.group("end")

        # Add the outer tiled loop
        tiled_loops.append(
            f"for (int {var}_tile = {start}; {var}_tile < {end}; {var}_tile += {tile_size}) {{\n"
        )
        # Add the inner loop
        tiled_loops.append(
            f"    for (int {var} = {var}_tile; {var} < std::min({var}_tile + {tile_size}, {end}); {var}++) {{\n"
        )

        # Update the position
        pos = match.end()
        current_level += 1

    # Close all opened loops
    tiled_loops.extend("    }\n" * current_level)

    return ''.join(tiled_loops)

def Operation_split(string):
    '''
    This function will split the string on the basis of operations
    Args:
        string: String to be splitted

    Returns:
        List of splitted string
    '''
    # splitting on bases of operations
    possible_operations = ['<', '>', '<=', '>=', '==', '!=', '&&', '||']

    condition_split = None
    for operation in possible_operations:
        if operation in string:
            condition_split = string.split(operation)
            break

    return condition_split

# handling Break conditions
def Soft_Break(function_str):
    """
    Convert a C/C++ function to its OpenMP equivalent by handling break and return statements.
    
    Args:
        function_str (str): The input C/C++ function as a string
        
    Returns:
        str: The converted OpenMP version of the function
    """
    # Extract function signature
    signature_match = re.match(r'^(.*?)\s*\{', function_str, re.DOTALL)
    if not signature_match:
        raise ValueError("Invalid function format")
    
    signature = signature_match.group(1)
    
    # Extract function body
    body = function_str[signature_match.end():].strip()[:-1]  # Remove the last '}'
    
    # Find the for loop
    for_loop_match = re.search(r'for\s*\((.*?);(.*?);(.*?)\)', body, re.DOTALL)
    if not for_loop_match:
        raise ValueError("No for loop found in function")
    
    # Extract loop components
    init, condition, increment = [s.strip() for s in for_loop_match.groups()]
    
    # Extract condition variables
    condition_vars = re.findall(r'([a-zA-Z_]\w*)', condition)
    loop_var = re.findall(r'([a-zA-Z_]\w*)\s*=', init)[0]
    limit_var = [var for var in condition_vars if var != loop_var][0]
    
    # Check if there's a return statement in the loop
    has_return = 'return' in body
    
    # Create the parallel variable if needed
    parallel_var = ""
    if has_return:
        return_val = re.search(r'return\s+([^;]+);', body).group(1)
        if return_val.isdigit() or return_val == '-1':
            parallel_var = f"    int parallel_temp = {return_val};\n"
        else:
            parallel_var = f"    {signature.split()[0]} parallel_temp = {return_val};\n"
    
    # Process the loop body
    loop_body = re.search(r'for\s*\([^{]*\)\s*{(.*?)}', body, re.DOTALL).group(1)
    
    # Replace return statements with parallel variable assignment
    if has_return:
        loop_body = re.sub(r'return\s+([^;]+);', 
                          f'parallel_temp = \\1;\n        {loop_var} = {limit_var};', 
                          loop_body)
    
    # Replace break statements
    loop_body = re.sub(r'break;', f'{loop_var} = {limit_var};', loop_body) + '}\n'
    
    # Add check for early termination
    if has_return:
        loop_body += f'\n        if (parallel_temp != {return_val}) {loop_var} = {limit_var};'
    
    # Construct the OpenMP version
    openmp_version = f"{signature} {{\n"
    if parallel_var:
        openmp_version += parallel_var
    
    # Add OpenMP pragma
    if has_return:
        openmp_version += "    #pragma omp parallel for shared(parallel_temp)\n"
    else:
        # Determine shared variables from the loop body
        shared_vars = set(re.findall(r'([a-zA-Z_]\w*)\s*=', loop_body)) - {loop_var}
        if shared_vars:
            shared_list = ", ".join(shared_vars)
            openmp_version += f"    #pragma omp parallel for shared({shared_list})\n"
        else:
            openmp_version += "    #pragma omp parallel for \n"
    
    # Add the modified for loop
    openmp_version += f"    for ({init}; {condition}; {increment}) {{\n"
    openmp_version += "        " + loop_body.replace("\n", "\n        ") + "\n"
    openmp_version += "    }\n"
    
    # Add return statement if needed
    if has_return:
        openmp_version += "    return parallel_temp;\n"
    
    openmp_version += "}"
    
    return openmp_version

# This function will check if the given loop block is parallelizable or not.
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

# This function will parallelize the given loop block if it is parallelizable.
def parallelizing_loop(Loop_Bloc):

    Parallelized_string = "#pragma omp parallel for"
    # print("Here")
    Reduction_line = Reduction_aaplication(Loop_Bloc)
    # print(Reduction_line)
    if Reduction_line:
        for line in Reduction_line:
            Parallelized_string += f" {line}"
    else:
        Parallelized_string += " schedule(static)"

    # print (Parallelized_string)
    return Parallelized_string

# This function checks if there is 'cin', 'cout', 'printf' or any type of input/output statement in the given code block.
def check_input_output(Loop_Block):
    """
    Checks if there is any input/output statement in the given loop block.
    If there is any input/output statement, returns True.
    Otherwise, returns False.

    Args:
        Loop_Block (str): The code block of a single loop.

    Returns:
        bool: True if there is any input/output statement, False otherwise.
    """
    # Patterns to identify input/output statements
    io_patterns = [
        r"cin\s*>> [^;]+;",
        r"cout\s*<< [^;]+;",
        r"printf\s*\( [^;]+;",
        r"scanf\s*\( [^;]+;",
    ]

    # Check for input/output patterns
    for pattern in io_patterns:
        if re.search(pattern, Loop_Block):
            return True

    return False

# This function will return a list of all the loop blocks present in the given C or C++ file.
def LoopBlocks(Code_String):
    Loop_Blocks = []
    i = 0  # Initialize the index manually

    while i < len(Code_String):
        # Check for the keyword 'for'
        if Code_String[i:i + 3] == 'for':
            start_index = i
            Block = "for "

            space = True
            # Find the start of the loop body
            while i < len(Code_String) and Code_String[i] != '(':
                i += 1
                space = False
            
            if space:
                Block = 'for'

            if i < len(Code_String):
                # Include the for loop condition
                while i < len(Code_String) and Code_String[i] != ')':
                    Block += Code_String[i]
                    i += 1
                Block += Code_String[i]  # Include the closing ')'
                i += 1  # Move past the closing ')'

            # Handle loop body
            if i < len(Code_String) and (Code_String[i] == '{' or Code_String[i + 1] == '{'):
                if Code_String[i] != '{':
                    i += 1
                Loop_Stack = ['{']
                Block += Code_String[i]  # Include '{'
                i += 1

                # Find the end of the block
                while Loop_Stack and i < len(Code_String):
                    if Code_String[i] == '{':
                        Loop_Stack.append('{')
                    elif Code_String[i] == '}':
                        Loop_Stack.pop()
                    Block += Code_String[i]
                    i += 1
            else:
                # Single-line loop body
                while i < len(Code_String) and Code_String[i] != ';':
                    Block += Code_String[i]
                    i += 1
                if i < len(Code_String) and Code_String[i] == ';':
                    Block += Code_String[i]  # Include ';'
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

# This function will write the content to the file.
def writing_code_to_file(file_path, content):
    try:
        with open(file_path, 'w') as file:
            file.write(content)
    except IOError:
        print("An error occurred while writing to the file.")

# This function will count the number of for loops in the given code.
def getCountofForLoops(code):
    count = 0
    i = 0
    while i < len(code):
        if code[i:i + 3] == 'for':
            count += 1
        i += 1
    return count

# This function will replace the loop block with the parallelized block in the code string.
def Replacing_Loop_Block(Loop_Block, Parallelized_Block, Code_String):
    '''
    This function will replace the loop block with the parallelized block in the code string.
        :param Loop_Block: List of original loop blocks in the code.
        :param Parallelized_Block: List of corresponding parallelized loop blocks.
        :param Code_String: Original code as a string.
        :return: Code string with parallelized blocks.
    '''
    for i in range(len(Loop_Block)):
        # finding the loop block in the code string
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

# This function will check the variable that are declared in the loop block and the one that come from outside the loop block.
def Variable_in_Loop(Loop_Block):
    Outside_Variable = []
    Inside_Variable = []

    # finding the variables that are declared inside the loop block
    # The vaiable can be any primitive data type or any user defined data type
    Inside_Variable = re.findall(r'\b(?:int|float|double|char|string|vector|list|set|map)\s+\w+\b', Loop_Block)

    # finding the variables that are declared outside the loop block
    # The vaiable can be any primitive data type or any user defined data type
    Outside_Variable = re.findall(r'\b(?:int|float|double|char|string|vector|list|set|map)\s+\w+\b', Loop_Block)

    return Inside_Variable, Outside_Variable

def Parinomo(SCode, core_type, ram_type, processors_count):
    Loop_Blocks = LoopBlocks(SCode)

    # applying tilling on the loop block
    for Loop_Block in Loop_Blocks:
        array_type = determine_array_access_type(Loop_Block)
        if array_type != "Single variables":
            tile_size = calculate_tile_size(ram_type, array_type)
            tiled_loop = generate_tiled_loop(Loop_Block, tile_size)
            SCode = SCode.replace(Loop_Block, tiled_loop)

    Loop_Blocks = LoopBlocks(SCode)

    # checking if the loop can be parallelized or not if not removeing that loop block
    for Loop_Block in Loop_Blocks:
            if check_input_output(Loop_Block):
                Loop_Blocks.remove(Loop_Block)

    parall_Loop_Block = []
    for Loop_Block in Loop_Blocks:

        if 'break' in Loop_Block or 'return' in Loop_Block:
            ParallelBlock = Soft_Break(Loop_Block)
        else:
            ParallelBlock = parallelizing_loop(Loop_Block) 

        if getCountofForLoops(Loop_Block) > 1:
            ParallelBlock += f'collapse({getCountofForLoops(Loop_Block)})'

        ParallelBlock += '\n' + Loop_Block
        parall_Loop_Block.append(ParallelBlock)

    Pcode = Replacing_Loop_Block(Loop_Blocks, parall_Loop_Block, SCode)

    # replacing 'int main()' with 'int main(int argc, char *argv[])'
    if 'int main()' in Pcode:
        Pcode = Pcode.replace('int main()', 'int main(int argc, char *argv[])')

        # thread_count = f"omp_set_num_threads({processors_count-2});\n"

        return "#include <omp.h>\n" + Pcode
    
    return Pcode