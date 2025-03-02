# from Parinomo import Parinomo, indent_cpp_code, LoopBlocks
# Ram = 2
# core_type = 'i5'
# Processpr = 8
#
# # reading file to get code
# file = open('CodeFiles/code2.txt', 'r')
# Scode = file.read()
# file.close()
#
# P_code = Parinomo(Scode, core_type,Ram, Processpr)

import re

def identify_dependencies(loop_block, loop_index='i'):
    """
    Analyzes a loop block to determine if it is parallelizable.

    The heuristic assumes that:
      - Array accesses using the loop index (e.g. A[i]) are isolated to each iteration.
      - Any assignment to a variable without such indexing (or with a different index)
        may introduce a cross-iteration dependency.

    Returns:
        (parallelizable: bool, non_parallelizable_line: int or None)
    If parallelizable is True, non_parallelizable_line is None.
    If parallelizable is False, non_parallelizable_line indicates the first line where a dependency is detected.
    """
    lines = loop_block.split('\n')
    written_vars = set()

    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()
        # Skip empty or comment lines.
        if not stripped or stripped.startswith('//') or stripped.startswith('#'):
            continue

        # Look for an assignment operation.
        match = re.search(r'(\w+)(\s*\[[^\]]+\])?\s*=', line)
        if match:
            var = match.group(1)
            index_part = match.group(2)
            if index_part:
                # Normalize the index: remove spaces and the surrounding brackets.
                index_clean = index_part.strip()[1:-1].strip()
                # If the index is not exactly the loop index, we consider it a cross-iteration dependency.
                if index_clean != loop_index:
                    return False, line_num
            else:
                # No array index implies a global variable assignment that is likely loop-carried.
                if var in written_vars:
                    return False, line_num
                written_vars.add(var)

    # If no problematic assignments are found, assume the loop block may be parallelizable.
    return True, None


# Example usage:

# This block should be parallelizable because each assignment uses the loop index 'i'.
loop_block_parallel = """
for (int i = 0; i < N; i++) {
    C[i] = A[i+1] + B[i+1];
    A[i] = C[i] * 2;
}
"""

# This block is parallelizable because 'sum' is assigned without an index but does not introduce cross-iteration dependency.
loop_block_non_parallel = """
for (int i = 0; i < N; i++) {
    sum = sum + A[i];
}
"""

parallelizable, reason = identify_dependencies(loop_block_parallel)
print("Parallelizable (expected True):", parallelizable)
if not parallelizable:
    print("Non-parallelizable due to dependency on line:", reason)

parallelizable, reason = identify_dependencies(loop_block_non_parallel)
print("Parallelizable (expected True):", parallelizable)
if not parallelizable:
    print("Non-parallelizable due to dependency on line:", reason)
