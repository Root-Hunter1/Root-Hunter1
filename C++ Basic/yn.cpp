#include <iostream>
using namespace std;

void value(int* ptr) {
        *ptr = 100;
}
int main() {
    int number = 183;
    value(&number);
    cout << "new value: " << number << endl;
    return 0;
}
