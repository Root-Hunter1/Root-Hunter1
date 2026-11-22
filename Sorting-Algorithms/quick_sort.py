def quick_sort(values):
    """Sort a list using quick sort.

    Average time: O(n log n)
    Worst time: O(n²)
    Space: O(log n)
    """
    items = list(values)
    if len(items) <= 1:
        return items

    pivot = items[len(items) // 2]
    below = [item for item in items if item < pivot]
    equal = [item for item in items if item == pivot]
    above = [item for item in items if item > pivot]
    return quick_sort(below) + equal + quick_sort(above)


if __name__ == "__main__":
    print(quick_sort([10, 7, 8, 9, 1, 5]))
