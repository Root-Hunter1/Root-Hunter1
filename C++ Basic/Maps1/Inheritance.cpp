#include <iostream>
#include <string>

// ১. Parent Class (মূল সার্ভারের সাধারণ কাজ)
class BaseServer {
public:
    int port;
    void openSocket() {
        std::cout << "Socket opened on port: " << port << std::endl;
    }
};

// ২. Child Class (BaseServer-এর সব ক্ষমতা পেয়ে গেল)
class DNSServer : public BaseServer {
public:
    void resolveDomain(std::string domain) {
        std::cout << "Resolving DNS for: " << domain << std::endl;
    }
};

int main() {
    DNSServer myDns;
    myDns.port = 53;                 // BaseServer থেকে পাওয়া ভ্যারিয়েবল
    myDns.openSocket();              // BaseServer থেকে পাওয়া ফাংশন
    myDns.resolveDomain("google.com"); // DNSServer-এর নিজস্ব ফাংশন

    return 0;
}
