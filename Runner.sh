cd 'Serial bin'

echo "Serial Execution"

touch 'output.txt'

echo "Graph" >> 'output.txt'
time ./Graph >> 'output.txt'
echo "Matrix" >> 'output.txt'
time ./Matrix 150 >> 'output.txt'
echo "Multiplication" >> 'output.txt'
time ./Multiplication 150 >> 'output.txt'
echo "Search" >> 'output.txt'
time ./Search 500 243 >> 'output.txt'
echo "Sorting" >> 'output.txt'
time ./Sorting 500 >> 'output.txt'
echo "Substring" >> 'output.txt'
time ./Substring >> 'output.txt'

cd ..

cd 'parallel bin'

TotalThreads=$(nproc)
touch 'output.txt'
echo "Parallel Execution"
for ((i = 1; i <= TotalThreads; i++))
done
    echo "Graph" >> 'output.txt'
    time ./Graph "$i" >> 'output.txt'
    echo "Matrix" >> 'output.txt'
    time ./Matrix 150 "$i" >> 'output.txt'
    echo "Multiplication" >> 'output.txt'
    time ./Multiplication 150 "$i" >> 'output.txt'
    echo "Search" >> 'output.txt'
    time ./Search 500 243 "$i" >> 'output.txt'
    echo "Sorting" >> 'output.txt'
    time ./Sorting 500 "$i" >> 'output.txt'
    echo "Substring" >> 'output.txt'
    time ./Substring "$i" >> 'output.txt'
done
