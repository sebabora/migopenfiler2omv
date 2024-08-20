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
import logging as log

testFilePath = "testfiles/"
testOutputFilePath = testFilePath + "output/"

defaultPassword = "P5WhBV9j8Q8"
#
# KISS
#

log.basicConfig(filename="testfiles/output/output.log", level=log.DEBUG)


# omvUser = {
#     "name" : str,
#     "uid" : int,
#     "tags" : list,
#     "groups" : list,
#     "shell" : str,
#     "password" : str,
#     "email" : str,
#     "comment" : str,
#     "disallowusermod" : bool,
#     "sshpubkeys" : list[str],
# }

# omvGroup = {
#     "name" : str,
#     "gid" : int,
#     "tags" : list,
#     "comment" : str,
#     "members" : list[str],
# }

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

UsersList = []
GroupList = []

whiteListedUsers = []
blacklistedUsers = []


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

    omvUser = {}
    omvUser["name"] = entry.get("givenName")[0]
    omvUser["uid"] = entry.get("uidNumber")[0]
    # omvUser["tags"] = {""}
    omvUser["tags"] = [""]
    omvUser["groups"] =["users", omvUser["name"]]
    omvUser["shell"] = entry.get("loginShell")[0]
    # NOTE: it is better to have default password then to not have one set at all
    omvUser["password"] = defaultPassword
    # tUser.password=entry.get("")[0]
    omvUser["email"] = omvUser["name"] + "@midas.pl"
    omvUser["comment"] = entry.get("")
    omvUser["disallowusermod"] =  True

    omvUser["sshpubkeys"] = [""]
    # tUser.sshpubkeys=entry.get("")
    # tUser.oldidNumber=entry.get("sambaSID")[0]
    # tUser.homeDir=entry.get("homeDirectory")[0]
    # tUser.passwordHash =entry.get("userPassword")[0]
    # tUser.sambaNTPassword =entry.get("sambaNTPassword")[0]
    # # print("Samba NT Password: ", tUser.sambaNTPassword)
    # tUser.gid=entry.get("gidNumber")[0]
    ## TODO: somekind verbose printing
    #
    # print("Parsing user: ", tUser.name, tUser.uid)

    log.debug("Parsing user: %s", omvUser)

    return omvUser

def parseGroup(entry):

    omvGroup = {}
    omvGroup["groupname"] = entry.get("cn")[0]
    omvGroup["gid"] = entry.get("gidNumber")
    omvGroup["tags"] = []
    omvGroup["members"] = entry.get("memberUid")

    ## TODO: somekind verbose printing
    #
    log.debug("Parsing user")

    return omvGroup

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
                    UsersList.append(parseSamAccount(record))
                    continue
                if attributs.count("posixGroup") > 0:
                    GroupList.append(parseGroup(record))
                    continue
            else:
                continue
        
        # pprint(record)
        recordCounter += 1
    ## TODO: some kind verbose printing 

    log.info("Found %i records", recordCounter)
    log.info("\tFound %s users", len(UsersList))
    log.info("\tFound %s gropus", len(GroupList))

    # print("Records: ", recordCounter)
    # print("Parsed Users: ", len(UsersList))
    # print("Parsed Groups: ", len(GroupList))
    
def createOmvUser():
    omvCmdCreateUserPrefix = "-u amin 'UserMgmt' 'setUser'"
    for user in UsersList:
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
    
def importBlacklistedGroups(csvFilePath = "testfiles/blacklistedGroups.csv"):
    
    if os.path.isfile(csvFilePath):
        tGroup = {}
        with open(csvFilePath, "r", newline='') as csvfile:
            csvreader = csv.reader(csvfile, dialect='excel', delimiter=";")

            rowCounter = 1
            for row in csvreader:
                if rowCounter == 1:
                    log.info("Ignoring first line of CSV file")
                    rowCounter += 1
                else:
                    tGroup["groupname"] = row[0]
                    tGroup["gid"] = row[1]
                    tGroup["members"] = row[2]
                    ## TODO: remove email suffix
                    # tGroup["email"] = tUser["name"] + "@midas.pl"
                    blacklistedUsers.append(tGroup)

                # print(', '.join(row))
                print(tGroup)
    else:
        print("file dosn't exists")
        sys.exit(1)

