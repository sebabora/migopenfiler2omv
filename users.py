from collections import OrderedDict
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

ofUsersList : list = []
ofGroupsList : list = []

whiteListedUsers : list = []
blacklistedUsers : list = []


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
    omvUser["name"] = entry.get("givenName")[0].lower()
    omvUser["uid"] = entry.get("uidNumber")[0]
    # omvUser["tags"] = {""}
    omvUser["tags"] = [""]
    omvUser["groups"] =["users", omvUser["name"].lower()]
    omvUser["shell"] = entry.get("loginShell")[0]
    # NOTE: it is better to have default password then to not have one set at all
    omvUser["password"] = defaultPassword
    # tUser.password=entry.get("")[0]
    omvUser["email"] = omvUser["name"] + "@midas.pl"
    omvUser["comment"] = entry.get("")
    omvUser["disallowusermod"] =  True

    omvUser["sshpubkeys"] = [""]
    ## TODO: somekind verbose printing
    #
    log.debug("Parsing user: %s", omvUser)
    return omvUser

def parseGroup(entry):

    omvGroup = {}
    omvGroup["groupname"] = entry.get("cn")[0].lower()
    omvGroup["gid"] = entry.get("gidNumber")
    omvGroup["tags"] = []
    ## TODO : to lower case
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
                    ofUsersList.append(parseSamAccount(record))
                    continue
                if attributs.count("posixGroup") > 0:
                    ofGroupsList.append(parseGroup(record))
                    continue
            else:
                continue
        
        # pprint(record)
        recordCounter += 1
    ## TODO: some kind verbose printing 

    log.info("Found %i records", recordCounter)
    log.info("\tFound %s users", len(ofUsersList))
    log.info("\tFound %s gropus", len(ofGroupsList))

    # print("Records: ", recordCounter)
    # print("Parsed Users: ", len(ofUsersList))
    # print("Parsed Groups: ", len(ofGroupsList))
    
def createOmvUser():
    omvCmdCreateUserPrefix = "-u amin 'UserMgmt' 'setUser'"
    for user in ofUsersList:
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
                    tGroup["groupname"] = row[0].lower()
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

        with open(csvFilePath, "r", newline='' ) as csvfile:
            csvreader = csv.reader(csvfile, dialect='excel', delimiter=";")
            ## skip headers
            next(csvreader)
            for row in csvreader:
                omvUser = {}
                omvUser["comment"] = row[0]
                omvUser["name"] = row[1]
                omvUser["password"] = row[2]
                omvUser["email"] = omvUser["name"] + "@midas.pl"

                whiteListedUsers.append(omvUser)
                # print(omvUser)
                # print(',-> '.join(row))
            print("White listed users:", len(whiteListedUsers))
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
                    for user in ofUsersList:
                        if user["name"].lower() == row[nameFieldNum-1].lower():
                            user["password"] = row[passFieldNumber-1]
    else:
        print("file dosn't exists")
        sys.exit(1)


def cleanofUsersList(manual = True) -> None:
    if len(blacklistedUsers) > 0:
        for user in ofUsersList:
            for buser in blacklistedUsers:
                if user["name"].lower() == buser["name"].lower():
                    ofUsersList.remove(user)
                    break
    elif len(whiteListedUsers) > 0:
        if manual: print("Removing user manualy")
        for user in ofUsersList:
            delUser = True
            # print(user["name"].lower())
            if manual:
                # answer = input("Remove user %s [y/n]: " % user["name"]).lower()
                print("Remove user %s [y/n]: " % user["name"].lower(), end="")
                answer = input()
                if answer == "y":
                    ofUsersList.remove(user)
                    continue
                elif answer == 'n':
                    continue
                else:
                    print('wrong answer')
            else:
                for wluser in whiteListedUsers:
                    # print("Compering user", user["name"].lower(), "==", wluser["name"].lower())
                    if user["name"].lower() == wluser["name"].lower():
                        print("%s marked to keep" % user["name"])
                        delUser = False 
                        break
            if delUser:
                print("Remove user %s [y/n]: " % user["name"].lower(), end="")
                if input().lower() == "y":
                    ofUsersList.remove(user)
                    print("Removing user: ", user["name"].lower())
        # printAllUsers(ofUsersList)        
    else:
        log.info("No users whitelist or blacklist has been provided")
        print("noting to remove")
    
