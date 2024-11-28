#include <iostream>
#include <vector>
using namespace std;

long long int Sum(vector<int> v)
{
    long long int x = 0;
    for (int i = 0; i < v.size(); i++)
    {
        x += v[i];
    }

    for (int i = 0; i < v.size(); i++)
    {
        for (int j = 0; j < 5; j++)
        {
            x += v[i];
        }
    }
    return x;
}

int Main()
{
    int N = 50;
    vector<int> v(N);
    for (int i = 0; i < N; i++)
    {
        v[i] = i;
    }

    cout << Sum(v) << endl;
}