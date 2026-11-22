def bubble_sort(values):
    """Sort a list in place using bubble sort.

    Time: O(n²)
    Space: O(1)
    """
    items = list(values)
    for end in range(len(items) - 1, 0, -1):
        swapped = False
        for index in range(end):
            if items[index] > items[index + 1]:
                items[index], items[index + 1] = items[index + 1], items[index]
                swapped = True
        if not swapped:
            break
    return items


if __name__ == "__main__":
    print(bubble_sort([64, 34, 25, 12, 22, 11, 90]))
