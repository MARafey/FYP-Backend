#include <stdio.h>

void funcA()
{
    printf("Hello, World!\\n");
}

void funcB()
{
    funcA();
}

int main()
{
    funcB();
    return 0;
}