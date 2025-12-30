#include <assert.h>
#include <stdio.h>

static long long sum_of_multiples(long long m, long long n) {
    long long max_range = n / m;
    return m * max_range * (max_range + 1) / 2;
}

static long long sum_of_multiples_of_either_3_or_5(long long n) {
    n -= 1;
    return sum_of_multiples(3, n) + sum_of_multiples(5, n)
           - sum_of_multiples(15, n);
}

int main(void) {
    assert(sum_of_multiples_of_either_3_or_5(10) == 23);
    printf("%lld\n", sum_of_multiples_of_either_3_or_5(1000));
    return 0;
}
