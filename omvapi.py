from collections import UserList, OrderedDict
from ldif import LDIFParser,LDIFWriter
#import ldif
from pprint import pprint
import subprocess
from dataclasses import dataclass
import json
import csv
import os
import errno
import sys
import logging


Userslist = []
Groupslist = []
whiteListedUsers = []
blackListedUsers = []

def omvRpcCmd(cmd = "-h"):
    omvCmdPath = '/usr/sbin/omv-rpc'
    if os.getuid() != 0:
        exit("You need to have root privileges to run omv-rpc script")
    else:
        try:
            proc = subprocess.check_output(omvCmdPath + " " + cmd, stderr=subprocess.STDOUT, shell=True)
            return proc
        except subprocess.CalledProcessError as e:
            print("[ERROR]: Error running omv-rpc")
            proc = e.output.decode()
            print(proc)

def createOmvUser():
    omvCmdCreateUserPrefix = "-u amin 'UserMgmt' 'setUser'"
    for user in Userslist:
        print("Creating user...")
        print(omvCmCreateUserPrefix + json.dump(user))
    
def createOmvGroup():
    omvCmdCreateGroupPrefix = "-u admin 'UserMgmt' 'setGroup'"
    print("creating group")
def printUsers():
    print("printing user")

def printOmvUsers():
    omvCmdPrintAllUsers = "-u admin 'UserMgmt' 'enumerateUsers'"
    omvRpcCmd(omvCmdPrintAllUsers)

def printOmvGroups():
    omvCmdPrintAllGroups = "-u admin 'UserMgmt' 'enumerateGroups'"
    omvRpcCmd(omvCmdPrintAllGroups)

def deleteAllOmvUsers():
    omvCmdDeleteUserPrefix = "-u admin 'UserMgmt' 'deleteUser'"
    ## TODO:: json object
    # for user in Userslist:
    omvRpcCmd(omvCmdDeleteUserPrefix + "JSON USER")

def deleteAllOmvGroups():
    omvCmdDeleteGroupPrefix =  "-u admin 'UserMgmt' 'deleteGroup'"
    ## TODO: json object
    # for group in GroupsList: 
    omvRpcCmd(omvCmdDeleteGroupPrefix + "JSON GROUP")

def importBlacklistedUsers(csvFilePath = "testfiles/blacklisted.csv"):
    if os.path.isfile(csvFilePath):
        print("file exists")
    else:
        print("file dosn't exists")
        sys.exit(1)

    with open(csvFilePath, "r", newline='') as csvfile:
        csvreader = csv.reader(csvfile, dialect='excel')
        for row in csvreader:
            print(', '.join(row))
        
    
def importWhitelistedUsers(csvFilePath = "testfiles/whitelisted.csv"):
    ## TODO: only one user sborawski
    import locale
    print(locale.getpreferredencoding())
    if os.path.isfile(csvFilePath):
        print("file exists")
    else:
        print("file dosn't exists")
        sys.exit(1)

    with open(csvFilePath, "r", newline='' ) as csvfile:
        csvreader = csv.reader(csvfile, dialect='excel', encoding='')
        for row in csvreader:
            print(', '.join(row))

    print("")

def importPasswordList(csvFilePath = "testfiles/secrets.csv"):
    
    if os.path.isfile(csvFilePath):
        print("file exists")
    else:
        print("file dosn't exists")
        sys.exit(1)

    with open(csvFilePath, "r", newline='') as csvfile:
        csvreader = csv.reader(csvfile, dialect='excel')
        for row in csvreader:
            print(', '.join(row))
def cleanUserList() -> None:
    print("cleaning user list")

def exportUsers(path = "importUsersToOmv.csv"):
    if os.path.isfile(path):
        print("file exists")
    else:
        print("file dosn't exists")
        sys.exit(1)

# users import format to openmediavault gui
# <username>;<uid>;<tags>;<email>;<password>;<shell>;<groupname,groupname,...>;<disallowusermod>
    # check if file exist 
    # ask user for interaction
    # override file by default
    # write user to file
    # 
    with open(path, "w", newline='\n\r') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=';',
                               quotechar='|', quoting=csv.QUOTE_MINIMAL, dialect='unix_dialect')
        for user in Userslist:
            csvwriter.writerow(user.name,
                                user.uid,
                                user.tags,
                                user.email,
                                user.password,
                                user.shell,
                                user.groups,
                                user.comment,
                                user.disallowusermod)

    print("ttt")
def exportGroups(path = "importGroupsToOmv.csv"):

    if os.path.isfile(path):
        print("file exists")
    else:
        print("file dosn't exists")
        sys.exit(1)

# groups import format to openmediavault gui
# <groupname>;<gid>;<tags>
    # for group in GroupsList:
    #     
    with open(path, "w", newline='\n\r') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=';',
                               quotechar='|', quoting=csv.QUOTE_MINIMAL, dialect='unix_dialect')
        for group in Groupslist:
            csvwriter.writerow(group.name, group.gid, group.tags)
    print("ccc")

# importWhitelistedUsers("testfiles/smbuserspass.csv")
logging.basicConfig(filename="output.log", level=logging.DEBUG)

# for g in Groupslist:
#     print(g.keys())
# exportUsers()
# exportGroups()

# try:
#     proc = subprocess.check_output(omvCmdPath + omvCmdPrintAllGroups, stderr=subprocess.STDOUT, shell=True)
# except IOError as e:
#     if e[0] == erron.EPERM:
#         sys.exit("jou need to have root privileges to run omv-rpc script")
# module samba
		# $this->registerMethod("getSettings");
		# $this->registerMethod("setSettings");
		# $this->registerMethod("getShareList");
		# $this->registerMethod("getShare");
		# $this->registerMethod("setShare");
		# $this->registerMethod("deleteShare");
		# $this->registerMethod("emptyRecycleBin");
		# $this->registerMethod("getStats");
