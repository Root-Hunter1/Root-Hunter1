#include <iostream>
using namespace std;

int main() {
    int size;
    cout << "your memory buffer: ";
    cin >> size;
    int* arr = new int[size];

    for (int i = 0; i <= size; i++) {
        arr[i] = (i + 1) * 10;
    }

    cout << "my frist arr: " << arr[0] << endl;
    cout << "my arr address: " << &arr[0] << endl;

    //কাজ শেষে মেমোরি মুছে ফেলা (খুবই জরুরি)
    delete[] arr;
    arr = nullptr; // নিরাপদ থাকার জন্য পয়েন্টার খালি করা
    return 0;
}
