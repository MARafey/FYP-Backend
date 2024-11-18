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

    // Bubble Sort
    for (int i = 0; i < N; i++)
    {
        for (int j = 0; j < N - i - 1; j++)
        {
            if (A[j] > A[j + 1])
            {
                int temp = A[j];
                A[j] = A[j + 1];
                A[j + 1] = temp;
            }
        }
    }

    return 0;
}