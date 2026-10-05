import os
import sys
import subprocess

def run_command(command, use_sudo=True):
    if use_sudo and os.getuid() != 0:
        command = f"sudo {command}"
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr.strip()}", file=sys.stderr)
        return False, result.stderr
    print(result.stdout.strip())
    return True, result.stdout

def main():
    print("=== SSH Port Hardening Script ===")
    
    # 1. Backup SSH config
    ssh_config_path = "/etc/ssh/sshd_config"
    backup_path = "/etc/ssh/sshd_config.bak"
    print(f"Backing up {ssh_config_path} to {backup_path}...")
    success, _ = run_command(f"cp {ssh_config_path} {backup_path}")
    if not success:
        print("Failed to backup SSH configuration. Exiting.")
        sys.exit(1)
        
    # 2. Modify SSH config to change Port 22 to 2222
    print("Modifying SSH port in configuration file...")
    try:
        # Read file
        with open(ssh_config_path, 'r') as f:
            lines = f.readlines()
        
        modified = False
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped == "#Port 22" or stripped == "Port 22":
                new_lines.append("Port 2222\n")
                modified = True
            else:
                new_lines.append(line)
        
        if not modified:
            new_lines.append("\nPort 2222\n")
            
        # Write to temporary file, then overwrite with sudo
        temp_file = "/tmp/sshd_config.tmp"
        with open(temp_file, 'w') as f:
            f.writelines(new_lines)
            
        success, _ = run_command(f"mv {temp_file} {ssh_config_path}")
        if not success:
            print("Failed to overwrite sshd_config. Exiting.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error modifying file: {e}")
        sys.exit(1)

    # 3. Configure UFW to allow port 2222/tcp
    print("Configuring UFW firewall to allow port 2222/tcp...")
    success, _ = run_command("ufw allow 2222/tcp")
    if not success:
        print("Warning: Failed to allow port 2222/tcp in UFW. Please verify manually.")
    
    # Enable UFW if not active
    run_command("ufw --force enable")

    # 4. Restart SSH service
    print("Restarting SSH service...")
    success, _ = run_command("systemctl restart ssh")
    if not success:
        print("Retrying with 'sshd' service...")
        success, _ = run_command("systemctl restart sshd")
        if not success:
            print("Failed to restart SSH service. Please restart it manually.")
            sys.exit(1)
            
    print("\n=== SSH Port Hardening Completed Successfully! ===")
    print("Instructions:")
    print("1. DO NOT close this terminal session yet.")
    print("2. Open a new terminal on your local machine and test connection:")
    print("   ssh -p 2222 devops@<IP_ADDRESS>")
    print("3. Verify that old port 22 is inaccessible:")
    print("   ssh -p 22 devops@<IP_ADDRESS>")

if __name__ == "__main__":
    if os.getuid() != 0:
        print("This script requires root privileges. Attempting to run with sudo...")
        args = [sys.executable] + sys.argv
        os.execvp("sudo", ["sudo"] + args)
    else:
        main()
