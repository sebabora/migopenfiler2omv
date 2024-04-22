### This program is made to test samba users rights
import urllib
from smb.SMBHandler import SMBHandler

def main():
    opener = urllib.reuest.build_opner(SMBHandler)
    fh = opener.open('smb://10.0.0.4/Roboczy IT/ksiazka_adresowa_roundcube.csv')
    data = fh.read()
    fh.close()
    if __name__ == "__main__":
        main()
