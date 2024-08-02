# Migration tool for old file server system called openfiler to newer openmediavault

### Where to start ?
- [ ] current prepare user list for creation on new system
### Things to do:
- [ ] Implement necessery switches source path, destination path, assuming that the software will be run on destination system
- [ ] Prepare user list for creation on new system
    - [ ] retrive users form old system
    - [ ] create white and black user list (list of active and inactive users)
    - [ ] decrypt or provide password list
- [ ] Create users on new system
    - [ ] test creation of users on new system using api
    - [ ] test creation of users on new system using system cli
- [ ] Prepare share list from old system
    - [ ] Parse config file of samba
    - [ ] Parse share info files in xml
    - [ ] Prapare white and black list of shares for creation
    - [ ] Prepare access list for shares
- [ ] Test creation of shares using RPC api
- [ ] Create shares on the new system with apropriet rights
- [ ] Copy data and fix rights on new system

### Test column
- Task title ~3d #type @name yyyy-mm-dd
### Completed Column ✓
- Complited task title 
