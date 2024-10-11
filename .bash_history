: 1728661172:0;mkdir Files
: 1728661172:0;wget https://raw.githubusercontent.com/antlr/antlr4/master/doc/grammars/cpp/CPP14.g4
: 1728661172:0;wget https://raw.githubusercontent.com/antlr/grammars-v4/master/cpp/CPP14Lexer.g4
: 1728661172:0;wget https://raw.githubusercontent.com/antlr/grammars-v4/master/cpp/CPP14Parser.g4
: 1728661173:0;# moving all file to Files directory
: 1728661173:0;mv CPP14*.* Files/
: 1728661173:0;antlr4 -Dlanguage=Python3 Files/CPP14Lexer.g4 Files/CPP14Parser.g4 Files/CPP14.g4
: 1728661181:0;clear
: 1728661191:0;wget https://raw.githubusercontent.com/antlr/antlr4/master/doc/grammars/cpp/CPP14.g4
: 1728661381:0;wget https://raw.githubusercontent.com/antlr/grammars-v4/refs/heads/master/antlr/antlr4/examples/CPP14.g4
: 1728661391:0;mv CPP14*.* Files/
: 1728661398:0;antlr4 -Dlanguage=Python3 Files/CPP14Lexer.g4 Files/CPP14Parser.g4 Files/CPP14.g4
: 1728661426:0;clear
: 1728661432:0;python main.py example.cpp
: 1728661604:0;./Runer.sh
: 1728661614:0;clear
: 1728661615:0;ls
: 1728661636:0;wget https://raw.githubusercontent.com/antlr/grammars-v4/refs/heads/master/antlr/antlr4/examples/CPP14.g4
: 1728661636:0;wget https://raw.githubusercontent.com/antlr/grammars-v4/master/cpp/CPP14Lexer.g4
: 1728661636:0;wget https://raw.githubusercontent.com/antlr/grammars-v4/master/cpp/CPP14Parser.g4
: 1728661636:0;wget https://raw.githubusercontent.com/antlr/grammars-v4/master/c/C.g4
: 1728661644:0;mkdir Files
: 1728661650:0;mv *.g4 Files/
: 1728661656:0;antlr4 -Dlanguage=Python3 Files/CPP14Lexer.g4 Files/CPP14Parser.g4 Files/CPP14.g4 Files/C.g4
: 1728661661:0;clear
: 1728661667:0;python main.py example.c
: 1728661709:0;pip install matplotlib networkx antlr4-python3-runtime
: 1728661728:0;clear
: 1728661733:0;python main.py example.c
: 1728661929:0;pip install pydot
: 1728661937:0;clear
: 1728661939:0;pip install pydot
: 1728661943:0;python main.py example.c
: 1728662119:0;Traceback (most recent call last):
: 1728662121:0;IndexError: list index out of range
: 1728662122:0;clear
: 1728662127:0;sudo apt-get install graphviz
: 1728662164:0;clear
: 1728662170:0;python main.py example.c
: 1728662219:0;clear
: 1728662221:0;python main.py example.c
: 1728662334:0;clear
: 1728662344:0;pip install graphviz
: 1728662348:0;clear
: 1728662351:0;python main.py
: 1728662370:0;clear
: 1728662388:0;python main.py example.c
: 1728662430:0;pip install pyvis
: 1728662444:0;clear
: 1728662447:0;python main.py example.c
: 1728662784:0;clear
: 1728662789:0;pip install jinja2
: 1728662798:0;pip install --upgrade pyvis
: 1728662800:0;clear
: 1728662803:0;python main.py example.c
: 1728663104:0;clear
: 1728663178:0;python test.py example.c
: 1728663551:0;clear
: 1728663553:0;python test.py example.c
: 1728663787:0;clear
: 1728663788:0;python test.py example.c
: 1728663896:0;clea
: 1728663897:0;clear
: 1728664322:0;python test.py example.c
: 1728664363:0;clear
: 1728664366:0;python test.py example.c
: 1728664417:0;clear
: 1728664420:0;git init
: 1728664422:0;clear
: 1728664427:0;git add .
: 1728664438:0;git commit -m "Adding bash file to make AST"
: 1728664449:0;git add remote origin https://github.com/MARafey/FYP.git
: 1728664474:0;git remote add origin https://github.com/MARafey/FYP.git
: 1728664476:0;clear
: 1728664537:0;git checkout -b AST
: 1728664543:0;git brach
: 1728664546:0;git bracnh
: 1728664561:0;git branch
