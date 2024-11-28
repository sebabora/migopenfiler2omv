# from os.path import exists, isfile
from pathlib import Path
from os.path import exists
import click
import users
import data
import omvapi
# from omvapi import *
import logging
import sys
# from users import ofUsersList
from richlogging import logger as rlog 

@click.group()
@click.option('--debug/--no-debug', default=False)
@click.option('--usage', is_flag=True, help='Print commont usage of tool')
@click.version_option(version='0.0.1')
@click.help_option()
@click.pass_context
def cli(ctx, debug, usage):
    if ctx.invoked_subcommand is None:
        click.echo('invoked without subcommand')
    else:
        click.echo(f'I am about to invoke {ctx.invoked_subcommand}')
        
    click.echo('Debug mode is %s' % ('ON' if debug else 'off'))
    ctx.ensure_object(dict)
    # if usage:
    #     click.echo('Print standard usage of the application')
    # ctx.obj['USAGE'] = usage
    if debug:
        rlog.debug("Aplication debug mode")
        ctx.obj['DEBUG'] = debug
    else:
        ctx.obj['DEBUG'] = False 

@cli.command()
@click.option('--help/-h')
@click.pass_context
def help(ctx, help):
    click.echo("This script should help you migrate old openmediavault to new system OpenMediaVault")
    click.echo("Aplication will create temporary migration files if you chose to migrate data")
    click.echo("Format of this migration files is csv")
    click.echo("You can use those migration files to migrate data on new machine")

@cli.command()
@click.argument('synctype', type=click.Choice(['users', 'shares', 'data'], case_sensitive=False), default="data")
@click.pass_context
def sync(ctx, synctype):
    if synctype == 'users':
        click.echo("SYNC users")
    if synctype == 'shares':
        click.echo("SYNC shares")
    if synctype == 'data':
        click.echo("Sync data")

@cli.group(name='migrate')
@click.pass_context
def migrate(ctx):
    # click.clear()
    rlog.info("Starting migration...")

@migrate.command(name='users')
@click.option('--white-list', '-uwl', 'whiteList', 
              type=click.Path(exists=True, dir_okay=False), 
              help='list of  ')
@click.option('--black-list', '-ubl', 'blackList', 
              type=click.Path(exists=True, dir_okay=False), 
              help='list of user excluded from migration')
@click.option('--output-file', '-uo', 'usrmigfile', 
              type=click.Path(exists=True, dir_okay=False), 
              help='Parsed user output file')
@click.option('--dry-run', '-dr', 'dryrun', is_flag=True, 
              help='prints just the  info from ldif file')
@click.option('--secrets', '-sc', 'secretlistfile', 
              type=click.Path(exists=False, dir_okay=False),
              help='list of secret passwords for users in csv format')
@click.argument('ldifdbpath', required=True, type=click.Path(exists=True, 
                                                             dir_okay=False, 
                                                             path_type=Path)) 
@click.pass_context
def migrateUsers(ctx,  whiteList, blackList, usrmigfile, dryrun, secretlistfile, ldifdbpath):
    """ldifdbpath path to openfiler ldap database (ldif file) dumped by slapcat -l ofdb.ldif"""
    userMigrationPath = "./testfiles/output/"
    userMigrationFileName = "mig_users.csv" 

    secretFilePath = "./testfiles/blacklistedusers.csv"

    overwriteMigrationFile = False 

    if usrmigfile: # name of user migration file has been provided
        rlog.info(f'Found user migration file {usrmigfile}')
        # NOTE: is joining path nessesery ? answer: NO 
        # usrmigfile = userMigrationPath.join(userMigrationFileName)
        userMigrationFile = Path(usrmigfile)
        rlog.info(f'Using {usrmigfile} migration file')
    else:
        userMigrationFile = Path(userMigrationPath.join(userMigrationFileName))
        rlog.info(f'Using default user migration file {userMigrationFileName}')

    if userMigrationFile.exists() & userMigrationFile.is_file():
        rlog.info(f'Found user migration file {str(userMigrationFile)}')
        # answer = click.prompt("User migration file exists! Overwrite it?", type=str)
        # if answer == "y":
        #     click.echo("answer yes")
        # else:
        #     click.echo("answer no")
        # NOTE: is this realy nessery if i allways overwrite migration file? 
        if click.confirm("User migration file exists! Overwrite it?", default=True):
            rlog.info(f'Overwriting migration file {str(userMigrationFile)}')
        else:
            click.echo("Skip parsing users use migration file")
            rlog.info(f'Migration file won\'t be overwritted')
    else:
        rlog.info(f'Migration file does not exists, crearing user migration file')

    rlog.info(f'Parsing ldif database')
    users.parseLDIFile(ldifdbpath)
    rlog.info(f'Found {users.ofUsersList} user entries')

    # read black list or white list users list from file
    if whiteList:
        users.importBlacklistedUsers(whiteList)
        rlog.info(f'Size of white user list {len(users.whiteListedUsers)}')

    if blackList:
        users.importBlacklistedUsers(blackList)
        rlog.info(f'Size of black user list {len(users.blacklistedUsers)}')

    users.cleanofUsersList(True)
    rlog.info(f'Cleaned user list entries: {len(users.ofUsersList)}')

    # NOTE: this has to run !!

    if secretlistfile:
        users.importPasswordList(secretlistfile)
    else:
        users.importPasswordList()

    if dryrun:
        users.printAllUsers(ofUsersList)
    
    users.exportUsers(str(userMigrationFile))
    
    rlog.info(f'Creating {len(users.ofUsersList)} users')
    # omvapi.createOmvUsers(users.ofUsersList)

