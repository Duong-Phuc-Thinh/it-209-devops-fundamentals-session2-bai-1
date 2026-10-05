import subprocess
import sys
import argparse

def test_ssh_connection(ip, key_path):
    print(f"[*] Dang thu ket noi toi {ip} bang khoa {key_path}...")
    
    # Lenh kiem tra he dieu hanh va cau hinh phan cung co ban tren Droplet
    cmd = [
        "ssh", 
        "-o", "StrictHostKeyChecking=no", 
        "-o", "ConnectTimeout=10",
        "-i", key_path, 
        f"root@{ip}", 
        "echo '--- OS Version ---' && cat /etc/os-release | grep PRETTY_NAME && echo '--- CPU Info ---' && lscpu | grep 'Model name' && echo '--- RAM Info ---' && free -h"
    ]
    
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        print("\n[+] Ket noi SSH thanh cong!")
        print("\nKet qua kiem tra cau hinh Droplet:")
        print("="*50)
        print(result.stdout)
        print("="*50)
        return True
    except subprocess.CalledProcessError as e:
        print("\n[-] Loi ket noi SSH!")
        print(f"Ma loi: {e.returncode}")
        print(f"Chi tiet loi tu SSH client:\n{e.stderr}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kiem tra ket noi SSH toi DigitalOcean Droplet.")
    parser.add_argument("-ip", "--ip_address", required=True, help="Dia chi IP cua Droplet")
    parser.add_argument("-i", "--key_path", required=True, help="Duong dan toi file SSH Private Key")
    
    args = parser.parse_args()
    success = test_ssh_connection(args.ip_address, args.key_path)
    sys.exit(0 if success else 1)