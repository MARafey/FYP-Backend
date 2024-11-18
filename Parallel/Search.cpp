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

    // linear search
    int target = stoi(argv[2]);

    int X = -1;
#pragma omp parallel for shared(X)
    for (int i = 0; i < N; i++)
    {
        if (A[i] == target)
        {
            X = i;
        }
        if (X != -1)
        {
            i = N;
        }
    }

    return 0;
}