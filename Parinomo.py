import re
from collections import defaultdict
import json
from typing import Any
import subprocess

# gives list of all variables withing the loop block return as single varaible or array varaible
def extract_loop_variables(code):
    """
    Extracts variables from C/C++ loop blocks, categorizing them as single or array variables.
    
    Args:
        code (str): A string containing C/C++ loop code
        
    Returns:
        tuple: (single_variables, array_variables) lists containing variable names
    """
    # Remove C-style comments
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
    
    # Find all variable declarations
    declarations = re.findall(r'\b(?:int|float|double|char|bool|long|short|unsigned|void|auto)\s+([a-zA-Z_][a-zA-Z0-9_]*)', code)
    
    # Find all variables used in the code
    # This looks for identifiers that aren't part of a keyword or function call
    all_identifiers = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b(?!\s*\()', code)
    
    # Remove C/C++ keywords
    keywords = ['for', 'if', 'else', 'while', 'do', 'switch', 'case', 'break', 'continue',
                'return', 'int', 'float', 'double', 'char', 'bool', 'void', 'long', 'short',
                'unsigned', 'signed', 'const', 'static', 'struct', 'enum', 'class', 'auto']
    all_identifiers = [ident for ident in all_identifiers if ident not in keywords]
    
    # Find array access patterns: identifiers followed by square brackets
    array_pattern = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\[')
    array_variables = list(set(array_pattern.findall(code)))
    
    # All other variables are single variables
    single_variables = list(set(all_identifiers) - set(array_variables))
    
    # Add declared variables that might not be used
    single_variables = list(set(single_variables + declarations))
    
    # Sort lists for consistent output
    single_variables.sort()
    array_variables.sort()
    
    return single_variables, array_variables

def analyze_openmp_variables(code, single_variables, array_variables):
    """
    Analyzes loop variables to determine their OpenMP clause classification
    (shared, private, firstprivate, lastprivate)
    
    Args:
        code (str): C/C++ loop code
        single_variables (list): List of single variables
        array_variables (list): List of array variables
        
    Returns:
        dict: Dictionary containing lists of variables for each OpenMP clause
    """
    # Remove C-style comments
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
    
    # Extract code inside the loop body (between curly braces)
    loop_body_match = re.search(r'for\s*\([^)]*\)\s*{(.*?)}', code, re.DOTALL)
    if not loop_body_match:
        return {"error": "No valid loop body found"}
    
    loop_body = loop_body_match.group(1)
    
    # Extract loop control variable
    loop_control_match = re.search(r'for\s*\(\s*(?:int\s+)?([a-zA-Z_][a-zA-Z0-9_]*)', code)
    if not loop_control_match:
        return {"error": "Could not identify loop control variable"}
    
    loop_var = loop_control_match.group(1)
    
    # Initialize result categories
    result = {
        "shared": [],
        "private": [loop_var],  # Loop control variable is always private
        "firstprivate": [],
        "lastprivate": [],
        "reduction": []
    }
    
    # Find all variables declared inside the loop
    declared_inside = re.findall(r'\b(?:int|float|double|char|bool|long|short|unsigned|void|auto)\s+([a-zA-Z_][a-zA-Z0-9_]*)', loop_body)
    
    # All variables declared inside the loop are private
    result["private"].extend(declared_inside)
    
    # Check each single variable
    for var in single_variables:
        if var in declared_inside or var == loop_var:
            continue  # Already handled
            
        # Check if read before write (firstprivate candidate)
        lines = loop_body.split('\n')
        read_first = False
        written = False
        
        for line in lines:
            # Look for read operations (variable appears on right side of assignment or in expressions)
            read_match = re.search(rf'[=|+|\-|*|/|%|&|\||^|>|<|!|?|:|\s]\s*{var}\b', line) or \
                         re.search(rf'[+|\-|*|/|%|&|\||^|>|<|!|?|:|\(]\s*{var}\b', line) or \
                         re.search(rf'\b{var}[+|\-|+]{2}', line)  # increment/decrement
            
            # Look for write operations (variable appears on left side of assignment)
            write_match = re.search(rf'\b{var}\s*(?:[+|\-|*|/|%|&|\||^])?=', line) or \
                          re.search(rf'\b{var}[+|\-]{2}', line)  # increment/decrement
            
            if read_match and not written:
                read_first = True
            if write_match:
                written = True
                
        # Check if written in the last iteration (lastprivate candidate)
        last_iter_usage = re.search(rf'\b{var}\s*(?:[+|\-|*|/|%|&|\||^])?=', lines[-1]) or \
                          re.search(rf'\b{var}[+|\-]{2}', lines[-1])
                
        # Check for reduction patterns
        reduction_match = re.search(rf'\b{var}\s*(?:[+|\-|*|/|%|&|\|])?=\s*{var}\b', loop_body)
        
        # Assign to appropriate category
        if reduction_match:
            result["reduction"].append(var)
        elif read_first and written:
            result["firstprivate"].append(var)
        elif last_iter_usage:
            result["lastprivate"].append(var)
        elif written:
            result["private"].append(var)
        else:
            result["shared"].append(var)
    
    # Handle array variables - generally shared unless clear pattern indicates otherwise
    for var in array_variables:
        # Check if the array is only read from
        write_to_array = re.search(rf'\b{var}\s*\[[^\]]*\]\s*(?:[+|\-|*|/|%|&|\||^])?=', loop_body) or \
                         re.search(rf'\b{var}\s*\[[^\]]*\][+|\-]{2}', loop_body)
                         
        if not write_to_array:
            result["shared"].append(var)
        else:
            # Check if array modifications depend on loop variable
            loop_var_dependent = re.search(rf'\b{var}\s*\[.*\b{loop_var}\b.*\]', loop_body)
            if loop_var_dependent:
                # If each iteration writes to different indices (loop var is used in index)
                result["shared"].append(var)
            else:
                # If we're potentially writing to the same indices
                result["shared"].append(var)  # Still shared but with potential race conditions
                
    # Remove duplicates and sort
    for category in result:
        result[category] = sorted(list(set(result[category])))
        
    return result

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
        r"\s*for\s*\((int\s+)?(?P<var>[a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(?P<start>[a-zA-Z_][a-zA-Z0-9_]*|\d+);\s*"
        r"(?P=var)\s*<\s*(?P<end>[a-zA-Z_][a-zA-Z0-9_]*|\d+);\s*(?P=var)\+\+\)"
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
            f"for (int {var}_tile = {start}; {var}_tile < {end}; {var}_tile += tile_size) {{\n"
        )
        # Add the inner loop
        tiled_loops.append(
            f"    for (int {var} = {var}_tile; {var} < std::min({var}_tile + tile_size, {end}); {var}++) {{\n"
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
        r"getline\s*\( [^;]+;",
        # multiple input/output statements
        r"cin\s*>> [^;]+;\s*cout\s*<< [^;]+;",
        r"printf\s*\( [^;]+;\s*printf\s*\( [^;]+;",
        r"scanf\s*\( [^;]+;\s*scanf\s*\( [^;]+;",
        r"getline\s*\( [^;]+;\s*getline\s*\( [^;]+;",

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

            semi_colum_count = 0
            for j in range(0, len(Block)):
                if Block[j] == ';':
                    semi_colum_count += 1

            if semi_colum_count < 2:
                continue

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

# This function finds start and end index of substring in the string
def find_substring(string, substring):
    start = string.index(substring)
    end = start + len(substring)
    return start, end

def Complexity_of_loop(Block: str) -> int | tuple[int, Any]:
    """
    This function calculates the complexity of the given loop block, based on provided rules.
    Rules:
        This function will return the complexity of the loop block.
        Things used:
            1. The loop condition
            2. The number of nested loops and their conditions
            3. The number of variables used in the loop
                a. single variable have complexity 1
                b. multiple dimension array variables have complexity 2
            4. The number of operations in the loop
                a. Binary operation have complexity 1 i.e (&, |, ^)
                b. Arithmatic operations have complexity 2 i.e (+, -, *, /, %)
                c. Unary operations have complexity 1.5 i.e (++, --)
                d. Assignment operations have complexity 1 i.e (=)
            5. The total number of lines within the loop excluding the loop condition line and brackets '{}' lines
            6. The number of function calls within the loop block
                a. Complexity of function depends upon the passed arguments and the return type of the function
                b. In case of passing array the complexity will be 3
                c. In case of passing single variable the complexity will be 1
            7. Incase the loop condition has a hard-coded value, the complexity will be that value multiplied by 0.2
    Parameters:
        Block (str): The loop block as a string

    Returns:
        float: The total calculated complexity of the loop block
    """
    complexity = 0.0

    # 1. Analyze the loop condition
    loop_condition = re.search(r'for\s*\((.*?)\)', Block)

    # Check if the loop condition has a hard-coded value
    value = re.findall(r'(\d+)', Block)
    # print(value)
    if value:
        # print(value)
        for v in value:
            if int(v) > 1000000:
                complexity += float(v) * 0.2
            else:
                complexity -= float(v) * 0.42 # 42 is a joke because during random seed we use 42 and I never understood why
            # print(complexity)

    if loop_condition:
        condition_content = loop_condition.group(1)
        # Assume each variable in the condition contributes a base complexity of 1
        complexity += condition_content.count(',') + 1  # Number of variables in loop condition

    # 2. Count nested loops
    nested_loops = re.findall(r'for\s*\([^)]*\)', Block)
    complexity += len(nested_loops) * 2  # Each nested loop adds 2 to complexity

    # 3. Analyze variables in the loop
    variables = re.findall(r'([a-zA-Z_]\w*(?:\[[^\]]*\])*)', Block)
    for var in variables:
        if '[' in var:  # It's a multi-dimensional variable
            complexity += 2
        else:  # Single variable
            complexity += 1

    # 4. Count operations
    binary_ops = re.findall(r'[\&\|\^]', Block)  # Binary operations
    arithmetic_ops = re.findall(r'[+\-*/%]', Block)  # Arithmetic operations
    unary_ops = re.findall(r'\+\+|--', Block)  # Unary operations
    assignment_ops = re.findall(r'=', Block)  # Assignment operations

    complexity += len(binary_ops) * 1  # Each binary operation adds 1
    complexity += len(arithmetic_ops) * 2  # Each arithmetic operation adds 2
    complexity += len(unary_ops) * 1.5  # Each unary operation adds 1.5
    complexity += len(assignment_ops) * 1  # Each assignment operation adds 1

    # 5. Total number of lines inside the loop (excluding brackets and loop header)
    lines = Block.split('\n')
    meaningful_lines = [line for line in lines if
                        line.strip() and not line.strip().startswith('for') and not line.strip().startswith(
                            '{') and not line.strip().startswith('}')]
    complexity += len(meaningful_lines)

    # 6. Function calls within the loop
    function_calls = re.findall(r'\b\w+\s*\(([^)]*)\)', Block)
    for call in function_calls:
        # Check what is passed to the function
        if '[' in call:  # Passing array
            complexity += 3
        else:  # Single variable
            complexity += 1

    # classifying the complexity into 1 to 5
    # 5 being the most complex and 1 being the least complex

    complexity = round(complexity)

    if complexity > 50:
        return 5 , complexity
    elif complexity > 40:
        return 4 , complexity
    elif complexity > 30:
        return 3 , complexity
    elif complexity > 20:
        return 2 , complexity
    else:
        return 1 , complexity

# This function will replace the loop block with the parallelized block in the code string.
def Replacing_Loop_Block(Loop_Block, Parallelized_Block, Code_String):
    '''
    This function will replace the loop block with the parallelized block in the code string.
        :param Loop_Block: List of original loop blocks in the code.
        :param Parallelized_Block: List of corresponding parallelized loop blocks.
        :param Code_String: Original code as a string.
        :return: Code string with parallelized blocks.
    '''

    # Code_String = '\n'+Code_String.strip().replace('  ', '').replace('\n\n', '\n')
    for i in range(len(Loop_Block)):
        str = Loop_Block[i]
        str = str.strip().replace('{', ' {')
        str = str.strip().replace('  ', ' ')
        str = indent_cpp_code(str)
        # print('*'*20 + '\n'+str)
        # print('*'*20 + '\n'+ Parallelized_Block[i])
        # print('*'*20 + '\n'+Code_String)
        Code_String = Code_String.replace(str, Parallelized_Block[i])
    # print(Code_String)
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

def indent_cpp_code(code: str, style: str = "LLVM") -> str:
    """Formats C++ code using clang-format."""
    try:
        result = subprocess.run(
            ["clang-format", f"--style={style}"], 
            input=code, 
            text=True, 
            capture_output=True, 
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Error formatting code:", e)
        return code

def identify_dependencies(loop_block, loop_index='i'):
    """
    Analyzes a loop block to determine if it is parallelizable.

    The heuristic assumes that:
      - Array accesses using the loop index (e.g. A[i]) are isolated to each iteration.
      - Any assignment to a variable without such indexing (or with a different index)
        may introduce a cross-iteration dependency.

    Returns:
        (parallelizable: bool, non_parallelizable_line: int or None)
    If parallelizable is True, non_parallelizable_line is None.
    If parallelizable is False, non_parallelizable_line indicates the first line where a dependency is detected.
    """
    lines = loop_block.split('\n')
    written_vars = set()

    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()
        # Skip empty or comment lines.
        if not stripped or stripped.startswith('//') or stripped.startswith('#'):
            continue

        # Look for an assignment operation.
        match = re.search(r'(\w+)(\s*\[[^\]]+\])?\s*=', line)
        if match:
            var = match.group(1)
            index_part = match.group(2)
            if index_part:
                # Normalize the index: remove spaces and the surrounding brackets.
                index_clean = index_part.strip()[1:-1].strip()
                # If the index is not exactly the loop index, we consider it a cross-iteration dependency.
                if index_clean != loop_index:
                    return False, line_num
            else:
                # No array index implies a global variable assignment that is likely loop-carried.
                if var in written_vars:
                    return False, line_num
                written_vars.add(var)

    # If no problematic assignments are found, assume the loop block may be parallelizable.
    return True, None

def Parinomo(SCode, core_type, ram_type, processors_count):

    # making a json file to store loops and their tilled version and parallelized version if avalible with complexity
    # to return at the end
    All_data = {}

    SCode = indent_cpp_code(SCode)

    Loop_Blocks = LoopBlocks(SCode)

    count = 1

    for loops in Loop_Blocks:

        All_data[count] = {}
        All_data[count]['Loop'] = loops

        if check_input_output(loops):
            array_type = determine_array_access_type(loops)
            if array_type != "Single variables":
                tile_size = calculate_tile_size(ram_type, array_type)
                tiled_loop = generate_tiled_loop(loops, tile_size)
                tiled_loop = indent_cpp_code(tiled_loop)
                All_data[count]['Tiled_Loop'] = tiled_loop
                All_data[count]['Parallelized_Loop'] = 'Not Parallelizable'
        else:
            ParallelBlock = indent_cpp_code(loops)

            Paralleizable_Flag, reason = identify_dependencies(ParallelBlock)

            if Paralleizable_Flag == True:
                if 'break' in ParallelBlock or 'return' in ParallelBlock:
                    All_data[count]['Parallelized_Loop'] = indent_cpp_code(Soft_Break(ParallelBlock)) + '\n' + ParallelBlock
                else:
                    # All_data[count]['Parallelized_Loop'] = indent_cpp_code(parallelizing_loop(ParallelBlock)) + '\n' + ParallelBlock
                    single_variable, array_variable = extract_loop_variables(ParallelBlock)
                    result = analyze_openmp_variables(ParallelBlock, single_variable, array_variable)
                    clauses = []
                    for category, vars_list in result.items():
                        if vars_list and category != "error":
                            if category == "reduction":
                                reducible_vars = [f"{var}" for var in vars_list]
                                if reducible_vars:
                                    clauses.append(f"reduction(+:{', '.join(reducible_vars)})")
                            else:
                                clauses.append(f"{category}({', '.join(vars_list)})")

                    reduction = Reduction_aaplication(ParallelBlock)

                    if reduction:
                        
                        reduction_clause = []
                        for line in reduction:
                            reduction_clause.append(f"{line}")

                        All_data[count]['Parallelized_Loop'] = indent_cpp_code(indent_cpp_code(f"#pragma omp parallel for {' '.join(clauses)} {' '.join(reduction_clause)}") + '\n' + ParallelBlock)
                    else:
                        All_data[count]['Parallelized_Loop'] = indent_cpp_code(indent_cpp_code(f"#pragma omp parallel for {' '.join(clauses)}") + '\n' + ParallelBlock)
                    All_data[count]['Tiled_Loop'] = 'Not Tiled'
            else:
                All_data[count]['Parallelized_Loop'] = 'Not Parallelizable ' + reason
                tile_size = calculate_tile_size(ram_type, array_type)
                tiled_loop = generate_tiled_loop(loops, tile_size)
                tiled_loop = indent_cpp_code(tiled_loop)
                All_data[count]['Tiled_Loop'] = tiled_loop

            

        Complexity_class , Complexity = Complexity_of_loop(loops)
        All_data[count]['Complexity'] = Complexity
        All_data[count]['Complexity_Class'] = Complexity_class

        count += 1

    # writing the data to the file
    file = open('P_code.txt', 'w')
    file.write(json.dumps(All_data, indent=4))
    file.close()

    return json.dumps(All_data, indent=4)