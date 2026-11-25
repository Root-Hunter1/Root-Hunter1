
#include <cstddef> // std::size_t, std::byte এর জন্য

#include <new> // Placement new এর জন্য

#include <iostream> 

#include <cstdint>  = Dns Struct  

#include <string> 

#include <vector>

#include <cstdlib> // exit(0) ব্যবহারের জন্য এই লাইব্রেরিটি লাগে

#include <sys/socket.h>

এটি Socket Programming-এর প্রধান Header।

এর মাধ্যমে Socket তৈরি এবং Network Data পাঠানো ও গ্রহণ করা যায়।

Function	কাজ

socket()	নতুন Socket তৈরি

bind()	Socket-এর সঙ্গে IP ও Port যুক্ত

sendto()	Data পাঠানো

recvfrom()	Data গ্রহণ

connect()	অন্য Socket-এর সঙ্গে সংযোগ

listen()	Connection-এর জন্য অপেক্ষা

accept()	Incoming Connection গ্রহণ

✅2.#include <netinet/in.h>

এটি Internet Protocol-এর Address এবং Port সম্পর্কিত Structure ও Constant দেয়।


Name
কাজ
sockaddr_in IPv4 Address সংরক্ষণ

sockaddr_in6 IPv6 Address সংরক্ষণ

htons() Host Byte Order থেকে Network Byte Order

htonl() 32-bit Host থেকে Network Byte Order

INADDR_ANY সব Local IPv4 Interface

struct sockaddr_in server;

server.sin_family = AF_INET;
server.sin_port = htons(53);
server.sin_addr.s_addr = INADDR_ANY;


✅3.#include <arpa/inet.h>
IP Address এবং Byte Order Conversion-এর কাজে লাগে।

Function	কাজ
inet_pton()	IP String থেকে Binary Address

inet_ntop()	Binary Address থেকে IP String

htonl()	Host to Network

ntohl()	Network to Host

htons()	16-bit Host to Network

ntohs()	16-bit Network to Host

উদাহরণ:
struct in_addr ip;
inet_pton(AF_INET, "8.8.8.8", &ip);

✅4.#include <unistd.h>
এটি Unix/Linux System Call-এর Header।

গুরুত্বপূর্ণ Function:
Function	কাজ

close()	Socket/File বন্ধ

read()	Data পড়া

write()	Data লেখা

sleep()	নির্দিষ্ট সময় অপেক্ষা

getpid()	Process ID পাওয়া

উদাহরণ:
close(sockfd);
এটি Socket বন্ধ করে।


✅6.DNS Programming-এ এগুলোর ব্যবহার
তোমার DNS Resolver-এর একটি সাধারণ Workflow:

1. socket() → UDP Socket তৈরি।

2. sockaddr_in → DNS Server-এর IP ও Port নির্ধারণ।

3. htons(53) → Port Network Byte Order-এ নেওয়া।

4. sendto() → DNS Query পাঠানো।

5. recvfrom() → DNS Response গ্রহণ।

6. close() → Socket বন্ধ।

মনে রাখবে: DNS-এর Packet Parsing-এর জন্য তুমি আগে uint8_t, vector এবং read16() ব্যবহার করেছো। আর এই Header-গুলো দিয়ে সেই Packet Network-এর মাধ্যমে পাঠানো ও গ্রহণ করা সম্ভব।