@migrate.command(name='groups')
@click.option('--white-list', '-uwl', 'whiteList', 
              type=click.Path(exists=True), help='list of  ')
@click.option('--black-list', '-ubl', 'blackList', 
              type=click.Path(exists=True), help='list of user excluded from migration')
@click.option('--output-file', '-uo', 'grpmigfile', 
              type=click.Path(exists=True), help='Parsed user output file')
@click.option('--dry-run', '-dr', is_flag=True, help='prints just the  info from ldif file')
@click.argument('ldifdbpath', required=True, type=click.Path(exists=True)) 
@click.pass_context
def migrateGroups(ctx, whiteList, blackList, grpmigfile, dry_run, ldifdbpath):
    """LDIFPATH path to openfiler ldap database (lidfdb file) dumped by slapcat -l ofdb.ldif file"""
    groupMigrationPath = "./testfiles/output/"
    groupMigrationFileName = "usersmigration.csv" 
    
    if grpmigfile.exists() & grpmigfile.is_file():
        # overwritemigfile = click.prompt("Do you whant to overwirte group migration file?",
        #                                 default="no",
        #                                 confirmation_prompt=False,
        #                                 click.Choice(['yes', 'y', 'no', 'n']),
        #                                 show_choices=True)
        overwritemigfile.lower()
        if overwritemigfile == 'yes' or overwritemigfile == 'y':
            users.exportGroups(grmigfile)

    if blackList:
        users.importBlacklistedGroups(blackList)
        #clean groups that aren't blacklisted
    else:
        #print list of users
        # cleanmanually = click.prompt("Do you whant to clean group list manualy",
        #                              default="no",
        #                              confirmation_prompt=False,
        #                              click.Choice(['yes','y','no','n']),
        #                              show_choices=True)
        if cleanmanually == 'yes' or 'y':
            users.cleanofGroupsList(True)
        else:
            users.cleanofGroupsList(False)


@migrate.command(name='sharedfolders')
@click.argument('sourceDir', type=click.Path(exists=True)) 
@click.option('--black-list', '-sfbl', 'blackList', 
              type=click.Path(exists=True), help='cvs format black list of sharedfolders')
@click.pass_context
def migrateSharedFolders(ctx, sourceDir, blackList):

    # blackList
    rlog.info(f'Migrating shares from {sourceDir}')
    # NOTE: read users:q from migration file or from ldif file
    for share in shares.sharedFolderList:
        # rlog.info(f'Creating share {share['name']}')
        omvapi.createSharedFolder(share)

    click.echo("migrating sharedfolders")
    # TODO: 
    # - parse users,
    # - parse groups,
    # - create temporary files for users and groups,
    # - 
    pass

@migrate.command(name='shares')
@click.argument('sourceDir', type=click.Path(exists=True))
@click.option('--black-list', '--sbl', 'blackList', type=click.Path(exists=True))
@click.pass_context
def migrateShares(ctx, sourceDir, blackList):
    pass

@migrate.command(name='data')
@click.option('--dry-run', '-dr',
              is_flag=True, show_default=True, default=True, help="Preforms dry run")
