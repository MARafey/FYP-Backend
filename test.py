import sys
from antlr4 import *
from antlr4.TokenStreamRewriter import TokenStreamRewriter
from Files.CLexer import CLexer
from Files.CParser import CParser
from Files.CListener import CListener
from antlr4.tree.Trees import Trees
from graphviz import Digraph

class ForLoopCommenter(CListener):
    def __init__(self, tokens):
        self.tokens = tokens
        self.rewriter = TokenStreamRewriter(tokens)

    def enterForStatement(self, ctx):
        self.rewriter.insertBefore(ctx.start, "// This is a for loop\n")

def visualize_tree(tree, parser):
    dot = Digraph(comment='AST')
    dot.attr(rankdir='TB')

    def add_node(tree, parent=None):
        node_id = str(id(tree))
        label = Trees.getNodeText(tree, parser.ruleNames)
        dot.node(node_id, label)
        
        if parent:
            dot.edge(str(id(parent)), node_id)
        
        for i in range(tree.getChildCount()):
            child = tree.getChild(i)
            add_node(child, tree)

    add_node(tree)
    return dot

def main(argv):
    if len(argv) < 2:
        print("Usage: python script.py <input_file.c>")
        sys.exit(1)

    input_file = argv[1]
    input_stream = FileStream(input_file)
    lexer = CLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = CParser(stream)
    tree = parser.compilationUnit()

    # Modify the AST
    listener = ForLoopCommenter(stream)
    walker = ParseTreeWalker()
    walker.walk(listener, tree)

    # Get the modified code
    modified_code = listener.rewriter.getDefaultText()

    # Save the modified code to a new file
    output_filename = 'modified_' + input_file
    with open(output_filename, 'w') as f:
        f.write(modified_code)
    print(f"Modified code saved as {output_filename}")

if __name__ == '__main__':
    main(sys.argv)