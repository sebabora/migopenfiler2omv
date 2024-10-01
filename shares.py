import os
import xml.etree.ElementTree as xp 

def parseShare(filename = "Roboczy_IT.info.xml"):
   tree = xp.parse("/srv/olddata/" + filename)
   root = tree.getroot()
   for child in root:
        # if child.tag != "group" or child.tag != "network":
        # if child.tag == "group": 
        #     for attr in child.attrib:
        #         print(child.tag,"=>",  child.attrib)
        #         print(type(child.tag),"=>",  type(child.attrib))
        if child.tag == "group" or child.tag == "network":
            continue
        else:
            print(child.tag, "->" , child.attrib)


def getSharesList(openfilerDataPath = "/srv/olddata"):
    parseShare()

def list_files(startpath):
    if not startpath:
        startpath = "/home/sebastian/"
    else:
        print("Start path ", startpath)

    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))
def list_xml_directory_files(path2openfilersys = "/srv/olddata/"):
    for root, dirs, files in os.walk(path2openfilersys):
        if layer == 1:
            print(files)

if __name__ == "__shares.py":
    print("Exp")
 
# parseShare()
getSharesList()

   # tree = xp.parse("/srv/olddata/" + filename)
   # root = tree.getroot()
   # for child in root:
   #      # if child.tag != "group" or child.tag != "network":
   #      if child.tag == "group": 
   #          for attr in child.attrib:
   #              print(child.tag,"=>",  child.attrib)
   #              print(type(child.tag),"=>",  type(child.attrib))
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
