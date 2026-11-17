#include <iostream>

using namespace std;

int main() {
    int age = 25;
    int* ptr = &age;

    cout << "this output valu: " << age << endl;
    cout << "hexdicimal valu: " << &age << endl;
    cout << "ptr thake address: " << ptr << endl;
    cout << "ptr real valu: " << *ptr << endl;

    *ptr = 79;
     cout << "ptr changes new valu: " << *ptr << endl;
     return 0;
}
