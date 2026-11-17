#include <iostream>
#include <memory> // Smart Pointer-এর জন্য এই লাইব্রেরি লাগে

using namespace std;

int main() {
    // ১. নিরাপদ উপায়ে ডাইনামিক মেমরি তৈরি (new লেখার দরকার নেই)
    unique_ptr<int> ptr = make_unique<int>(53);

    cout << "DNS Port: " << *ptr << endl; // সাধারণ পয়েন্টারের মতোই ভ্যালু দেখাবে

    // মান পরিবর্তন করা
    *ptr = 8080;
    cout << "New Port: " << *ptr << endl;

    // এখানে আলাদা করে delete লিখতে হবে না!
    // main() শেষ হওয়ার সাথে সাথে ptr নিজেই মেমরি খালি করে দেবে।
    return 0;
}
