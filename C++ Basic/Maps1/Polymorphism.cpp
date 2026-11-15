#include <iostream>

// Parent Class
class Protocol {
public:
    // virtual মানে চাইল্ড ক্লাস চাইলে এটিকে বদলাতে পারবে
    virtual void handlePacket() {
        std::cout << "Handling generic network packet..." << std::endl;
    }
};

// Child Class 1 (UDP)
class UDPProtocol : public Protocol {
public:
    void handlePacket() override {
        std::cout << "Fast UDP DNS Packet processed!" << std::endl;
    }
};

// Child Class 2 (TCP)
class TCPProtocol : public Protocol {
public:
    void handlePacket() override {
        std::cout << "Reliable TCP DNS Packet processed!" << std::endl;
    }
};

int main() {
    Protocol* pkt; // প্যারেন্ট ক্লাসের পয়েন্টার

    UDPProtocol udp;
    TCPProtocol tcp;

    pkt = &udp;
    pkt->handlePacket(); // আউটপুট: Fast UDP DNS Packet processed!

    pkt = &tcp;
    pkt->handlePacket(); // আউটপুট: Reliable TCP DNS Packet processed!

    return 0;
}
