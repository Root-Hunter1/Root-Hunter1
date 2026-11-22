def fibonacci(n):
    """Return nth Fibonacci number using bottom-up dynamic programming."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n < 2:
        return n
    previous, current = 0, 1
    for _ in range(2, n + 1):
        previous, current = current, previous + current
    return current


def climbing_stairs(number):
    """Count ways to climb number steps taking one or two steps."""
    if number < 0:
        return 0
    if number == 0:
        return 1
    previous, current = 1, 1
    for _ in range(1, number):
        previous, current = current, previous + current
    return current


def longest_common_subsequence(left, right):
    """Return the length of the longest common subsequence."""
    table = [[0] * (len(right) + 1) for _ in range(len(left) + 1)]
    for i in range(1, len(left) + 1):
        for j in range(1, len(right) + 1):
            if left[i - 1] == right[j - 1]:
                table[i][j] = table[i - 1][j - 1] + 1
            else:
                table[i][j] = max(table[i - 1][j], table[i][j - 1])
    return table[len(left)][len(right)]


def coin_change(coins, amount):
    """Return the minimum number of coins needed to make amount."""
    minimum = [amount + 1] * (amount + 1)
    minimum[0] = 0
    for total in range(1, amount + 1):
        for coin in coins:
            if coin <= total:
                minimum[total] = min(minimum[total], 1 + minimum[total - coin])
    return -1 if minimum[amount] > amount else minimum[amount]


if __name__ == "__main__":
    print(fibonacci(10))
    print(climbing_stairs(5))
    print(longest_common_subsequence("ABCBDAB", "BDCAB"))
    print(coin_change([1, 2, 5], 11))
