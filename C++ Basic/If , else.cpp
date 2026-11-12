#include <iostream>

using namespace std;

int main() {
    int port;
    cout << "what is your port Name: " << endl;
    cin >> port;

    if (port == 80) {
        cout << "80 your port number Http" << endl;
    } else if (port == 443) {
        cout << "443 your port number Https" << endl;
    } else {
        cout << "your port number not found!";
    }
    return 0;
}
