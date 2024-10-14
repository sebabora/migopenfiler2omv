import json
import subprocess
import os
import logging
from rich.console import Console
from rich.table import Table
from rich.table import box
# from rich.jason import JSON
from rich import print_json
# from click import Context
import click

def errorPrinter(response : dict):
    err = response["error"]
    print("Error code:", err["code"])
    print("Error message:", err["message"])

# NOTE: zrobione
def omvRpcCmd(cmd = "-h"):
    omvCmdPath = '/usr/sbin/omv-rpc'
    user = '-u admin'
    if os.getuid() != 0:
        exit("You need to have root privileges to run omv-rpc script")
    else:
        try:
            proc = subprocess.check_output("{0} {1} {2}".format(omvCmdPath, user, cmd), 
                                           stderr=subprocess.STDOUT, shell=True)
            # print(type(proc))
            return proc
        except subprocess.CalledProcessError as e:
            print("[ERROR]: Error running omv-rpc")
            proc = e.output.decode()
# NOTE: zrobione
def printListofFilesystems(listoffs : list):
    for fs in listoffs:
        # print("Device name", fs["devicename"])
        # # print("ccanonicaldevicefile", fs["cannonicaldevicefile"])
        # print("uuid", fs["uuid"])
        # print("type", fs["type"])
        # print("mountpoint", fs["mountpoint"])
        # print("used", fs["used"])
        # print("available", fs["available"])
        # print("procentage", fs["procentage"])
        print(fs["description"])
        print("     mounted:", fs["mountpoint"])
        # print("_readonly", fs["_readonly"])
            # print(fs)
# NOTE: zrobione
# def getListOfFilesystems(debug = True) -> list: 
def getListOfFilesystems(ctx) -> list: 
    out = omvRpcCmd("'FileSystemMgmt' 'enumerateMountedFilesystems' '{\"includeroot\": false}'")
    
    try:
        fileSystemList = json.loads(out)

        if len(fileSystemList) > 0:
            print("objcect: ", ctx.obj['DEBUG']) 

            if ctx.obj['DEBUG']:
                print_json(json.dumps(fileSystemList, indent=2))
                printListofFilesystems(fileSystemList) ## TODO: remove
            return fileSystemList
        else:
            ## TODO: loging object
            print("empty list")
            return []
    except ValueError:
        print('Decoding JSON has failed')
        return []
        ## TODO: exit program with code 1 
# FIX: czy to jest potrzebne ?
def printListOfSystemUsers(omvUsersList : list):
    for user in omvUsersList:
        print(user)

# NOTE: zrobione
def getOmvSystemUsers(ctx) -> list:
    out = omvRpcCmd("'UserMgmt' 'enumerateSystemUsers'")

    try:
        omvSystemUsersList = json.loads(out)

        if len(omvSystemUsersList) > 0:
            if ctx.obj["DEBUG"]: print_json(json.dumps(omvSystemUsersList , indent=2))
            printOmvUsers(omvSystemUsersList)
            # if debug: printListOfSystemUsers(omvSystemUsersList)
            # if debug: printListOfSystemUser(omvSystemUsersList) ## TODO: remove
            return omvSystemUsersList
        else:
            ## TODO: loging object
            print("empty list")
            return []
    except ValueError:
        print('Decoding JSON has failed')

# NOTE: zrobione
def printOmvUsers(omvUsersList : list):
    # omvCmdPrintAllUsers = "'UserMgmt' 'enumerateUsers'"
    # omvRpcCmd(omvCmdPrintAllUsers)
    tab = Table(title="OpenMediaVault users")
    tab.add_column("Name", justify="right", style="cyan", no_wrap=True)
    tab.add_column("uid", justify="center", style="green", no_wrap=True)
    tab.add_column("gid", justify="center")
    tab.add_column("dir", justify="left")
    tab.add_column("shell", justify="left")
    tab.add_column("groups", justify="right")
    
    print("Found %s openmediavault users" % len(omvUsersList))
    for user in omvUsersList:
        tab.add_row(user['name'], 
                    str(user['uid']), 
                    str(user['gid']), 
                    user['dir'], 
                    user['shell'], 
                    ", ".join(user['groups'])
                    )
        # print("User: ", user['name'])

    console = Console()
    console.print(tab)

