#include <iostream>
#include <thread>
#include <map>
#include <string>
#include <chrono>

using namespace std::chrono_literals;

void refash_red(std::map<std::string, int > hacker) {
    while (true) {
    for (auto& item : hacker) {
        item.second++;
        std::cout << item.first << "-" << item.second << std::endl;
    }
    std::this_thread::sleep_for(700ms);
    }
}

int main() {
    std::map<std:: string, int > hacker = {
        {"Tiger", 20},
        {"Hacler", 21},
        {"father", 23},
        {"mother", 69},

    };

    std::thread hull(refash_red, hacker);

    hull.join();

    return 0;
}