@click.argument('src', nargs=1, type=click.Path(exists=True, file_okay=False))
@click.argument('dst', nargs=1, type=click.Path(exists=True, file_okay=False))
@click.pass_context
def migrateData(ctx,dry_run, src, dst):
    click.echo(click.format_filename(src))
    click.echo(click.format_filename(dst))

    dataMigrationFilePathStr = './testfiles/'
    # FIX: create this file
    dataMigrationFileName = 'datamigration.csv'

    # TODO: 
    # exexucte rsync for every single catalog
    #
    rlog.info(f'Copying data...')
    # use some kind of list of shares to copy data
    # from migration file
    if click.confirm("Do you want to use share migration file ", default=True):
        rlog.info(f'Using migration file {dataMigrationFilePathStr.join(dataMigrationFileName)}')
        # FIX: read migration file here!
    else:
        answer = click.prompt("Provide path to migration file:", type=str)
        if answer:
            migrationFilePath = Path(answer)
            if migrationFilePath.exists() and migrationFilePath.is_file():
                click.info(f'Using migration file {str(migrationFilePath)}')
            else:
                rlog.error(f'File path does not exists')
                sys.exit(1)
    
    if dry_run:
        rlog.info(f'Dry-run copying data from: {src} {dst}')
        # data.copyShareData(Path(src), Path(dst), True)
    else:
        rlog.info(f'Copying data from: {src} {dst}')
        # data.copyShareData(Path(src), Path(dst), False)
#
# -------------------------------------------------------------------------------
#
# NOTE: dorób opcje debug
@cli.command()
@click.argument('omvObj', 
                type=click.Choice(['users', 
                                   'systemusers', 
                                   'groups', 
                                   'systemgroups', 
                                   'sharedfolders',
                                   'shares', 
                                   'disks'], 
                                  case_sensitive=False), 
                default="users")
@click.option('--print-uuid', '-pu', is_flag=True, help='print only uuids and names in debug mode')
@click.option('--asc/--desc', default=True)
@click.pass_context
def show(ctx, omvobj, print_uuid, asc):
    
    if omvobj == "users":
        omvapi.getOmvUsers(ctx)
    if omvobj == "systemusers":
        omvapi.getOmvSystemUsers(ctx)
    if omvobj == "groups":
        omvapi.getOmvGroups(ctx, False)
    if omvobj == "systemgroups":
        omvapi.getOmvGroups(ctx, True)
    if omvobj == "sharedfolders":
        omvapi.getSharedFolders(ctx, print_uuid)
    if omvobj == "shares":
        omvapi.getShares(ctx, print_uuid)
    if omvobj == "disks":
        omvapi.getListOfFilesystems(ctx)
    # print('type: ', type(ctx))
# @cli.command(name="test")
# @click.argument('creation', type=click.Choice(['sharedfolder','share','users','groups']) 
TEST_SUBJECT=['sharedFolder', 'share', 'user', 'group']
TEST_ACTIONS=['creation', 'deletion', 'permission', 'sync', 'migration']


@cli.group()
@click.pass_context
def test(ctx):
    # NOTE: is there a way to know what action had been choosen ?
    rlog.info("Testing functionality")
    pass
    
@test.command(name='user')
@click.argument('action', type=click.Choice(TEST_ACTIONS))
# @click.option('--user')
@click.pass_context
def testUser(ctx, action):
    test_user = {"name" :"rpcUsr",
                 "groups" : ["rpcUsrGr","users"],
                 "password" : "dupamaryski",
                 "email" : "",
                 "disallowusermod" : False, 
                 "sshpubkeys" : []
                 }

    if action == 'creation':
        rlog.info("Creating test user")
        omvapi.createOmvUser(test_user)
    elif action == 'deletion':
        omvapi.deleteOmvUser(test_user)
        rlog.info("Test deletion of user")
    elif action == 'permission':
        # NOTE: is this make sens here
        rlog.info("Test user permissions")
    elif action == 'sync':
        omvapi.getOmvUsers(test_user)
        rlog.info("Test user sync")

        # NOTE: is this make sens ?
    elif action == 'migration':
        click.echo("Test user migration")

@test.command(name='group')
@click.argument('subject', type=click.Choice(TEST_ACTIONS))
@click.pass_context
def testGroup(ctx, subject):
    click.echo("group")
    test_group = {"name" : "rpcGroup",
                  # NOTE: czy napewno podaje dane typu uid ?
                  "gid" : "1045",
                  "members" : ["rpcUsr"]
                  }
    
    if subject == 'creation':
        rlog.info("Creating test user")
        omvapi.createOmvUser(test_group)
    elif subject == 'deletion':
        omvapi.deleteOmvUser(test_group)
        rlog.info("Test deletion of user")
    elif subject == 'permission':
        # NOTE: is this make sens here
        rlog.info("Test user permissions")
    elif subject == 'sync':
        omvapi.getOmvUsers(test_group)
        rlog.info("Test user sync")

        # NOTE: is this make sens ?
    elif subject == 'migration':
        click.echo("Test user migration")
    pass

