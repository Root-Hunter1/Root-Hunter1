def heap_sort(values):
    """Sort a list using a binary max heap.

    Time: O(n log n)
    Space: O(1)
    """
    items = list(values)

    def sift_down(root, length):
        while True:
            largest = root
            left = 2 * root + 1
            right = 2 * root + 2
            if left < length and items[left] > items[largest]:
                largest = left
            if right < length and items[right] > items[largest]:
                largest = right
            if largest == root:
                return
            items[root], items[largest] = items[largest], items[root]
            root = largest

    for index in range(len(items) // 2 - 1, -1, -1):
        sift_down(index, len(items))
    for end in range(len(items) - 1, 0, -1):
        items[0], items[end] = items[end], items[0]
        sift_down(0, end)
    return items


if __name__ == "__main__":
    print(heap_sort([12, 11, 13, 5, 6, 7]))
