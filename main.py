from Parinomo import Parinomo, indent_cpp_code, LoopBlocks
Ram = 2
core_type = 'i5'
Processpr = 8

# reading file to get code
file = open('CodeFiles/code5.txt', 'r')
Scode = file.read()
file.close()

P_code = Parinomo(Scode, core_type,Ram, Processpr)