@test.command(name='sharedFolder')
@click.argument('action', type=click.Choice(TEST_ACTIONS))
# @click.option('--user')
@click.pass_context
def testSharedFolder(ctx, action):
    click.echo("sharedfolder")
    test_sharedFolder = {"name" : "rpcSharedFolder",
                         "mntent" : { # NOTE: get disk reference first
                            "devicefile" : "/dev/mapper/omv--vg2-data",
                            "fsname" : "/dev/disk/by-uuid/8d3565a5-652a-4bec-ad04-3f5bcca74a67",
                            "dir" : "/srv/dev-disk-by-uuid-8d3565a5-652a-4bec-ad04-3f5bcca74a67",
                            "type" : "ext4",
                            "postixacl" : True,
                            },
                         "reldirpath" : "rpcSharedFolder/",
                         "mntentref" : "", # uuid somekind ?
                         "device" : "/dev/disk/by-id/dm-name-omv--vg2-data", 
                         "mode" : "755",
                         "tags" : "", # could be empty or none ?
                        }
    if action == 'creation':
        rlog.info("Creating test user")
        omvapi.createOmvUser(test_sharedFolder)
    elif action == 'deletion':
        omvapi.deleteOmvUser(test_sharedFolder)
        rlog.info("Test deletion of user")
    elif action == 'permission':
        # NOTE: is this make sens here
        rlog.info("Test user permissions")
    elif action == 'sync':
        omvapi.getOmvUsers(test_sharedFolder)
        rlog.info("Test user sync")

        # NOTE: is this make sens ?
    elif action == 'migration':
        click.echo("Test user migration")

@test.command(name='share')
@click.argument('action', type=click.Choice(TEST_ACTIONS))
# @click.option('--user')
@click.pass_context
def testShare(ctx, action):
    test_share = {"name" : "smbShareExample",
                  "enbale" : True,
                  "sharedfolderref" : "", # NOTE: get sharedfolder reference
                  "comment" : "",
                  "guest" : "no",
                  "readonly" : False,
                  "browsable" : True,
                  "timemachine" : False,
                  "transportencryption" : True,
                  "incheritacls" : False,
                  "incheritpermissions" : False,
                  "recyclebin": False,
                  "recyclemaxsize": 0,
                  "recyclemaxage": 0,
                  "hidedotfiles": True,
                  "easupport": False,
                  "extraoptions": "",
                  "storedosattributes": False,
                  "hostsallow": "",
                  "hostsdeny": "",
                  "audit": False,
                  }
    
    if action == 'creation':
        rlog.info("Creating ")
    elif action == 'deletion':
        omvapi.deleteOmvUser(test_share)
        rlog.info("Test deletion of user")
    elif action == 'permission':
        # NOTE: is this make sens here
        rlog.info("Test user permissions")
    elif action == 'sync':
        omvapi.getOmvUsers(test_share)
        rlog.info("Test user sync")

        # NOTE: is this make sens ?
    elif action == 'migration':
        click.echo("Test user migration")

@test.command(name='datacopy')
@click.argument('src', nargs=1, type=click.Path(exists=True, file_okay=False))
@click.argument('dst', nargs=1, type=click.Path(exists=True, file_okay=False))
@click.option('--share-name', '-sn', help='Used share name')
@click.pass_context
def testDataCopy(ctx, src, dst, share_name):
    srcPathStr = ""

    if not share_name:
        share_name = click.prompt('Please enter the share', type=str)
        rlog.info(f'Using share name {share_name}')

        omvapi.getSharedFolders(ctx, False)
        omvapi.printSharedFolders(omvapi.getSharedFolders(ctx, False), False)
    else:
        rlog.info(f'Using share name:{share_name}')

    if not str(src).endswith("/"):
        srcPathStr = src + "/"

    if not str(dst).endswith("/"):
        dstPathStr = dst + "/"

    if ctx.obj['DEBUG']:
        rlog.debug(f'Source rath:{srcPathStr}{share_name}/')
        rlog.debug(f'Destination:{dstPathStr}{share_name}/')

    copyShareData(Path(f'{srcPathStr}{share_name}/'), Path(f'{dstPathStr}{share_name}/'), TRUE)

@test.command(name='all')
@click.argument('action', type=click.Choice(TEST_ACTIONS))
# @click.option('--user')
@click.pass_context
def testShare(ctx, action):
    click.echo("share")
    if action == 'creation':
        rlog.info("Creating test user")
        omvapi.createOmvUser(test_share)
    elif action == 'deletion':
        omvapi.deleteOmvUser(test_share)
        rlog.info("Test deletion of user")
    elif action == 'permission':
        # NOTE: is this make sens here
        rlog.info("Test user permissions")
    elif action == 'sync':
        omvapi.getOmvUsers(test_share)
        rlog.info("Test user sync")

        # NOTE: is this make sens ?
    elif action == 'migration':
        click.echo("Test user migration")


if __name__ == '__main__':
    cli()

