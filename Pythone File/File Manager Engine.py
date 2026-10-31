import os
import shutil

os.system("clear")
print("=========================================")
print("[+] Y4-PROJECT: TIGER FILE MANAGER BOT   ")
print("=========================================")

print("[+] Available Server Operations:")
print("  1. List Files in Current Directory")
print("  2. Create a New Folder (Directory)")
print("  3. Rename a File/Folder")
print("  4. Delete a File Completely")

try:
    choice = input("\n[*] Select Operation (1-4): ").strip()
    print("-" * 55)

    if choice == "1":
        files = os.listdir(".")
        print("[*] Displaying Active Files & Folders inside Root:")
        for idx, item in enumerate(files):
            print(f"  [{idx+1}] -> {item}")

    elif choice == "2":
        folder_name = input("[*] Enter New Folder Name: ").strip()
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
            print(f"[+] SUCCESS: Folder '{folder_name}' Created on Server Disk!")
        else:
            print("[!] Warning: Folder already exists!")

    elif choice == "3":
        old_name = input("[*] Enter Current File/Folder Name: ").strip()
        new_name = input("[*] Enter New Name for Target: ").strip()
        if os.path.exists(old_name):
            os.rename(old_name, new_name)
            print(f"[+] SUCCESS: Changed '{old_name}' to '{new_name}' cleanly.")
        else:
            print("[!] Error: Target path not found!")

    elif choice == "4":
        target_file = input("[*] Enter Target File Name to Destroy: ").strip()
        if os.path.exists(target_file):
            if os.path.isdir(target_file):
                shutil.rmtree(target_file)
            else:
                os.remove(target_file)
            print(f"[+] SUCCESS: Target '{target_file}' Wiped Out from Server Disk!")
        else:
            print("[!] Error: File does not exist on this directory!")
    else:
        print("[!] Error: Invalid Operation Selected!")

except Exception as e:
    print(f"\n[!] System Core Error: {e}")

print("=========================================")
