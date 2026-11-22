def merge_sort(values):
    """Sort a list using divide-and-conquer merge sort.

    Time: O(n log n)
    Space: O(n)
    """
    items = list(values)
    if len(items) <= 1:
        return items

    middle = len(items) // 2
    left = merge_sort(items[:middle])
    right = merge_sort(items[middle:])

    merged = []
    left_index = right_index = 0
    while left_index < len(left) and right_index < len(right):
        if left[left_index] <= right[right_index]:
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1

    merged.extend(left[left_index:])
    merged.extend(right[right_index:])
    return merged


if __name__ == "__main__":
    print(merge_sort([38, 27, 43, 3, 9, 82, 10]))