# NOTE: zrobione
def getOmvUsers(ctx) -> list:
    out = omvRpcCmd("'UserMgmt' 'enumerateUsers'")
    try:
        omvUsers = json.loads(out)
        if ctx.obj["DEBUG"]: print_json(json.dumps(omvUsers, indent=2))
        # if debug: print("TYP:", type(omvUsers))
        
        if len(omvUsers) > 0:
            printOmvUsers(omvUsers)
        else:
            print("EMPTY LIST")
    except ValueError:
        print('Decoding JSON has failed')
    print("echo")

# NOTE: zrobione
def printOmvGroups(omvGroupsList : list):
    tab = Table(title="OpenMediaVault groups")
    tab.add_column("Group Name", justify="right", style="cyan", no_wrap=True)
    tab.add_column("uid", justify="center", style="green", no_wrap=True)
    tab.add_column("members", justify="right")
    tab.add_column("system", justify="left")
    
    print("Found %s openmediavault groups" % len(omvGroupsList))
    for group in omvGroupsList:
        tab.add_row(group['name'], 
                    str(group['gid']), 
                    ", ".join(group['members']),
                    str(group['system']), 
                    )
    console = Console()
    console.print(tab)
    
# NOTE: zrobione
def getOmvGroups(ctx, systemGroups = False) -> list:
    if systemGroups: out = omvRpcCmd("'UserMgmt' 'enumerateSystemGroups'")
    else: 
        out = omvRpcCmd("'UserMgmt' 'enumerateGroups'")
    try:
        omvGroups = json.loads(out)
        if ctx.obj["DEBUG"]: print_json(json.dumps(omvGroups, indent=2))

        if len(omvGroups) > 0:
            printOmvGroups(omvGroups)
        else:
            print("EMPTY LIST")
    except ValueError:
        print('Decoding JSON has failed')
# TODO: debug and table fix based on needed data for rpc api
def printSharedFolders(omvSharedFoldersList : list, print_uuid=False):
    print("Found %s openmediavault shares" % len(omvSharedFoldersList))
    tab = Table(title="OpenMediaVault shares")
    tab2 = Table(title="OpenMediaVault shares", box=None)
    
    console = Console()
    if print_uuid: 
        tab.add_column("Name", justify="right", style="blue", no_wrap=True)
        tab.add_column("act", justify="center", style="red")
        tab.add_column("device", justify="left", style="white")
        tab.add_column("reldirpath", justify="left", style="green")
        tab.add_column("snaps", justify="center")
        # tab.add_column("
        
        for share in omvSharedFoldersList:
            tab.add_row(share['name'],
                        str(int(share['_used'])),
                        share['device'], 
                        share['reldirpath'],
                        str(share['snapshots'])
                        )
            # getSharedFolderPermissions(share)
        console.print(tab)
    else:
        tab2.add_column("act", justify="center", style="red")
        tab2.add_column("Name", justify="left", style="blue", no_wrap=True)
        tab2.add_column("device", justify="left", style="magenta")
        tab2.add_column("uuid", justify="left", style="green")
        
        for share in omvSharedFoldersList:
            # getSharedFolderPermissions(share)
            tab2.add_row(str(int(share['_used'])),
                        share['name'],
                        share['device'], 
                        share['uuid'],
                        )
        console.print(tab2)
        
def getSharedFolderPermissions(sharedFolder : dict, debug = True) -> bool:
    # request_test = {'uuid' : "df8e639f-0706-47c8-bd8f-f10a3dd65b0a"}
    request_test = {'uuid' : ""}
    request = request_test
    # request = {"uuid" : sharedFolder["uuid"]}

    request_json = json.dumps(request, ensure_ascii=True, separators=(', ', ':'))
    cmd_request = f"'ShareMgmt' 'getPrivileges' '{request_json}'"

    response_raw = omvRpcCmd(cmd_request)
    try:
        response = json.loads(response_raw)
        print(response)
        print("TYPE: ", response["response"])
        if response["response"] == "null":
            errorPrinter(response)
            return False
    except ValueError:
        print('Decoding JSON has failed')
    return True
def setSharedFolderPermissions(uuid : str, privileges : list):
    #[{'type': 'user', 'name': 'linusrtest', 'perms': None}, {'type': 'user', 'name': 'rpcUsr', 'perms': None}, {'type": 'group', 'name': 'rpcUsrGr', 'perms': None}]
    pass

