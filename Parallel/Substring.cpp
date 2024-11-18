#include <iostream>
#include <string>
#include <omp.h>
#include <atomic> // For atomic operations
using namespace std;

int findSubstring(const string &str, const string &substring)
{
    int strLength = str.length();
    int subLength = substring.length();

    atomic<int> position(-1); // Use atomic to handle concurrent writes

#pragma omp parallel for
    for (int i = 0; i <= strLength - subLength; i++)
    {
        // Skip if another thread has already found the substring
        if (position != -1)
            continue;

        int j;
        // Check if the substring matches at this position
        for (j = 0; j < subLength; j++)
        {
            if (str[i + j] != substring[j])
            {
                break;
            }
        }
        // If the whole substring matched
        if (j == subLength)
        {
            position.store(i, memory_order_relaxed); // Save the starting index
        }
    }
    return position.load(); // Substring not found if still -1
}

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        cout << "Usage: " << argv[0] << " <number_of_threads>" << endl;
        return -1;
    }

    omp_set_num_threads(stoi(argv[1]));

    string str = "Hello, this is a sample string.";
    string substring = "sample";

    int position = findSubstring(str, substring);

    return 0;
}
