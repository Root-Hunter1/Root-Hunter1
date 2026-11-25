# C++ Basics — Code Guide

This folder contains small examples of common C++ language features and standard-library tools. Each source file is a learning example; many are standalone programs with their own `main()` function, so compile and run them one at a time.

## Files in this folder

| File | What it demonstrates |
|---|---|
| `2Pointer.cpp` | Passing an integer's address to a function through a pointer. The function dereferences the pointer and changes the original integer from `183` to `100`. |
| `If , else.cpp` | Conditional branching with `if`, `else if`, and `else`. It reads a port number and identifies `80` as HTTP and `443` as HTTPS. |
| `Maps.cpp` | A `std::map` of names and integer values, iterated and updated in a worker thread. The loop runs forever and prints the updated entries every 700 milliseconds. |
| `Thread.cpp` | Creating threads with `std::thread` and waiting for them with `join()`. The file contains two separate examples, each with its own `main()`; use one example at a time when compiling. |
| `for, while Loop.cpp` | Repeating work with a `for` loop and a `while` loop. The example prints five packet numbers, then prints a scan message three times. |
| `function call` | Defining a function and calling it from `main()`. The function prints 200 plus signs. The file has no `.cpp` extension, so specify the file when compiling or rename it with a `.cpp` extension. |
| `input.cpp` | Reading a single word from standard input with `cin` and printing it back. Since `cin >> tiger` stops at whitespace, it does not read a full name containing spaces. |
| `new-delete.cpp` | Allocating an integer array dynamically with `new[]`, accessing its elements, and releasing it with `delete[]`. See the safety note below before running it. |
| `plus.cpp` | Declaring integer variables, adding them, and printing their sum. |

## Subfolders

### `pointer/`

| File | What it demonstrates |
|---|---|
| `pointer.cpp` | A raw pointer holding the address of an integer. It prints the value and address, dereferences the pointer, and changes the integer through the pointer. |
| `shared_ptr.cpp` | Shared ownership of dynamically allocated data with `std::shared_ptr`. `use_count()` shows how the number of owners changes when a shared pointer is copied and goes out of scope. |
| `unique_ptr.cpp` | Exclusive ownership with `std::unique_ptr`. The smart pointer automatically releases the allocated integer when it goes out of scope. |

### `Maps1/`

| File | What it demonstrates |
|---|---|
| `Class opp.cpp` | Defining a class, private data members, a public constructor, and a public method; then creating an object and calling its method. |
| `Inheritance.cpp` | Inheritance: `DNSServer` derives from `BaseServer` and uses the base class's member and method alongside its own method. |
| `Polymorphism.cpp` | Runtime polymorphism with a virtual method and overriding. Calling `handlePacket()` through a base-class pointer runs the implementation for the actual UDP or TCP object. |
| `Vector.cpp` | Storing a variable number of strings in `std::vector`, adding values with `push_back()`, and iterating over them. |
| `unordered_map.cpp` | Associating string keys with string values in `std::unordered_map` and looking up a value by key. |

## Important notes

- **Array bounds:** In `new-delete.cpp`, the loop condition is `i <= size`, which writes one element past the allocated array. Change it to `i < size` before running the example. Also, make sure the entered size is positive.
- **Infinite loop:** `Maps.cpp` intentionally loops forever. Stop the program manually (for example, with Ctrl+C) when you are done observing it.
- **Threads and output:** The `Thread.cpp` examples print from multiple threads, so the `+` and `-` characters may appear interleaved. Compile only one of its two `main()` examples at a time.
- **Standard version:** The `Maps.cpp` example uses chrono literals such as `700ms`; compile it with C++14 or later and enable thread support where required by your compiler.
- **Port example:** The port numbers in `If , else.cpp` are used only to demonstrate conditionals; the program does not open a network port.
