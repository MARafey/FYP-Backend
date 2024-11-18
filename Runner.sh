cd 'Serial bin'

echo "Serial Execution"

touch 'output.txt'

echo "Graph" >> 'output.txt'
{ time ./Graph; } >> 'output.txt' 2>&1

echo "Matrix" >> 'output.txt'
{ time ./Matrix 150; } >> 'output.txt' 2>&1

echo "Multiplication" >> 'output.txt'
{ time ./Multiplication 150; } >> 'output.txt' 2>&1

echo "Search" >> 'output.txt'
{ time ./Search 500 243; } >> 'output.txt' 2>&1

echo "Sorting" >> 'output.txt'
{ time ./Sorting 500; } >> 'output.txt' 2>&1

echo "Substring" >> 'output.txt'
{ time ./Substring; } >> 'output.txt' 2>&1

cd ..

cd 'parallel bin'

TotalThreads=$(nproc)
touch 'output.txt'
echo "Parallel Execution" > 'output.txt'  # Start by clearing the output file

for ((i = 1; i <= TotalThreads; i++)); do
    echo "Threads: $i" >> 'output.txt'
    
    echo "Graph" >> 'output.txt'
    { time ./Graph "$i"; } 2>&1 | tee -a 'output.txt'
    
    echo "Matrix" >> 'output.txt'
    { time ./Matrix 150 "$i"; } 2>&1 | tee -a 'output.txt'
    
    echo "Multiplication" >> 'output.txt'
    { time ./Multiplication 150 "$i"; } 2>&1 | tee -a 'output.txt'
    
    echo "Search" >> 'output.txt'
    { time ./Search 500 243 "$i"; } 2>&1 | tee -a 'output.txt'
    
    echo "Sorting" >> 'output.txt'
    { time ./Sorting 500 "$i"; } 2>&1 | tee -a 'output.txt'
    
    echo "Substring" >> 'output.txt'
    { time ./Substring "$i"; } 2>&1 | tee -a 'output.txt'
done
