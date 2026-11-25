#include <iostream>
#include <memory>
#include <string>
#include <cstdlib>

using namespace std;

void Nmea(std::unique_ptr<string[]> names) {
    names[0] = "ruma";
    names[1] = "suma";
    names[2] = "baby";

    for (int i = 0; i < 3; i++) {
        std::cout << names[i] << endl;
    }
}

int main() {
    system("clear");

    string num;
    std::cout << "you make start your c++ program" << "\n" << endl;
    std::cout << "waht is your program name: "<< endl;
    cin >> num;

    if (num == "Nmea") {
        std::cout << "Running" << endl;
    } else if (num == "9") {
        std::cout << "Sever Not Found!" << endl;
        cout << "Real Name: Nmea: " << "exit Number 9" << endl;
        exit(0);
    } else {
        std::cout << "Wrong Input" << endl;
        exit(0);
    }

    auto names = std::make_unique<string[]> (3);
    Nmea(std::move(names));

    std::cout << &names << "\n" << endl;

    auto arr = std::make_unique<int[]> (5);

    for (int i = 0; i < 5; i++) {
        arr[i] = i;
    }

    auto ptr = std::move(arr);

    for (int i = 0; i < 5; i++) {
        std::cout << ptr[i] << endl;
    }

    return 0;
}
