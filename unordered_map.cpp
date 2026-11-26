#include <iostream>
#include <string>
#include <unordered_map>
#include <thread>
#include <chrono>

using namespace std;
using namespace std::chrono_literals;

void Nm(std::unordered_map<string, int>& name) {
    name["Tige"] = 20;
    name["waht"] = 27;
    name["baby"] = 89;
}

int main() {
    std::unordered_map<string, int> pm;

    Nm(pm);

    //or //for (auto count = 0; i < 5; count++)
    while (true) {
        for (auto item : pm) {
            cout << item.first << " : " << item.second << endl;
            std::this_thread::sleep_for(200ms);
        }
        cout << "-----------" << endl;
    }


    std::this_thread::sleep_for(200ms);

    return 0;

}
