#!/bin/bash

SOURCE_DIR="Serial"
OUTPUT_DIR="Serial bin"

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Loop through all .cpp files in the source directory
for file in "$SOURCE_DIR"/*.cpp; do
    if [ -f "$file" ]; then
        # Get the base name of the file (without directory and extension)
        base_name=$(basename "$file" .cpp)
        # Compile the file
        g++ "$file" -o "$OUTPUT_DIR/$base_name"
        if [ $? -eq 0 ]; then
            echo "Compiled $file -> $OUTPUT_DIR/$base_name"
        else
            echo "Failed to compile $file"
        fi
    fi
done

echo " Serial Compilation complete."

#!/bin/bash

# Directory containing the C++ files
SOURCE_DIR="Parallel"
# Output directory for compiled files
OUTPUT_DIR="parallel bin"

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Loop through all .cpp files in the source directory
for file in "$SOURCE_DIR"/*.cpp; do
    if [ -f "$file" ]; then
        # Get the base name of the file (without directory and extension)
        base_name=$(basename "$file" .cpp)
        # Compile the file with OpenMP support
        g++ -fopenmp "$file" -o "$OUTPUT_DIR/$base_name"
        if [ $? -eq 0 ]; then
            echo "Compiled $file -> $OUTPUT_DIR/$base_name"
        else
            echo "Failed to compile $file"
        fi
    fi
done

echo " Parallel Compilation complete."