def importBlacklistedUsers(csvFilePath = "testfiles/blacklisted.csv"):
    
    if os.path.isfile(csvFilePath):
        print("file exists")
    else:
        print("file dosn't exists")
        sys.exit(1)
    tUser = {}
    with open(csvFilePath, "r", newline='') as csvfile:
        csvreader = csv.reader(csvfile, dialect='excel', delimiter=";")

        rowCounter = 1
        for row in csvreader:
            if rowCounter == 1:
                log.info("Ignoring first line of CSV file")
                rowCounter += 1
            else:
                tUser["comment"] = row[0]
                tUser["name"] = row[1]
                tUser["password"] = row[2]
                ## TODO: remove email suffix
                # tUser["email"] = tUser["name"] + "@midas.pl"
                blacklistedUsers.append(tUser)

            # print(', '.join(row))
            print(tUser)
        print("DELETING")
        csvfile.close()
        
    
def importWhitelistedUsers(csvFilePath = "testfiles/smbuserspwds.csv"):
    ## TODO: only one user sborawski
    
    if os.path.isfile(csvFilePath):
        
        log.info("Reading users white list")

        omvUser = {}
        with open(csvFilePath, "r", newline='' ) as csvfile:
            csvreader = csv.reader(csvfile, dialect='excel', delimiter=";")
            rowCounter = 1
            for row in csvreader:
                # skip the fist row (is there a function for this ? )
                # print(type(row))
                # print("Range: ", range(row))
                # print("Len: ", len(row))
                
                # for i in range(len(row)):
                #     print(i)
                #     print(row[i])

                if rowCounter == 1:
                    log.info("Ignoring first line of CSV file")
                    rowCounter += 1
                else:
                    omvUser["comment"] = row[0]
                    omvUser["name"] = row[1]
                    omvUser["password"] = row[2]
                    omvUser["email"] = omvUser["name"] + "@midas.pl"

                    whiteListedUsers.append(omvUser)
                    # print(omvUser)
                    # print(',-> '.join(row))
            print("")

            csvfile.close()
    else:
        print("file dosn't exists")
        sys.exit(1)

def importPasswordList(csvFilePath = "testfiles/secrets.csv", nameFieldNum = 2, passFieldNumber = 3):
##
## it assumes that you have a csv file with passwords in fallowing format:
## <Full User Name>;<username>;smbpassword
## 
    if os.path.isfile(csvFilePath):
        with open(csvFilePath, "r", newline='') as csvfile:
            csvreader = csv.reader(csvfile,
                                   delimiter=";",
                                   dialect='excel')
            for row in csvreader:
                if len(row) > 1:
                    for user in UsersList:
                        if user["name"] == row[nameFieldNum-1]:
                            user["password"] = row[passFieldNumber-1]
    else:
        print("file dosn't exists")
        sys.exit(1)


def cleanUsersList() -> None:
    
    if len(blacklistedUsers) > 0:
        for user in UsersList:
            for buser in blacklistedUsers:
                if user["name"].lower() == buser["name"].lower():
                    UsersList.remove(user)
                    break
    elif len(whiteListedUsers) > 0:
        for user in UsersList:
            deleteUser = True
            for wuser in whiteListedUsers:
                if user["name"].lower() == wuser["name"].lower():
                    deleteUser = False
            if deleteUser:
                UsersList.remove(user)
            # keepUser = False
            # for wuser in whiteListedUsers:
            #     if user["name"].lower() == wuser["name"]:
            #         keepUser = True
            #         print("Name: ", wuser["name"])
            # if keepUser:
            #     print("Removing user: ", user["name"])
            #     UsersList.remove(user)
        print("Cleaned list length ", len(UsersList))
    else:
        log.info("No users whitelist or blacklist has been provided")
        print("noting to remove")
    
