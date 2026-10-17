GNU nano 9.0                  0.lua
if user_pass == "tiger2" then

    if pass == "2" then
        print("\n[!] ENTER TARGET IP:")
        target = io.read()
        print("[+] STARTING ATTACK SCAN...")
        os.execute("nmap -A -T4 " .. target)
     end
else
    print("Access Denied")
end
