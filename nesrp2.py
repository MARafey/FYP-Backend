import sys
from antlr4 import *
from CPP14Lexer import CPP14Lexer
from CPP14Parser import CPP14Parser
from antlr4.tree.Tree import TerminalNode  # Import TerminalNode for checking terminal nodes

# Function to create AST
def create_ast(input_stream):
    lexer = CPP14Lexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = CPP14Parser(stream)
    tree = parser.translationUnit()  # The root of the AST
    return tree

# Traverse the AST and detect loop nodes and function calls
def detect_loops_and_functions(node, loop_positions, function_positions, inside_loop=False, loop_inserted=False, function_inserted=False):
    if hasattr(node, 'children'):
        for child in node.children:
            # Detect 'for', 'while', 'do' loops
            if isinstance(child, TerminalNode):
                if child.getText() in ['for', 'while', 'do']:
                    if not inside_loop:  # Only insert before the first top-level loop
                        loop_positions.append(child.symbol.start)  # Record position for top-level loop
                        loop_inserted = True
                    inside_loop = True  # Set flag to indicate we're inside a loop
                elif child.getText() == '}':  # End of a loop
                    inside_loop = False  # Reset the flag

                # Check for function calls (using the context for function identifier)
                if child.getText().isidentifier() and not function_inserted:  # Check if it's a valid identifier (function call)
                    function_positions.append(child.symbol.start)
                    function_inserted = True

            # Recursively check child nodes
            detect_loops_and_functions(child, loop_positions, function_positions, inside_loop, loop_inserted, function_inserted)

# Insert code at specific positions in the original source code
def insert_code_at_positions(original_code, positions, code_to_insert):
    # Insert the code before each position, starting from the last position to preserve the order
    for pos in sorted(positions, reverse=True):
        original_code = original_code[:pos] + code_to_insert + original_code[pos:]
    return original_code

# Write the modified code to a new file
def write_code_to_file(output_file, modified_code):
    with open(output_file, 'w') as file:
        file.write(modified_code)

# Read original C++ code from a file
def read_original_code(input_file):
    with open(input_file, 'r') as file:
        return file.read()

# Main function
def main(args):
    if len(args) < 2:
        print("Usage: python3 generate_ast.py <input_file.cpp> [output_file.cpp]")
        return

    input_file = args[1]
    output_file = args[2] if len(args) > 2 else 'updated_' + input_file

    # Read the original C++ code
    original_code = read_original_code(input_file)

    # Create AST from the original C++ code
    input_stream = InputStream(original_code)
    ast = create_ast(input_stream)

    # Detect loops and function calls in the AST and store their positions
    loop_positions = []
    function_positions = []
    detect_loops_and_functions(ast, loop_positions, function_positions)

    # Insert "Hello world" before the detected loops in the original code, only once for nested loops
    if loop_positions:
        modified_code = insert_code_at_positions(original_code, [loop_positions[0]], 'std::cout << "Hello world" << std::endl;\n')
    else:
        modified_code = original_code

    # Insert "Hello world" before the first function call only if there are function calls
    if function_positions:
        modified_code = insert_code_at_positions(modified_code, [function_positions[0]], 'std::cout << "Hello world" << std::endl;\n')

    # Write the modified code to a new file
    write_code_to_file(output_file, modified_code)
    print(f"Updated file saved as {output_file}.")

if __name__ == "__main__":
    main(sys.argv)

