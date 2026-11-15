#include <iostream>
#include <thread>

void function1() {
   for (int i=0; i < 200; i++)
       std::cout << "+";
}

void function2() {
    for (int i = 0; i < 200; i++)
        std::cout << "-";
}

int main() {
    function1();
    function2();

    std:: thread worker1(function1);
    std:: thread worker2(function2);

    worker1.join();
    worker2.join();

    return 0;
}



✅✅✅✅Steps 2 next part✅✅

#include <iostream>
#include <thread>

//#char (bytes/bits) example: char name[] = "Hacker"
//little name//
void function1(char symbol) { 
   for (int i=0; i < 200; i++)
       std::cout << symbol;
}

void function2() {
    for (int i = 0; i < 200; i++)
        std::cout << "-";
}

int main() {
    std::thread worker1(function1, 'o');
    std::thread worker2(function2);

    worker1.join();
    worker2.join();

    return 0;
}

