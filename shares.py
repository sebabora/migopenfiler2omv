import os
import xml.etree.ElementTree as xp 
import glob
from pathlib import Path
import omvapi
from rich.console import Console
from rich.table import Table
# from omvapi import

sharedFolderList = []

def printOfShares(smbShareList : list):
    tab = Table(title="Openfilershares")
    tab.add_column("Name", justify="right", style="green", no_wrap=True)
    tab.add_column("EN", justify="center", style="blue")
    tab.add_column("Guest", justify="center")
    tab.add_column("Browseable", justify="center", style="white")
    tab.add_column("bin", justify="center", style="white")
    tab.add_column("timemachine", justify="center", style="white")
    tab.add_column("encryption", justify="center", style="white")

    print("Total number of shares %s" % len(smbShareList))

    for smbShare in smbShareList:
        tab.add_row(smbShare["name"],
                    "Y" if smbShare["enable"] else "N",
                    smbShare["guest"],
                    "Y" if smbShare["browseable"] else "N",
                    "Y" if smbShare["recyclebin"] else "N",
                    "Y" if smbShare["timemachine"] else "N",
                    "Y" if smbShare["transportencryption"] else "N")
                    # smbShare["extraoptions"],
                
    console = Console()
    console.print(tab)
    
def parseOfShares(xmlfilePath : str) -> dict:
    # TODO: usuń to bo to tymczasowe tylko
    # 
    xmltree = xp.parse(xmlfilePath)
    sharedesc = ""
    sharePublicAccess = "no"
    smbShare = {}

    smbShare["name"] = ""
    xmlroot = xmltree.getroot()

    for child in xmlroot:

        groupAccessList = []
        groupReadList = []
        groupWriteList = []

        if child.tag == "dircount":
            dircountname = child.attrib.get("name", None)
            if not dircountname:
                print("dircount not 0")
        if child.tag == "dirtype":
            dirtypename = child.attrib.get("name", None)
            if dirtypename == "share":
                print("dirtype not share")
        if child.tag == "description":
            sharedesc = child.attrib.get("value", None)
            if not sharedesc:
                smbShare["comment"] = sharedesc

        # print("tagg:", child.tag,"attrib: ", child.attrib)
        if child.tag == "smb":
            # print(child.attrib["sharename"])
            # NOTE: this is how you get value of sharename if it doesn't exists
            sharename = child.attrib.get("sharename", None)
            if "sharename" in child.attrib:
                smbShare["name"] = sharename
            else:
                print("NOTE EXISTS, in a file:", xmlfilePath)
                smbShare["name"] = ""
                continue
            if sharename != None:
                smbShare["name"] = child.attrib["sharename"]
                # print(child.attrib["sharename"])
                # smbname = child.attrib["sharename"].replace(" ", "_")
            else:
                print("sharename NONNNEE")

        if len(smbShare) > 0:
            if child.tag == "network":
                pass
                # print(child.attrib.get("network"))
            if child.tag == "access":
                sharePublicAccess = child.attrib.get("public")

            smbShare["enable"] = True
            smbShare["sharedfolderref"] = "4cf9e35a-868e-4390-b627-187409020867"
            smbShare["comment"] = ""
            smbShare["guest"] = "no"
            smbShare["readonly"] = False
            smbShare["browseable"] = child.attrib.get("browseable")
            smbShare["recyclebin"] = True
            smbShare["recyclemaxsize"] = 0
            smbShare["recyclemaxage"] = 30
            smbShare["hidedotfiles"] = True
            smbShare["inheritacls"] = False
            smbShare["inheritpermissions"] = False
            smbShare["easupport"] = False
            smbShare["storedosattributes"] = False
            smbShare["hostsallow"] = ""
            smbShare["hostsdeny"] = ""
            smbShare["audit"] = False
            smbShare["timemachine"] = False
            smbShare["transportencryption"] = False
            smbShare["extraoptions"] = ""

        if child.tag == "group":
            if child.attrib.get("read") == "yes":
                groupReadList.append(child.attrib.get("id"))
            if child.attrib.get("write") == "yes":
                groupWriteList.append(child.attrib.get("id"))
            if child.attrib.get("access") == "yes":
                groupAccessList.append(child.attrib.get("id"))

        if child.tag == "primary":
            primaryGroupId = child.attrib.get("id")
            groupAccessList.append(primaryGroupId)
            groupReadList.append(primaryGroupId)
            groupWriteList.append(primaryGroupId)
            # TODO: this can be deleted
            smbShare["primaryGroup"] = primaryGroupId

        smbShare["accesslist"] = groupAccessList
        smbShare["writelist"] = groupWriteList
        smbShare["readlist"] = groupReadList

    return smbShare

def getOfSharesList(xmlfilelist : list) -> list:
    
    for xmlfile in xmlfilelist:
        tsmbShare = parseOfShares(xmlfile)
        sharedFolderList.append(tsmbShare)
    printOfShares(sharedFolderList)

# NOTE: invoke first
def createOfSharesFromFiles(directory : Path) -> list:
    xmlfiles = []
    for file in glob.glob(str(directory.joinpath("*.xml"))):
        xmlfiles.append(file)
    # for path in xmlfiles:
    #     print(path)
    return xmlfiles 

getOfSharesList(createOfSharesFromFiles(Path('/srv/olddata/')))

"""
=== sharemgmt ===
"getCandidates"
"enumerateSharedFolders"
"getList"
"get"
"set"
"delete"
"getPrivileges"
"setPrivileges"
"getPrivilegesByRole"
"setPrivilegesByRole"
"copyPrivileges"
"getFileACL"
"setFileACL"
"getPath"
"enumerateSnapshots"
"enumerateAllSnapshots"
"createSnapshot"
"createScheduledSnapshotTask"
"enumerateScheduledSnapshotTasks"
"enumerateAllScheduledSnapshotTasks"
"deleteSnapshot"
"restoreSnapshot"
"fromSnapshot"
"getSnapshotLifecycle"
"setSnapshotLifecycle"
    
"""
