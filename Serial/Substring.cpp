#include <iostream>
#include <string>
using namespace std;

int findSubstring(const string &str, const string &substring)
{
    int strLength = str.length();
    int subLength = substring.length();

    // Iterate through the main string
    for (int i = 0; i <= strLength - subLength; i++)
    {
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
            return i; // Return the starting index
        }
    }
    return -1; // Substring not found
}

int main(int argc, char *argv[])
{
    string str = "Hello, this is a sample string.";
    string substring = "sample";

    int position = findSubstring(str, substring);

    return 0;
}