def cleanGroupList() -> None:
    print("test")
    # if len(blacklistedUsers) > 0:
    #     for group in GroupList:
    #         for bgroup in blacklistedUsers:
    #             if group["groupname"].lower() == bgroup["groupname"] :
    #                 GroupList.remove(group)
    #                 break
    # elif len(whiteListedUsers) > 0:
    #     for group in GroupList:
    #         deletegroup = True
    #         for wgroup in whiteListedUsers:
    #             if group["groupname"].lower() == wgroup["groupname"].lower():
    #                 deletegroup = False
    #         if deletegroup:
    #             GroupList.remove(group)
    #         # keepgroup = False
    #         # for wgroup in whiteListedUsers:
    #         #     if group["name"].lower() == wuser["name"]:
    #         #         keepgroup = True
    #         #         print("Name: ", wgroup["name"])
    #         # if keepgroup:
    #         #     print("Removing group: ", user["name"])
    #         #     GroupList.remove(group)
    #     print("Cleaned list length ", len(GroupList))
    # else:
    #     log.info("No users whitelist or blacklist has been provided")
    #     print("noting to remove")
    # print("cleaning group list")

def exportUsers(path = testOutputFilePath + "importUsersToOmv.csv"):
    
    fnames = []
    if len(UsersList) > 0:
        first = UsersList[0]
        fnames = first.keys()
    else:
        log.error("Empty Group list")
    ## TODO: exit program with error

    with open(path, "w", newline='') as csvfile:
        # dwriter = csvfile.writer(csvfile)

        dwriter = csv.DictWriter(csvfile, 
                                 fieldnames=fnames,
                                 delimiter=";",
                                 quoting=csv.QUOTE_MINIMAL,
                                 dialect="excel")
        dwriter.writeheader()
        row = {}
        for u in UsersList:
            for key, val in u.items():
                if type(val) is list:
                    row[key] = ",".join(val)
                else:
                    row[key] = val

            dwriter.writerow(row)

# users import format to openmediavault gui
# <username>;<uid>;<tags>;<email>;<password>;<shell>;<groupname,groupname,...>;<disallowusermod>
    # check if file exist 
    # ask user for interaction
    # override file by default
    # write user to file
    # 

def exportGroups(path = testOutputFilePath + "importGroupsToOmv.csv"):

    fnames = []
    if len(GroupList) > 0:
        first = GroupList[0]
        fnames = first.keys()
    else:
        log.error("Empty Group list")
    ## TODO: exit program with error

    with open(path, "w", newline='') as csvfile:
        # dwriter = csvfile.writer(csvfile)

        dwriter = csv.DictWriter(csvfile, 
                                 fieldnames=fnames,
                                 delimiter=";",
                                 quoting=csv.QUOTE_MINIMAL,
                                 dialect="excel")
        dwriter.writeheader()
        row = {}
        for g in GroupList:
            for key, val in g.items():
                if type(val) is list:
                    row[key] = ",".join(val)
                else:
                    row[key] = val

            dwriter.writerow(row)
# groups import format to openmediavault gui
# <groupname>;<gid>;<tags>
    # for group in GroupsList:
    #     

def printAllUsers(ul: list) -> None:

    if len(ul) > 0:
        for user in ul:
            print("Name: ", user["name"], end="")
            print(", old_uid: ", user["uid"], end="")
            print(", email: ", user["email"], end="")
            print(", groups: ", user["groups"] )
    else:
        print("No users has been found")
        sys.exit(1)

def printAllGroups(gl: list) -> None:
    
    if len(gl) > 0:
        for group in gl:
            print("GroupName: ", group["groupname"], end="")
            print("gid: ", group["gid"], end="")
            print("members: ", group["members"]) 

parseLDIFile()
importWhitelistedUsers()
# importBlacklistedUsers()

importPasswordList("testfiles/smbuserspwds.csv")

cleanUsersList()
cleanGroupList()
print("US: ", len(UsersList))
# cleanGroupList()
# printAllUsers(UsersList)

exportGroups()
exportUsers()

# printAllUsers(UsersList)

# try:
#     proc = subprocess.check_output(omvCmdPath + omvCmdPrintAllGroups, stderr=subprocess.STDOUT, shell=True)
# except IOError as e:
#     if e[0] == erron.EPERM:
#         sys.exit("jou need to have root privileges to run omv-rpc script")
