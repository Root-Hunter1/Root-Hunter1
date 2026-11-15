#include <iostream>
#include <vector>
#include <string>

int main() {
    // স্ট্রিং রাখার একটি ডাইনামিক ভেক্টর
    std::vector<std::string> blocked_ips;

    // নতুন আইপি যোগ করা (সাইজ নিজে থেকেই বাড়বে)
    blocked_ips.push_back("192.168.1.10");
    blocked_ips.push_back("10.0.0.5");
    blocked_ips.push_back("172.16.0.2");

    // সবগুলো আইপি প্রিন্ট করা
    for (const auto& ip : blocked_ips) {
        std::cout << "Blocked IP: " << ip << std::endl;
    }

    return 0;
}