def getSharedFolders(ctx, print_uuid = False) -> list:
    out = omvRpcCmd("'ShareMgmt' 'enumerateSharedFolders'")

    try:
        omvShares = json.loads(out)
        if ctx.obj["DEBUG"]: print_json(json.dumps(omvShares, indent=2))

        if len(omvShares) > 0:
            printSharedFolders(omvShares, print_uuid)
            return omvShares
        else:
            print("EMPTY LIST")
            
    except ValueError:
        print('Decoding JSON has failed')
# -------------------------------------------------------------------------
def createSharedFolder(sharedFolder : dict) -> bool:
    request = {"name" : sharedFolder["name"]}

    request_json = json.dumps(request, ensure_ascii=True, separators=(', ', ':'))
    cmd_request = f"'ShareMgmt' 'set''{request_json}'"

    response_raw = omvRpcCmd(cmd_request)
    try:
        response = json.loads(response_raw)
        if response["response"] == "null":
            errorPrinter(response)
            return True
        else:
            print("Deletedl group:", sharedFolder["name"])
            return False
    except ValueError:
        print('Decoding JSON has failed')

    pass

def deleteSharedFolder(sharedFolder : dict, debug = True) -> bool:
    request = {"name" : user["name"]}

    request_json = json.dumps(request, ensure_ascii=True, separators=(', ', ':'))
    cmd_request = f"'UserMgmt' 'deleteUser' '{request_json}'"

    response_raw = omvRpcCmd(cmd_request)
    try:
        response = json.loads(response_raw)
        if response["response"] == "null":
            errorPrinter(response)
            return True
        else:
            print("Deletedl group:", user["name"])
            return False
    except ValueError:
        print('Decoding JSON has failed')

def deleteSharedFolders(sharedFoldersList : list, ctx) -> bool:
    for sharedFolder in sharedFoldersList:
        deleteSharedFolder(sharedFolder)
    pass
# NOTE: done
def printShares(omvShareList : list, print_uuid=False):
    print("Found %s openmediavault shares" % len(omvShareList))
    tab = Table(title="OpenMediaVault shares")
    tab2 = Table(title="OpenMediaVault shares", box=None)
    
    console = Console()
    if not print_uuid: 
        tab.add_column("sharedfoldername", justify="right", style="blue", no_wrap=True)
        tab.add_column("browseable", justify="center", style="red")
        tab.add_column("guest", justify="left", style="white")
        tab.add_column("readonly", justify="left", style="green")
        # tab.add_column("
        
        for share in omvShareList:
            tab.add_row(share['sharedfoldername'],
                        str(share['browseable']),
                        share['guest'],
                        str(share['readonly'])
                        )
            # getSharesPermissions(share)
        console.print(tab)
    else:
        tab2.add_column("sharedfoldername", justify="left", style="red")
        tab2.add_column("uuid", justify="center", style="blue", no_wrap=True)
        tab2.add_column("sharedfolderref", justify="center", style="magenta")
        # tab2.add_column("hostsallow", justify="left", style="green")
        # tab2.add_column("hostsdeny", justify="left", style="blue")
        
        for share in omvShareList:
            tab2.add_row(share['sharedfoldername'],
                         share['uuid'],
                         share['sharedfolderref'],
                         # share['hostsallow'],
                         # share['hostsdeny']
                         )
            # getSharesPermissions(share)
        console.print(tab2)

def getSharesPermissions(share : dict, debug = True) -> bool:
    # NOTE: check if exist
    # make support for erros and printing it
    # out = omvRpcCmd("'ShareMgmt' 'getPrivileges' '".join(share['uuid']
    # out = omvRpcCmd("'ShareMgmt' 'getPrivileges' '{0}'".format(share['uuid']))
    # print("'ShareMgmt' 'getPrivileges' '"{0}:{1}\"}\'".format("name", share['uuid']))
    # print("'ShareMgmt' 'getPrivileges' '"{0}:{1}\"}\'".format("name", share['uuid']))
    pass

