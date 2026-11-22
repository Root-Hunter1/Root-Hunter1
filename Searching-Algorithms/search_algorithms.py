def linear_search(values, target):
    """Return the first index of target, or -1 when absent."""
    for index, value in enumerate(values):
        if value == target:
            return index
    return -1


def binary_search(values, target):
    """Search a sorted list using binary search.

    Time: O(log n)
    Space: O(1)
    """
    low, high = 0, len(values) - 1
    while low <= high:
        middle = (low + high) // 2
        if values[middle] == target:
            return middle
        if values[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1


if __name__ == "__main__":
    data = [2, 3, 4, 10, 40]
    print(linear_search(data, 10))
    print(binary_search(data, 10))
