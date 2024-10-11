import sys
from antlr4 import *
from antlr4.tree.Tree import TerminalNodeImpl
from Files.CLexer import CLexer
from Files.CParser import CParser

def add_comment_before_for_loops(tree):
    for i in range(tree.getChildCount()):
        child = tree.getChild(i)
        if isinstance(child, CParser.StatementContext):  # Change this line
            # Create a comment node
            comment = f"// Comment: This is a for loop\n"
            # Create a new terminal node for the comment
            comment_node = TerminalNodeImpl(CommonToken(1, comment))
            # Insert the comment node before the for loop
            tree.children.insert(i, comment_node)
            i += 1  # Increment the index to skip the newly added comment in the next iteration
        # Recursively process children
        add_comment_before_for_loops(child)

def write_modified_ast_to_file(tree, filename):
    with open(filename, 'w') as f:
        f.write(tree.toStringTree())  # Adjust this method if you need a different representation

def main(argv):
    # Parse the input C file
    input_stream = FileStream(argv[1])
    lexer = CLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = CParser(stream)
    tree = parser.compilationUnit()

    # Add comments before for loops
    add_comment_before_for_loops(tree)

    # Save the modified AST to a new file
    write_modified_ast_to_file(tree, 'modified_ast.c')

if __name__ == '__main__':
    main(sys.argv)
