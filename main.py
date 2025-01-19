from Parinomo import Parinomo, indent_cpp_code, LoopBlocks


Ram = 2
core_type = 'i5'
Processpr = 8

# reading file to get code
file = open('CodeFiles/code2.txt', 'r')
Scode = file.read()
file.close()

P_code = Parinomo(Scode, core_type,Ram, Processpr)

'''
import re
from typing import Any


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
                b. multiple dimension variables have complexity 2
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


example_loop = """
for (int i = 0; i < r1; ++i) {
        for (int j = 0; j < c2; ++j) {
            for (int k = 0; k < c1; ++k) {
                mult[i][j] += a[i][k] * b[k][j];
            }
        }
    }
"""
print("Complexity = ",Complexity_of_loop(example_loop))

example_loop = """
for (int i =0; i < 10; i++) {
sum += arr[i];
}
"""
print("Complexity = ",Complexity_of_loop(example_loop))

example_loop = """
for (int i =0; i < 1000000; i++) {
sum += arr[i];
}
"""
print("Complexity = ",Complexity_of_loop(example_loop))


example_loop = """
for (int i =0; i < N; i++) {
sum += arr[i];
}
"""
print("Complexity = ",Complexity_of_loop(example_loop))


example_loop = """
for (int i =0; i < 10; i++) {
}
"""
print("Complexity = ",Complexity_of_loop(example_loop))
'''