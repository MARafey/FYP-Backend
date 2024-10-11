sudo apt update
sudo apt install default-jdk
cd /usr/local/lib
sudo curl -O https://www.antlr.org/download/antlr-4.13.1-complete.jar

echo 'export CLASSPATH=".:/usr/local/lib/antlr-4.13.1-complete.jar:$CLASSPATH"' >> ~/.bashrc
echo 'alias antlr4="java -Xmx500M -cp \"/usr/local/lib/antlr-4.13.1-complete.jar:$CLASSPATH\" org.antlr.v4.Tool"' >> ~/.bashrc
echo 'alias grun="java -Xmx500M -cp \"/usr/local/lib/antlr-4.13.1-complete.jar:$CLASSPATH\" org.antlr.v4.gui.TestRig"' >> ~/.bashrc


pip install antlr4-python3-runtime

source ~/.bashrc

mkdir Files

wget https://raw.githubusercontent.com/antlr/grammars-v4/refs/heads/master/antlr/antlr4/examples/CPP14.g4
wget https://raw.githubusercontent.com/antlr/grammars-v4/master/cpp/CPP14Lexer.g4
wget https://raw.githubusercontent.com/antlr/grammars-v4/master/cpp/CPP14Parser.g4
wget https://raw.githubusercontent.com/antlr/grammars-v4/master/c/C.g4

# moving all file to Files directory
mv CPP14*.* Files/
mv *.g4 Files/

antlr4 -Dlanguage=Python3 Files/CPP14Lexer.g4 Files/CPP14Parser.g4 Files/CPP14.g4 Files/C.g4
pip install matplotlib networkx antlr4-python3-runtime pydot
sudo apt-get install graphviz
pip install pyvis
