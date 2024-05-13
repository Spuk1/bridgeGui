import os
import sys
import subprocess




def elevate():
    subprocess.getstatusoutput("groupadd -g 1009 netAdmin")
    subprocess.getstatusoutput(f"usermod -G netAdmin -a {os.getlogin()}")
    subprocess.getstatusoutput(f"group{os.getlogin()}")
    with open("/etc/sudoers","a",encoding="utf-8") as f:
        f.writelines(f"{os.getlogin()} ALL=NOPASSWD: /usr/bin/ip\n")
    return


def main():
    elevate()
    return 0


if __name__ == "__main__":
    sys.exit(main())