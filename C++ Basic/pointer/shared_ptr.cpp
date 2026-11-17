#include <iostream>
#include <memory> // Smart Pointer use

using namespace std;

int main() {
    // ১. প্রথম মালিক তৈরি হলো (Reference Count = 1)
    shared_ptr<int> ptr1 = make_shared<int>(53);
    cout << "Malik songkha: " << ptr1.use_count() << endl; // আউটপুট: 1

    {
        // ২. ptr1-কে কপি করে দ্বিতীয় মালিক ptr2 বানানো হলো (Count = 2)
        shared_ptr<int> ptr2 = ptr1;
        cout << "Notun malik jukto howar por: " << ptr1.use_count() << endl; // আউটপুট: 2
        cout << "Value: " << *ptr2 << endl; // আউটপুট: 53
    } // এখানে ব্র্যাকেট শেষ হওয়ায় ptr2 ধ্বংস হয়ে গেল, কিন্তু মেমরি মুছল না!

    // ৩. ptr1 এখনও বেঁচে আছে (Count আবার 1 হয়ে গেছে)
    cout << "ptr2 shesh howar por malik: " << ptr1.use_count() << endl; // আউটপুট: 1

    // main() শেষ হলে ptr1-ও ধ্বংস হবে এবং তখন মেমরি পুরোপুরি খালি হবে
    return 0;
}
