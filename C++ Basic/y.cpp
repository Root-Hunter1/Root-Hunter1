#include <iostream>

using namespace std;

int addpacket(int a, int b) {
return a + b;
}

int main() {
    int total = addpacket(5, 10);
    cout << "Total Packets:" << total << endl;
    return 0;
}
