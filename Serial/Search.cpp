#include <vector>
#include <iostream>
using namespace std;

int main(int argc, char *argv[])
{
    int N = stoi(argv[1]);

    vector<int> A(N, 1);

    for (int i = 0; i < N; i++)
    {
        A[i] = rand() % N;
    }

    // linear search
    int target = stoi(argv[2]);
    for (int i = 0; i < N; i++)
    {
        if (A[i] == target)
        {
            break;
        }
    }

    return 0;
}