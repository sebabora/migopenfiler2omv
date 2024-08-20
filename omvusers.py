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

omvUser = {
    "name" : str,
    "uid" : int,
    "tags" : list,
    "groups" : list,
    "shell" : str,
    "password" : str,
    "email" : str,
    "comment" : str,
    "disallowusermod" : bool,
    "sshpubkeys" : list[str],
}

omvGroup = {
    "name" : str,
    "gid" : int,
    "tags" : list,
    "comment" : str,
    "members" : list[str],
}

print(omvUser)

@dataclass
class User:
    """ Single user data """
    name: str
    uid: int
    tags: list
    groups: list
    shell: str
    password: str
    email: str
    comment: str
    disallowusermod: bool
    sshpubkeys: list[str]
    oldidNumber: int
    homeDir: str
    passwordHash : str
    sambaNTPassword : str
    gid: int
    # def printUser():
    #     print("User: ", name)

@dataclass
class Group:
    name: str
    gid: int
    tags: list
    comment: str
    members: list[str]
    def __str__(self):
        return field.name + " " 

Userslist = []
Groupslist = []

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

            
def parseSamAccount(entry):
    tUser = User()
    tUser.name=entry.get("givenName")[0]
    tUser.uid=entry.get("uidNumber")[0]
    tUser.groups=["users", tUser.name]
    tUser.shell=entry.get("loginShell")[0]
    # tUser.password=entry.get("")[0]
    tUser.email=tUser.name + "@midas.pl"
    tUser.comment=entry.get("")
    tUser.disallowusermod= True
    tUser.sshpubkeys=entry.get("")
    tUser.oldidNumber=entry.get("sambaSID")[0]
    tUser.homeDir=entry.get("homeDirectory")[0]
    tUser.passwordHash =entry.get("userPassword")[0]
    tUser.sambaNTPassword =entry.get("sambaNTPassword")[0]
    # print("Samba NT Password: ", tUser.sambaNTPassword)
    tUser.gid=entry.get("gidNumber")[0]
    ## TODO: somekind verbose printing
    #
    # print("Parsing user: ", tUser.name, tUser.uid)

    return tUser

def parseGroup(entry):
    tGroup = Group(entry.get("cn")[0], entry.get("gidNumber"), entry.get("memberUid"))
    ## TODO: somekind verbose printing
    #
    # print("Parsing group:x ", tGroup.gid)
    # print(tGroup.__dataclass_fields__)
    return tGroup

def parseLDIFile(path = "testfiles/ofusersdb.ldif"):
    parser = LDIFParser(open(path, "rb") )
    # for dn, record in parser.parse():
    #     print('got entry record: %s' % dn)
    #     pprint(record)
    recordCounter = 0

    for dn, record in parser.parse():

        recordCounter += 1
        for element, attributs in record.items():
            if element == "objectClass":
                ## TODO: somekind verbose printing
                # print("element: ", element, "attr", attributs)
                if attributs.count("top") > 0:
                    continue
                if attributs.count("posixAccount") > 0:
                    Userslist.append(parseSamAccount(record))
                    continue
                if attributs.count("posixGroup") > 0:
                    Groupslist.append(parseGroup(record))
                    continue
            else:
                continue
        
        # pprint(record)
        recordCounter += 1
    ## TODO: some kind verbose printing 

    logging.info("Found %i records", recordCounter)
    logging.info("\tFound %s users", len(Userslist))
    logging.info("\tFound %s gropus", len(Groupslist))

    # print("Records: ", recordCounter)
    # print("Parsed Users: ", len(Userslist))
    # print("Parsed Groups: ", len(Groupslist))
    
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
    # for user in Userlist:
    omvRpcCmd(omvCmdDeleteUserPrefix + "JSON USER")

def deleteAllOmvGroups():
    omvCmdDeleteGroupPrefix =  "-u admin 'UserMgmt' 'deleteGroup'"
    ## TODO: json object
    # for group in Grouplist: 
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

parseLDIFile()
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
