import subprocess
import os

os.system("clear")
print("=========================================")
print("[+] CUSTOM LINUX MAC ADDRESS CHANGER    ")
print("=========================================")

interface = input("Enter Interface (e.g., wlan0, eth0): ")
new_mac = input("Enter New MAC Address (e.g., 00:11:22:33:44:55): ")

print(f"\n[*] Changing MAC address for {interface} to {new_mac}...")
print("-" * 50)

try:
    subprocess.run(["ifconfig", interface, "down"], check=True)
    subprocess.run(["ifconfig", interface, "hw", "ether", new_mac], check=True)
    subprocess.run(["ifconfig", interface, "up"], check=True)
    
    print(f"[+] SUCCESS! MAC address successfully changed to {new_mac}")

except subprocess.CalledProcessError:
    print("[!] Error: Failed to change MAC Address!")
    print("[*] Note: This tool requires Root (sudo) privileges on Linux.")

except Exception as e:
    print(f"[!] An error occurred: {e}")

print("-" * 50)
print("[+] Task Completed!")
