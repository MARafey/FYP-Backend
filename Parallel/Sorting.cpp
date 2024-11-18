#include <vector>
#include <iostream>
#include <omp.h>
using namespace std;

int main(int argc, char *argv[])
{
    int N = stoi(argv[1]);
    omp_set_num_threads(stoi(argv[2]));

    vector<int> A(N, 1);

#pragma omp parallel for
    for (int i = 0; i < N; i++)
    {
        A[i] = rand() % N;
    }

// Bubble Sort
#pragma omp parallel for
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