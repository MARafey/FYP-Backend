#include <vector>
#include <iostream>
#include <omp.h>
using namespace std;

int main(int argc, char *argv[])
{
    int N = stoi(argv[1]);

    omp_set_num_threads(stoi(argv[2]));

    vector<vector<int>> A(N, vector<int>(N, 1));
    vector<vector<int>> B(N, vector<int>(N, 1));
    vector<vector<int>> C(N, vector<int>(N, 0));

#pragma omp parallel for collapse(2)
    for (int i = 0; i < N; i++)
    {
        for (int j = 0; j < N; j++)
        {
            C[i][j] = A[i][j] + B[i][j];
        }
    }

    return 0;
}