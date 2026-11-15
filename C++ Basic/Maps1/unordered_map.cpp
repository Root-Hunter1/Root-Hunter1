#include <iostream>
#include <unordered_map>
#include <string>

int main() {
    std::unordered_map<std::string, std::string > dns_recode;

    dns_recode["ghogle.com"] = "127.1.0.1";
    dns_recode["fac3book.com"] = "213.34.3.3";

    std::cout << "ghogle_ip: " << dns_recode["ghogle.com"] << std::endl;

    return 0;

}
