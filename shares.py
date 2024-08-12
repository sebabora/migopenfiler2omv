import xml.etree.ElementTree as xp 

def parseShare(filename = "Roboczy_IT.info.xml"):
   tree = xp.parse("/srv/olddata/" + filename)
   root = tree.getroot()
   for child in root:
        if child.tag != "group" or child.tag != "network":
            print(child.tag," =>",  child.attrib)
def getSharesList(openfilerDataPath = "/srv/olddata"):
    print("retriving list of files to prase")
    print("------------- --------------------")
    print("------------- --------------------")
    print("------------- --------------------")
   
parseShare()
getSharesList()

tlist = []
tlist.append("lipa")
tlist.append("kipa")

arry = {}

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
