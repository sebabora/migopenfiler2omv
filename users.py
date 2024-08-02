from ldif import LDIFParser
from pprint import pprint

#parser = LDIFParser(open("testfiles/ofusersdb.ldif", "rb"), 'dn=sambaDomainName=LOCALHOST,dc=openfiler,dc=nas')
parser = LDIFParser(open("testfiles/ofusersdb.ldif", "rb") )
# for dn, record in parser.parse():
#     print('got entry record: %s' % dn)
#     pprint(record)
    
for dn, record in parser.parse():
    print("Record to typ: ", type(record))
    for key, value in record.items():
        print("Value to typ ", type(value))
        for entry in value:
            print(entry)
        #print(key, " ", value)
#    for entry in record:
#        print(entry['ou'])
    #print('XXXXX: %s' % dn, 'recored read :', parser.records_read)
    #pprint(record)
    

#def printusers(userlist):
#   
#    for user in userlist:
#        print(user)
        
