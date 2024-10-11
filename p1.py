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

# Traverse the AST and detect loop nodes
def detect_loops_in_ast(node, loop_positions):
    if hasattr(node, 'children'):
        for child in node.children:
            # Detect 'for', 'while', 'do' loops based on TerminalNode
            if isinstance(child, TerminalNode):
                if child.getText() in ['for', 'while', 'do']:
                    # Append the starting position of the loop in the original code
                    loop_positions.append(child.symbol.start)
            # Recursively check child nodes
            detect_loops_in_ast(child, loop_positions)

# Insert code at specific positions in the original source code
def insert_code_at_positions(original_code, positions, code_to_insert):
    # Insert the code before each loop, starting from the last position to preserve the order
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

    # Detect loops in the AST and store their positions
    loop_positions = []
    detect_loops_in_ast(ast, loop_positions)

    # Insert "Hello world" before the detected loops in the original code
    modified_code = insert_code_at_positions(original_code, loop_positions, 'std::cout << "Hello world" << std::endl;\n')

    # Write the modified code to a new file
    write_code_to_file(output_file, modified_code)
    print(f"Updated file saved as {output_file}.")

if __name__ == "__main__":
    main(sys.argv)
