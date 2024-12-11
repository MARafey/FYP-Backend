from Parinomo import *


# code = '''
# #include <iostream>
# #include <vector>
# #include <algorithm>

# using namespace std;

# int main() {
#     int n;
#     cin >> n;
#     vector<int> numbers(n);

#     for (int i = 0; i < n; i++) cin >> numbers[i];
#     sort(numbers.begin(), numbers.end());

#     vector<vector<int>> result;
#     for (int i = 0; i < n - 2; i++) {
#         if (i > 0 && numbers[i] == numbers[i - 1]) continue;
#         int left = i + 1, right = n - 1;
#         while (left < right) {
#             int sum = numbers[i] + numbers[left] + numbers[right];
#             if (sum == 0) {
#                 result.push_back({numbers[i], numbers[left], numbers[right]});
#                 while (left < right && numbers[left] == numbers[left + 1]) left++;
#                 while (left < right && numbers[right] == numbers[right - 1]) right--;
#                 left++;
#                 right--;
#             } else if (sum < 0) {
#                 left++;
#             } else {
#                 right--;
#             }
#         }
#     }

#     for (const auto& triplet : result) {
#         for (int num : triplet) cout << num << " ";
#         cout << endl;
#     }

#     return 0;
# }
# '''

# print(Parinomo(code))

# print("--------------------")


# code = '''
# // C++ program to find the sum of all elements in an array
# #include <iostream>
# using namespace std;

# int main()
# {
#     // Initialize the array
#     int arr[] = { 1, 2, 3, 4, 5 };

#     // size of the array
#     int n = sizeof(arr) / sizeof(arr[0]);

#     // sum of the array elements
#     int sum = 0;
#     for (int i = 0; i < n; i++)
#         sum++;

#     cout << "Sum: " << sum << endl;

#     return 0;
# }
# '''

code = '''
for (int i = 0; i < n; i++) {
    int k = 0,l;
    k++;
    j++;
}
'''

# print(Parinomo(code))

print(Variable_in_Loop(code))