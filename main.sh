[ -d "Serial bin" ] && rm -r "Serial bin"
[ -d "parallel bin" ] && rm -r "parallel bin"
find . -type f -name "*.csv" -exec rm -f {} +

./Compiler.sh
./Runner.sh
python3 Serial_Table_Creation.py
python3 Parallel_Table_Creation.py