from math import gcd


def lcm(a, b):
    """Return the least common multiple of two integers."""
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // gcd(a, b)


def is_prime(number):
    """Return whether number is prime."""
    if number < 2:
        return False
    divisor = 2
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 1
    return True


def sieve(limit):
    """Return all primes up to limit using the sieve of Eratosthenes."""
    if limit < 2:
        return []
    is_prime_flag = [True] * (limit + 1)
    is_prime_flag[0] = is_prime_flag[1] = False
    for number in range(2, int(limit ** 0.5) + 1):
        if is_prime_flag[number]:
            for multiple in range(number * number, limit + 1, number):
                is_prime_flag[multiple] = False
    return [number for number in range(2, limit + 1) if is_prime_flag[number]]


def is_palindrome(text):
    """Return whether text is a palindrome, ignoring non-letters and case."""
    normalized = "".join(character.lower() for character in text if character.isalnum())
    return normalized == normalized[::-1]


def caesar_cipher(text, shift):
    """Shift letters in text by shift positions."""
    output = []
    for character in text:
        if character.isalpha():
            base = ord("A") if character.isupper() else ord("a")
            output.append(chr((ord(character) - base + shift) % 26 + base))
        else:
            output.append(character)
    return "".join(output)


if __name__ == "__main__":
    print(gcd(48, 18), lcm(48, 18))
    print(is_prime(29), sieve(30))
    print(is_palindrome("Racecar"), caesar_cipher("Hello, World!", 3))
