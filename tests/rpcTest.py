import os
import errno
import sys

from subprocess import call

def prompt_sudo():
    ret = 0
    if os.geteuid() != 0:
        msg = "[sudo] password for %u:"
        ret = subprocess.check_call("sudo -v -p '%s'" % msg, shell=True)
    return ret

def main():
    print("X")
    # if prompt_sudo() != 0:
    #     # the user wasn't authenticated as a sudoer, exit?
    # try:
    #     os.rename('/root/.bash_profile', '/root/.bash_nopro')
    # except IOError as e:
    #     if e[0] == errno.EPERM:
    #         sys.exit("You need root permissions to do this!!")

if __name__ == '__main__':
    main()

