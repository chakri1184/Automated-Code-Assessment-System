#include <stdio.h>

int main() {
    int a, b;
    scanf("%d %d", &a, &b);

    printf("%d\n", a + b);
    printf("%d\n", a - b);
    printf("%d\n", a * b);

    if (b != 0)
        printf("%f\n", (float)a / b);
    else
        printf("Error\n");

    return 0;
}