def getShares(ctx, print_uuid = False) -> list:
    omvShareList = []
    limit = 2
    start = 0
    request_data = True

    response = {"total": 1, "data": []}
    while request_data:
        request = {"start" : start, "limit" : limit, "sortfiled" : "name", "stordir" : "ASC" }
        request_json = json.dumps(request, ensure_ascii=True, separators=(', ', ':'))
        cmd_request = f"'Smb' 'getShareList' '{request_json}'"

        response_raw = omvRpcCmd(cmd_request)
        
        if not response["total"] > 0:
            request_data = False
            continue

        try:
            response = json.loads(response_raw)
            if len(response["data"]) > 0:
                start = start + limit
                if ctx.obj["DEBUG"]: print_json(json.dumps(response["data"], indent=2))
            else:
                request_data = False
                continue

            for share in response["data"]:
                omvShareList.append(share)
            # omvShareList = response["data"]

            # FIX: this should display ony list of shares
            # if ctx.obj["DEBUG"]: print_json(json.dumps(omvShareList, indent=2))
        except ValueError:
            print('Decoding JSON has failed')
    else:
        print("Total number of shares %s" % len(omvShareList)) 
        printShares(omvShareList, print_uuid)
        return omvShareList

    print(type(response_raw))
    if type(response_raw) == type(None):
        print("NONNNEEE TYPE")
        return []
def createShare(share : dict, debug = True) -> bool:
    return True
def deleteShare(share : dict, debug = True) -> bool:
    return True
def deleteShares(shareList : list, debug = True) -> bool:
    return True

def createOmvUser(user : dict, debug = True):
    # request = {"start" : start, "limit" : limit, "sortfiled" : "name", "stordir" : "ASC" }
    request = {"name" : user["name"], "groups" : user["groups"], 
               "password" : user["password"],
               "email" : user["email"],
               "disallowusermod" : user["disallowusermod"],
               "sshpubkeys" : user["sshpubkeys"]}

    request_json = json.dumps(request, ensure_ascii=True, separators=(', ', ':'))
    cmd_request = f"'UserMgmt' 'setUser' '{request_json}'"
    print("cmd_request:", cmd_request)
    response_raw = omvRpcCmd(cmd_request)
    try:
        response = json.loads(response_raw)
        # FIX: use errorPrinter
        if response["response"] == "null":
            err = response["error"]
            print("Error code:", err["code"])
            print("Error message:", err["message"])
        else:
            print("created a user")
    except ValueError:
        print('Decoding JSON has failed')
    # omvRpcCmd('UserMgmt ' + json.dumps(user, sort_keys=False, default=str))

def createOmvUsers(listOfUsers : list, debug = True):
    for user in listOfUsers:
        createOmvUser(user, debug)

def createOmvGroup(group : dict, debug = True):
    request = {"name" : group["name"],
               "gid" : group["password"],
               "comment" : group["comment"],
               # FIX: pamietaj o wypelnieniu tej grupy
               "members" : group["members"]}

    request_json = json.dumps(request, ensure_ascii=True, separators=(', ', ':'))
    cmd_request = f"'groupMgmt' 'setgroup' '{request_json}'"
    print("cmd_request:", cmd_request)

def createOmvGroups(listOfGroups : list, debug = True):
    for group in listOfGroups:
        createOmvGroup(group, debug)
# NOTE: done
def deleteUser(user : dict, debug = True) -> bool:
    request = {"name" : user["name"]}

    request_json = json.dumps(request, ensure_ascii=True, separators=(', ', ':'))
    cmd_request = f"'UserMgmt' 'deleteUser' '{request_json}'"

    response_raw = omvRpcCmd(cmd_request)
    try:
        response = json.loads(response_raw)
        if response["response"] == "null":
            errorPrinter(response)
            return True
        else:
            print("Deletedl group:", user["name"])
            return False
    except ValueError:
        print('Decoding JSON has failed')

def deleteGroup(group: dict, debug = True) -> bool:
    request = {"name" : group["name"]}

    request_json = json.dumps(request, ensure_ascii=True, separators=(', ', ':'))
    cmd_request = f"'groupMgmt' 'setgroup' '{request_json}'"

    response_raw = omvRpcCmd(cmd_request)
    try:
        response = json.loads(response_raw)
        if response["response"] == "null":
            errorPrinter(response)
            return False
        else:
            print("Deleted user:", group["name"])
            return True
    except ValueError:
        print('Decoding JSON has failed')

def deleteAllOmvUsers(omvUsersList: dict, exception : str) -> bool:
    result = False
    for user in omvUsersList:
        if user["name"] == exception:
            continue
        else:
            result = result or deleteUser(user)
    return result
            
def deleteAllOmvGroups(group : dict, exception : str) -> bool:
    result = False
    for group in omvGroupsList:
        if group["name"] == exception:
            continue
        else:
            result = result or deleteGroup(group)
    return result

