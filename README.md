# OOP Network Scanner

A modular, clean, and professional Command Line Interface (CLI) network scanning tool built using Python and Object-Oriented Programming (OOP) principles. This tool automates the process of fetching target IP addresses and launching rapid port scans using Nmap.

## 🚀 Features
- **OOP Architecture:** Built with high code maintainability and scalability in mind.
- **Automated DNS Resolution:** Converts any domain name into its corresponding IP address seamlessly.
- **Integrated Subprocess:** Automatically invokes the Nmap utility directly via native system calls.
- **Cross-Platform:** Runs perfectly on Linux, Termux (Android), and Windows.

## 🎯 Objectives
- Understand Object-Oriented Programming (OOP) concepts in automation.
- Automate system commands using Python subprocesses.
- Build reliable and efficient security testing tools.
- Learn how production-grade scripts are structured.

## 🛠️ Source Code 
Here is the complete Python source code for this project. You can review the object-oriented structure below:

```python
import socket
import os
import subprocess

class NetworkScanner:
    def __init__(self):
        self.target_domain = ""
        self.target_ip = ""

    def get_ip(self):
        try:
            self.target_ip = socket.gethostbyname(self.target_domain)
            print(f"[+] Target ip address: {self.target_ip}")
            return True
        except Exception as e:
            print(f"[!] Target ip address: 0.0.0.0 (Error: {e})")
            return False

    def run_nmap(self):
        print(f"[*] Running Nmap Scan To {self.target_ip}")
        nmap_command = ["nmap", "-F", self.target_ip]
        try:
            result = subprocess.run(nmap_command, capture_output=True, text=True, check=True)
            print(result.stdout)
        except Exception as e:
            print(f"[!] Scan Error: {e}")

    def start(self):
        os.system("clear")
        print("=====================================")
        print("[*] CLASS OOP DEVELOPER ENGINE")
        print("=====================================")
        self.target_domain = input("Enter Target Domin: ")
        
        if self.get_ip():
            self.run_nmap()

if __name__ == "__main__":
    scanner = NetworkScanner()
    scanner.start()
```

## 🗺️ Future Roadmap
- Add custom port range selection.
- Save scan results directly to a text file.
- Integrate multi-threading for faster scanning.
- Add banner grabbing capabilities using sockets.

## 📝 License
This project is open source and intended for learning, experimentation, and educational purposes.
