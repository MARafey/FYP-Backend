import sys
from antlr4 import *
from Files.CLexer import CLexer
from Files.CParser import CParser
from antlr4.tree.Trees import Trees
from graphviz import Digraph

def visualize_tree(tree, parser):
    dot = Digraph(comment='AST')
    dot.attr(rankdir='TB')

    def add_node(tree, parent=None):
        node_id = str(id(tree))
        label = Trees.getNodeText(tree, parser.ruleNames)  # Use parser.ruleNames instead of parser
        dot.node(node_id, label)
            
        if parent:
            dot.edge(str(id(parent)), node_id)
            
        for i in range(tree.getChildCount()):
            child = tree.getChild(i)
            add_node(child, tree)

    add_node(tree)
    return dot

def main(argv):
    input_stream = FileStream(argv[1])
    lexer = CLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = CParser(stream)
    tree = parser.compilationUnit()

    # Generate the AST visualization
    dot = visualize_tree(tree, parser)
    
    # Save the visualization as a PDF
    output_file = 'ast_visualization'
    dot.render(output_file, view=True, format='pdf', cleanup=True)
    print(f"AST visualization saved as {output_file}.pdf")

if __name__ == '__main__':
    main(sys.argv)