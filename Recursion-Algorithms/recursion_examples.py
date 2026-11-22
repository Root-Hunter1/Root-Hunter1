def factorial(number):
    """Calculate number! recursively."""
    if number < 0:
        raise ValueError("number must be non-negative")
    if number in (0, 1):
        return 1
    return number * factorial(number - 1)


def reverse_string(text):
    """Reverse a string recursively."""
    if len(text) <= 1:
        return text
    return reverse_string(text[1:]) + text[0]


def tower_of_hanoi(discs, source="A", target="C", auxiliary="B"):
    """Return move instructions for the Tower of Hanoi puzzle."""
    moves = []

    def move(count, from_rod, to_rod, spare):
        if count == 0:
            return
        move(count - 1, from_rod, spare, to_rod)
        moves.append((from_rod, to_rod))
        move(count - 1, spare, to_rod, from_rod)

    move(discs, source, target, auxiliary)
    return moves


if __name__ == "__main__":
    print(factorial(6))
    print(reverse_string("hello"))
    print(tower_of_hanoi(3))
