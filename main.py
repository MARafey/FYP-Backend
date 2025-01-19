import re
from typing import Dict, List, Tuple

def analyze_loop_parallelization(loop_string: str) -> Tuple[bool, List[str]]:
    """
    Analyzes a C/C++ for loop string to determine if it can be parallelized.
    
    Parameters:
        loop_string (str): String containing the for loop code
        
    Returns:
        Tuple[bool, List[str]]: (can_parallelize, reasons)
        - can_parallelize: Boolean indicating if the loop can be parallelized
        - reasons: List of reasons explaining the decision
    """
    reasons = []
    
    # Clean the input string
    loop_string = loop_string.strip()
    
    # Basic patterns that suggest loop-carried dependencies
    dependency_patterns = [
        (r'\[.+?\+.+?\]', "Array access with variable index"),
        (r'[^=]=[^=]', "Assignment operation"),
        (r'^\+{2}|--', "Increment/decrement operators"),
        (r'push_back|push|pop|insert|erase', "Container modifications"),
        (r'break|continue|return', "Loop control statements"),
        (r'scanf|cin|getline', "Input operations"),
        (r'printf|cout', "Output operations")
    ]
    
    # Check for loop initialization pattern
    init_pattern = r'for\s*\(\s*(?:int|size_t)?\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*\d+\s*;'
    if not re.search(init_pattern, loop_string):
        reasons.append("Non-standard loop initialization")
        return False, reasons
    
    # Check for dependencies
    for pattern, reason in dependency_patterns:
        if re.search(pattern, loop_string):
            reasons.append(f"Found potential dependency: {reason}")
    
    # Check for pointer arithmetic
    if '*' in loop_string and ('++' in loop_string or '--' in loop_string):
        reasons.append("Contains pointer arithmetic")
    
    # Check for function calls
    function_calls = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*\s*\(', loop_string)
    if function_calls:
        reasons.append("Contains function calls which may have side effects")
    
    # If we found any reasons against parallelization
    if reasons:
        return False, reasons
    
    # If we haven't found any issues, check for positive indicators
    positive_indicators = []
    
    # Check for common parallel patterns
    if re.search(r'for\s*\([^;]+;\s*[^;]+<\s*[^;]+;\s*[^)]+\)', loop_string):
        positive_indicators.append("Standard counting loop structure")
    
    if re.search(r'\[\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\]', loop_string):
        positive_indicators.append("Simple array access pattern")
    
    if positive_indicators:
        reasons.extend(positive_indicators)
        return True, reasons
    
    reasons.append("No clear parallelization benefit identified")
    return False, reasons

def get_optimization_suggestions(loop_string: str) -> List[str]:
    """
    Provides optimization suggestions for the loop if it can't be parallelized.
    
    Parameters:
        loop_string (str): String containing the for loop code
        
    Returns:
        List[str]: List of optimization suggestions
    """
    suggestions = []
    
    # Check for vectorization potential
    if re.search(r'\[\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\]', loop_string):
        suggestions.append("Consider SIMD vectorization for array operations")
    
    # Check for loop unrolling potential
    if not re.search(r'break|continue|return', loop_string):
        suggestions.append("Consider loop unrolling for better instruction pipelining")
    
    # Check for cache optimization potential
    if re.search(r'\[\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\+\s*\d+\s*\]', loop_string):
        suggestions.append("Consider cache blocking/tiling for better memory access patterns")
    
    return suggestions

# Example usage
loop_code = """
for (int i = 0; i < n; i++) {
    arr[i] = arr[i] * 2;
}
"""

can_parallelize, reasons = analyze_loop_parallelization(loop_code)
if can_parallelize:
    print("Loop can be parallelized!")
else:
    print("Loop cannot be parallelized.")
    
print("Reasons:", reasons)

# Get optimization suggestions if needed
suggestions = get_optimization_suggestions(loop_code)
print("Optimization suggestions:", suggestions)