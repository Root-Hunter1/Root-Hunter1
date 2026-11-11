#include <iostream>

using namespace std;

int main() {
    for (int i = 1; i <= 5; i++) {
        cout << "packet number: " << i << endl;
    }
    int count = 0;
    while (count < 3) {
        cout << "scaning: " << endl;
        count ++;
    }

    return 0;
}