def cleanofGroupsList(manual = False) -> None:
    ## based on users sice we dont need groups with no users
    ## cleaning should be done after cleaning user list
    ##
    if len(blacklistedUsers) > 0:
        for user in ofUsersList:
            for buser in blacklistedUsers:
                if user["name"].lower() == buser["name"].lower():
                    ofUsersList.remove(user)
                    break
    elif len(whiteListedUsers) > 0:
        for group in ofGroupsList:
            delGroup = True
            # print(group["name"].lower())
            if manual:
                print("Remove group %s [y/n]: " % group["groupname"].lower(), end="")
                answer = input()
                if answer == "y":
                    ofGroupsList.remove(group)
                    continue
                elif answer == 'n':
                    continue
                else:
                    print('wrong answer')
            else:
                # make sure you not deleting group with:
                # -- the same name
                # -- that has a member
                for user in ofUsersList:
                    for groupname in user["groups"]:
                        if groupname == user["name"]:
                            delGroup = False
                            break
            if delGroup:
                print("Remove group %s [y/n]: " % group["groupname"].lower(), end="")
                if input().lower() == "y":
                    ofGroupsList.remove(group)
                    print("Removing group: ", group["groupname"].lower())
        # printAllgroups(ofGroupsList)        
    else:
        log.info("No users whitelist or blacklist has been provided")
        print("noting to remove")

def exportUsers(path = testOutputFilePath + "importUsersToOmv.csv"):
    
    fnames = []
    if len(ofUsersList) > 0:
        first = ofUsersList[0]
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
        for u in ofUsersList:
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
    if len(ofGroupsList) > 0:
        first = ofGroupsList[0]
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
        for g in ofGroupsList:
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
    counter = 0
    if len(ul) > 0:
        for user in ul:
            counter += 1
            # print(counter,".Name: ", user["name"], end="")
            print("%d. Name:" % counter , user["name"], end="")
            # print(", old_uid: ", user["uid"], end="")
            print(", email:", user["email"])
            # print(", groups: ", user["groups"] )
    else:
        print("No users has been found")
        sys.exit(1)

def printAllGroups(gl: list) -> None:
    
    if len(gl) > 0:
        for group in gl:
            print("GroupName: ", group["groupname"], end="")
            print("gid: ", group["gid"], end="")
            print("members: ", group["members"]) 

def serialize2file(listofjsonsobj: list, path = testOutputFilePath + "outputUser.json"):
    with open(path, "w+") as jsonfile:
        print("serializing files")
        for entry in listofjsonsobj:
            json.dump(entry, jsonfile)
#tests:
# parseLDIFile()
# importWhitelistedUsers()
# # importBlacklistedUsers()
#
# importPasswordList("testfiles/smbuserspwds.csv")
# cleanofUsersList(False)
# cleanofGroupsList(False)
#
# print("ofUsersList:", len(ofUsersList))
# print("White listed users:", len(whiteListedUsers))
# print("ofGroupsList", len(ofGroupsList))
#
# exportUsers()
# exportGroups()
#
# serialize2file(ofUsersList)
# printAllUsers(ofUsersList)

# try:
#     proc = subprocess.check_output(omvCmdPath + omvCmdPrintAllGroups, stderr=subprocess.STDOUT, shell=True)
# except IOError as e:
#     if e[0] == erron.EPERM:
#         sys.exit("jou need to have root privileges to run omv-rpc script")
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
