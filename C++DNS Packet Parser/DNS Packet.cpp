#include <iostream>
#include <cstdint>
#include <string>
#include <vector>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
using namespace std;

// DNS header first: 12 byte
struct DnsHeader {
    uint16_t id;
    uint16_t flags;
    uint16_t qdcount;
    uint16_t ancount;
    uint16_t nscount;
    uint16_t arcount;
};

uint16_t read16(const uint8_t* p) {
    return (p[0] << 8) | p[1];
}

int main() {
    vector<uint8_t> packet = {
        0x12, 0x34,             // ID
        0x01, 0x00,             // flags (standard query)
        0x00, 0x01,             // questions = 1
        0x00, 0x00,             // answers = 0
        0x00, 0x00,             // authority = 0
        0x00, 0x00,             // additional = 0
        // Question: google.com
        3, 'w','w','w',
        6, 'g','o','o','g','l','e',
        3, 'c','o','m',
        0,                      // End of Name
        0x00, 0x01,             // type A
        0x00, 0x01              // class IN
    };

    const uint8_t* p = packet.data();

    DnsHeader h;
    h.id      = read16(p);
    h.flags   = read16(p + 2);
    h.qdcount = read16(p + 4);

    cout << "ID: " << hex << h.id << dec << endl;
    cout << "Questions: " << h.qdcount << endl;

    // Reading the domain name (starting at offset 12)
    size_t pos = 12;
    string name;
    while (p[pos] != 0) {
        int len = p[pos++];
        name += string((const char*)(p + pos), len);
        pos += len;
        if (p[pos] != 0) name += ".";
    }
    pos++; // শেষের 0 টপকানো

    uint16_t qtype  = read16(p + pos);
    uint16_t qclass = read16(p + pos + 2);

    std::cout << "Type: " << qtype << std::endl;
    std::cout << "Class: " << qclass << std::endl;
    cout << "Domain: " << name << endl;
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) { perror("socket"); return 1; }

    // ৫ সেকেন্ডের timeout, নইলে উত্তর না এলে আটকে থাকবে
    struct timeval tv{5, 0};
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    sockaddr_in server{};
    server.sin_family = AF_INET;
    server.sin_port = htons(53);
    inet_pton(AF_INET, "8.8.8.8", &server.sin_addr);

    ssize_t sent = sendto(sock, packet.data(), packet.size(), 0,
                      (sockaddr*)&server, sizeof(server));
    std::cout << "Sent bytes: " << sent << std::endl;

    uint8_t buf[512];
    ssize_t n = recvfrom(sock, buf, sizeof(buf), 0, nullptr, nullptr);
    if (n < 0) { perror("recvfrom"); close(sock); return 1; }
    std::cout << "Received bytes: " << n << std::endl;
   
    // উত্তরের header পড়া
    std::cout << "Answer count: " << read16(buf + 6) << std::endl;
    
    close(sock);

    return 0;
}
