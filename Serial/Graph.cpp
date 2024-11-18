#include <iostream>
#include <vector>
#include <stack>
using namespace std;

const int N = 20;

// Function to perform DFS
bool dfs(vector<vector<int>> &matrix, int startX, int startY, int targetX, int targetY, vector<vector<bool>> &visited)
{
    stack<pair<int, int>> s;
    s.push({startX, startY});
    visited[startX][startY] = true;

    // Directions for moving in a 2D grid (up, down, left, right)
    vector<pair<int, int>> directions = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}};

    while (!s.empty())
    {
        auto [x, y] = s.top();
        s.pop();

        if (x == targetX && y == targetY)
        {
            return true;
        }

        for (auto &[dx, dy] : directions)
        {
            int nx = x + dx, ny = y + dy;
            if (nx >= 0 && nx < N && ny >= 0 && ny < N && matrix[nx][ny] == 1 && !visited[nx][ny])
            {
                visited[nx][ny] = true;
                s.push({nx, ny});
            }
        }
    }

    return false;
}

int main(int argc, char *argv[])
{
    // Initialize a 20x20 adjacency matrix
    vector<vector<int>> matrix(N, vector<int>(N, 1)); // 1 means passable, 0 means blocked

    // Example of blocking some nodes
    matrix[5][5] = 0;
    matrix[5][6] = 0;
    matrix[5][7] = 0;

    int targetX = 15, targetY = 15; // Example target node

    // Iterate over all possible start nodes
    for (int startX = 0; startX < N; startX++)
    {
        for (int startY = 0; startY < N; startY++)
        {
            if (matrix[startX][startY] == 1)
            {                                                            // Only consider valid start nodes
                vector<vector<bool>> visited(N, vector<bool>(N, false)); // Reset visited for each start node
                bool canReach = dfs(matrix, startX, startY, targetX, targetY, visited);
            }
        }
    }

    return 0;
}
