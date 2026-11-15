#include <iostream>
#include <string> //private, public, and, protected।

// ১. ক্লাস বা নকশা তৈরি
class DNSServer {
private:
    int port;           // প্রাইভেট ডাটা (বাইরে থেকে বদলানো যাবে না)
    std::string ip;

public:
    // Constructor (অবজেক্ট তৈরির সাথে সাথেই এটি রান হয়)
    DNSServer(std::string server_ip, int server_port) {
        ip = server_ip;
        port = server_port;
    }

    // পাবলিক ফাংশন বা মেথড
    void start() {
        std::cout << "DNS Server started on " << ip << ":" << port << std::endl;
    }
};

int main() {
    // ২. ক্লাস থেকে আসল অবজেক্ট (Object) তৈরি
    DNSServer myServer("127.0.0.1", 53);
    myServer.start(); // সার্ভার চালু করা হলো

    return 0;
}
