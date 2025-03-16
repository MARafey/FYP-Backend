from Parinomo import Parinomo, indent_cpp_code, LoopBlocks
Ram = 2
core_type = 'i5'
Processpr = 8

# reading file to get code
file = open('CodeFiles/code.txt', 'r')
Scode = file.read()
file.close()

P_code = Parinomo(Scode, core_type,Ram, Processpr)
# import re

# def extract_loop_variables(code):
#     """
#     Extracts variables from C/C++ loop blocks, categorizing them as single or array variables.
    
#     Args:
#         code (str): A string containing C/C++ loop code
        
#     Returns:
#         tuple: (single_variables, array_variables) lists containing variable names
#     """
#     # Remove C-style comments
#     code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
#     code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
    
#     # Find all variable declarations
#     declarations = re.findall(r'\b(?:int|float|double|char|bool|long|short|unsigned|void|auto)\s+([a-zA-Z_][a-zA-Z0-9_]*)', code)
    
#     # Find all variables used in the code
#     # This looks for identifiers that aren't part of a keyword or function call
#     all_identifiers = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b(?!\s*\()', code)
    
#     # Remove C/C++ keywords
#     keywords = ['for', 'if', 'else', 'while', 'do', 'switch', 'case', 'break', 'continue',
#                 'return', 'int', 'float', 'double', 'char', 'bool', 'void', 'long', 'short',
#                 'unsigned', 'signed', 'const', 'static', 'struct', 'enum', 'class', 'auto']
#     all_identifiers = [ident for ident in all_identifiers if ident not in keywords]
    
#     # Find array access patterns: identifiers followed by square brackets
#     array_pattern = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\[')
#     array_variables = list(set(array_pattern.findall(code)))
    
#     # All other variables are single variables
#     single_variables = list(set(all_identifiers) - set(array_variables))
    
#     # Add declared variables that might not be used
#     single_variables = list(set(single_variables + declarations))
    
#     # Sort lists for consistent output
#     single_variables.sort()
#     array_variables.sort()
    
#     return single_variables, array_variables


# def analyze_openmp_variables(code, single_variables, array_variables):
#     """
#     Analyzes loop variables to determine their OpenMP clause classification
#     (shared, private, firstprivate, lastprivate)
    
#     Args:
#         code (str): C/C++ loop code
#         single_variables (list): List of single variables
#         array_variables (list): List of array variables
        
#     Returns:
#         dict: Dictionary containing lists of variables for each OpenMP clause
#     """
#     # Remove C-style comments
#     code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
#     code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
    
#     # Extract code inside the loop body (between curly braces)
#     loop_body_match = re.search(r'for\s*\([^)]*\)\s*{(.*?)}', code, re.DOTALL)
#     if not loop_body_match:
#         return {"error": "No valid loop body found"}
    
#     loop_body = loop_body_match.group(1)
    
#     # Extract loop control variable
#     loop_control_match = re.search(r'for\s*\(\s*(?:int\s+)?([a-zA-Z_][a-zA-Z0-9_]*)', code)
#     if not loop_control_match:
#         return {"error": "Could not identify loop control variable"}
    
#     loop_var = loop_control_match.group(1)
    
#     # Initialize result categories
#     result = {
#         "shared": [],
#         "private": [loop_var],  # Loop control variable is always private
#         "firstprivate": [],
#         "lastprivate": [],
#         "reduction": []
#     }
    
#     # Find all variables declared inside the loop
#     declared_inside = re.findall(r'\b(?:int|float|double|char|bool|long|short|unsigned|void|auto)\s+([a-zA-Z_][a-zA-Z0-9_]*)', loop_body)
    
#     # All variables declared inside the loop are private
#     result["private"].extend(declared_inside)
    
#     # Check each single variable
#     for var in single_variables:
#         if var in declared_inside or var == loop_var:
#             continue  # Already handled
            
#         # Check if read before write (firstprivate candidate)
#         lines = loop_body.split('\n')
#         read_first = False
#         written = False
        
#         for line in lines:
#             # Look for read operations (variable appears on right side of assignment or in expressions)
#             read_match = re.search(rf'[=|+|\-|*|/|%|&|\||^|>|<|!|?|:|\s]\s*{var}\b', line) or \
#                          re.search(rf'[+|\-|*|/|%|&|\||^|>|<|!|?|:|\(]\s*{var}\b', line) or \
#                          re.search(rf'\b{var}[+|\-|+]{2}', line)  # increment/decrement
            
#             # Look for write operations (variable appears on left side of assignment)
#             write_match = re.search(rf'\b{var}\s*(?:[+|\-|*|/|%|&|\||^])?=', line) or \
#                           re.search(rf'\b{var}[+|\-]{2}', line)  # increment/decrement
            
#             if read_match and not written:
#                 read_first = True
#             if write_match:
#                 written = True
                
#         # Check if written in the last iteration (lastprivate candidate)
#         last_iter_usage = re.search(rf'\b{var}\s*(?:[+|\-|*|/|%|&|\||^])?=', lines[-1]) or \
#                           re.search(rf'\b{var}[+|\-]{2}', lines[-1])
                
#         # Check for reduction patterns
#         reduction_match = re.search(rf'\b{var}\s*(?:[+|\-|*|/|%|&|\|])?=\s*{var}\b', loop_body)
        
#         # Assign to appropriate category
#         if reduction_match:
#             result["reduction"].append(var)
#         elif read_first and written:
#             result["firstprivate"].append(var)
#         elif last_iter_usage:
#             result["lastprivate"].append(var)
#         elif written:
#             result["private"].append(var)
#         else:
#             result["shared"].append(var)
    
#     # Handle array variables - generally shared unless clear pattern indicates otherwise
#     for var in array_variables:
#         # Check if the array is only read from
#         write_to_array = re.search(rf'\b{var}\s*\[[^\]]*\]\s*(?:[+|\-|*|/|%|&|\||^])?=', loop_body) or \
#                          re.search(rf'\b{var}\s*\[[^\]]*\][+|\-]{2}', loop_body)
                         
#         if not write_to_array:
#             result["shared"].append(var)
#         else:
#             # Check if array modifications depend on loop variable
#             loop_var_dependent = re.search(rf'\b{var}\s*\[.*\b{loop_var}\b.*\]', loop_body)
#             if loop_var_dependent:
#                 # If each iteration writes to different indices (loop var is used in index)
#                 result["shared"].append(var)
#             else:
#                 # If we're potentially writing to the same indices
#                 result["shared"].append(var)  # Still shared but with potential race conditions
                
#     # Remove duplicates and sort
#     for category in result:
#         result[category] = sorted(list(set(result[category])))
        
#     return result

# # Example usage
# code = '''
# for (int i = 0; i < 10; i++){
#     a += 1;
#     b++;
#     a += a+b;
#     int d;
#     arr[i]++;
#     bsc[i][j] += a;
# }
# '''
# single_variables, array_variables = extract_loop_variables(code)
# result = analyze_openmp_variables(code, single_variables, array_variables)
# print("OpenMP pragma suggestion:")
# print("#pragma omp parallel for", end=" ")

# clauses = []
# for category, vars_list in result.items():
#     if vars_list and category != "error":
#         if category == "reduction":
#             reducible_vars = [f"{var}" for var in vars_list]
#             if reducible_vars:
#                 clauses.append(f"reduction(+:{', '.join(reducible_vars)})")
#         else:
#             clauses.append(f"{category}({', '.join(vars_list)})")
            
# print(" ".join(clauses))