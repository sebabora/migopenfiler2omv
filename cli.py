# from os.path import exists, isfile
from pathlib import Path
from os.path import exists
import click
import users
from omvapi import *
import logging
import sys

@click.group()
@click.option('--debug/--no-debug', default=True)
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
    if usage:
        click.echo('Print standard usage of the application')
    ctx.obj['DEBUG'] = debug
    ctx.obj['USAGE'] = usage

    # users.parseLDIFile(ldifPath)
    # if len(users.ofUsersList) > 0:
    #     click.echo(f'Parsed %{len(users.ofUsersList)} users')
    # if len(users.ofGroupsList) > 0:

    #     click.echo(f'Parsed %{len(users.ofGroupsList)} groups')

@cli.command()
@click.option('--help/-h')
@click.pass_context
def help(ctx, help):
    click.echo("This script should help you migrate old openmediavault to new system OpenMediaVault")
    pass

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
    pass

# NOTE: migration files ? or just run it     
# @cli.command()
# @click.argument('ldifPath', required=True, type=click.Path()) 
# @click.option('--users-white-list', '-uwl', 'usersWhiteList', type=click.Path(), help='list of users ')
# @click.option('--users-black-list', '-ubl', 'usersBlackList', type=click.Path(), help='list of user excluded from migration')
# @click.option('--users-output-file', '-uo', 'usersOutputFile', type=click.Path(), help='Parsed user output file')
# @click.option('--dry-run-users', '-dru', 'dryRunUsers', is_flag=True, help='prints just the users info from ldif file')
# @click.pass_context
# def migratex(ctx, ldifPath,
#             usersOutputFile,
#             usersWhiteList,
#             usersBlackList,
#             dryRunUsers):
#     click.echo("migrate")
#     click.echo(click.format_filename(ldifPath))
#
# -------------------------------------------------------------------------------
#
# NOTE: migration second aprouch
# MIG_SUBJECT = ['users', 'groups', 'sharedFolders', 'shares']

@cli.group(name='migrate')
@click.pass_context
def migrate(ctx):
    # click.clear()
    click.echo("Starting migration... ")
    pass

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
    userMigrationFileName = "usersmigration.csv" 

    users.parseLDIFile(ldifdbpath)

    # read black list or white list users list from file
    if whiteList:
        users.importBlacklistedUsers(whiteList)
    if blackList:
        users.importBlacklistedUsers(blackList)
    if secretlistfile:
        users.importPasswordList(secretlistfile)

    users.cleanofUsersList(False)

    if not usrmigfile:
        usrmigfile = userMigrationPath.join(userMigrationFileName)
    # migration temporary files
    click.echo(type(usrmigfile))

    if usrmigfile.exists() & usrmigfile.is_file():
        click.echo("file exists")
        click.prompt("User migration file exists! Overwrite it?",
                     default="y",
                     confirmation_prompt=False,
                     click.Choice(['yes','y','no','n']),
                     click.show_choices=True) 

    users.cleanofUsersList(True)
    
    if ctx["DEBUG"]:
        users.printAllUsers()
    
    users.exportUsers(usrmigfile)
    # TODO: create users from list

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
        overwritemigfile = click.prompt("Do you whant to overwirte group migration file?",
                                        default="no",
                                        confirmation_prompt=False,
                                        click.Choice(['yes', 'y', 'no', 'n']),
                                        show_choices=True)
        overwritemigfile.lower()
        if overwritemigfile == 'yes' or overwritemigfile == 'y':
            users.exportGroups(grmigfile)

    if blackList:
        users.importBlacklistedGroups(blackList)
        #clean groups that aren't blacklisted
    else:
        #print list of users
        cleanmanually = click.prompt("Do you whant to clean group list manualy",
                                     default="no",
                                     confirmation_prompt=False,
                                     click.Choice(['yes','y','no','n']),
                                     show_choices=True)
        if cleanmanually == 'yes' or 'y':
            users.cleanofGroupsList(True)
        else:
            users.cleanofGroupsList(False)

    if grpmigfile.exists()
    if ctx["DEBUG"]:

@migrate.command(name='sharedfolders')
@click.argument('sourceDir', type=click.Path(exists=True)) 
@click.option('--black-list', '-sfbl', 'blackList', 
              type=click.Path(exists=True), help='cvs format black list of sharedfolders')
@click.pass_context
def migrateSharedFolders(ctx, sourceDir, blackList):

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
    click.echo("migrating sharedfolders")
    # NOTE: read users:q from migration file or from ldif file
    
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
    # TODO: 
    # exexucte rsync for every single catalog
    #
    if dry_run:
        click.echo("DRY RUN")
    else:
        click.echo("WARNING")
    pass
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
        getOmvUsers(ctx)
    if omvobj == "systemusers":
        getOmvSystemUsers(ctx)
    if omvobj == "groups":
        getOmvGroups(ctx, False)
    if omvobj == "systemgroups":
        getOmvGroups(ctx, True)
    if omvobj == "sharedfolders":
        getSharedFolders(ctx, print_uuid)
    if omvobj == "shares":
        getShares(ctx, print_uuid)
    if omvobj == "disks":
        getListOfFilesystems(ctx)
    # print('type: ', type(ctx))

# @cli.command(name="test")
# @click.argument('creation', type=click.Choice(['sharedfolder','share','users','groups']) 
TEST_SUBJECT=['sharedFolder', 'share', 'user', 'group']
TEST_ACTIONS=['creation', 'deletion', 'permission', 'sync', 'migration']


@cli.group()
@click.pass_context
def test(ctx):
    click.echo("WHY THIS Has to go")
    pass
    
@test.command(name='user')
@click.argument('action', type=click.Choice(TEST_ACTIONS))
@click.option('--user')
@click.pass_context
def testUser(ctx, action):
    click.echo("user")
    pass

@test.command(name='group')
@click.argument('subject', type=click.Choice(TEST_ACTIONS))
@click.pass_context
def testGroup(ctx, subject):
    click.echo("group")
    pass

@test.command(name='sharedFolder')
@click.argument('action', type=click.Choice(TEST_ACTIONS))
# @click.option('--user')
@click.pass_context
def testSharedFolder(ctx, action):
    click.echo("sharedfolder")
    pass

@test.command(name='share')
@click.argument('action', type=click.Choice(TEST_ACTIONS))
# @click.option('--user')
@click.pass_context
def testShare(ctx, action):
    click.echo("share")
    pass

@test.command(name='all')
@click.argument('action', type=click.Choice(TEST_ACTIONS))
# @click.option('--user')
@click.pass_context
def testShare(ctx, action):
    click.echo("share")
    pass

 # @cli.command(name='test')
# @click.option('--creation', type=click.Choice(TEST_SUBJECT))
# @click.option('--deletion', type=click.Choice(TEST_SUBJECT))
# @click.option('--permissions', is_flag=True)
# @click.option('--migration', is_flag=True)
# @click.option('--sync', is_flag=True)
# @click.argument('testarg')
# @click.option('--all', is_flag=True)
# @click.pass_context
# def test(ctx, creation, deletion, permissions, migration, sync, testarg, all):
#     click.echo("Starting testing....")
#     logHandler = logging.StreamHandler(sys.stdout)
#     log = logging.getLogger("my-loger")
#     log.addHandler(logHandler)
#     log.error("hello world")
#     log.info("hello world info")
#
#     test_user = {"name" :"rpcUsr",
#                  "groups" : ["rpcUsrGr","users"],
#                  "password" : "dupamaryski",
#                  "email" : "",
#                  "disallowusermod" : False, 
#                  "sshpubkeys" : []
#                  }
#
#     test_group = {"name" : "rpcGroup",
#                   # NOTE: czy napewno podaje dane typu uid ?
#                   "gid" : "1045",
#                   "members" : ["rpcUsr"]
#                   }
#
#     test_sharedFolder = {"name" : "rpcSharedFolder",
#                          "mntent" : { # NOTE: get disk reference first
#                             "devicefile" : "/dev/mapper/omv--vg2-data",
#                             "fsname" : "/dev/disk/by-uuid/8d3565a5-652a-4bec-ad04-3f5bcca74a67",
#                             "dir" : "/srv/dev-disk-by-uuid-8d3565a5-652a-4bec-ad04-3f5bcca74a67",
#                             "type" : "ext4",
#                             "postixacl" : True,
#                             },
#                          "reldirpath" : "rpcSharedFolder/",
#                          "mntentref" : "", # uuid somekind ?
#                          "device" : "/dev/disk/by-id/dm-name-omv--vg2-data", 
#                          "mode" : "755",
#                          "tags" : "", # could be empty or none ?
#                         }
#
#     test_share = {"name" : "smbShareExample",
#                   "enbale" : True,
#                   "sharedfolderref" : "", # NOTE: get sharedfolder reference
#                   "comment" : "",
#                   "guest" : "no",
#                   "readonly" : False,
#                   "browsable" : True,
#                   "timemachine" : False,
#                   "transportencryption" : True,
#                   "incheritacls" : False,
#                   "incheritpermissions" : False,
#                   "recyclebin": False,
#                   "recyclemaxsize": 0,
#                   "recyclemaxage": 0,
#                   "hidedotfiles": True,
#                   "easupport": False,
#                   "extraoptions": "",
#                   "storedosattributes": False,
#                   "hostsallow": "",
#                   "hostsdeny": "",
#                   "audit": False,
#                   }
#
#     if not creation == '':
#         if creation == 'sharedFolder':
#             createSharedFolder(test_sharedFolder, True)
#         if creation == 'share':
#             createShare(test_share, True)
#         if creation == 'user':
#             createOmvUser(test_user, True)
#         if creation == 'group':
#             createOmvGroup(test_group, True)
#     if not deletion == '':
#         if deletion == 'sharedFolder':
#            deleteSharedFolder(test_sharedFolder, True)
#         if deletion == 'share':
#             deleteShare(test_share, True)
#         if deletion == 'user':
#             deleteUser(test_user, True)
#         if deletion == 'group':
#             deleteGroup(test_group)
#     if permissions:
#         getSharedFolderPermissions(test_sharedFolder)
#     if all:
#         createOmvGroup(test_group, True)
#         createOmvUser(test_user, True)
#         createSharedFolder(test_sharedFolder)
#         createShare(test_share)
#         getOmvUsers(ctx)
#         getOmvGroups(ctx)
#         getSharedFolders(ctx)
#         getShares(ctx)
#         deleteShare(ctx)
#         deleteSharedFolder(ctx)
#         deleteOmvGroup(test_group)
#         deleteOmvUser(test_group)

if __name__ == '__main__':
    cli()

# @click.group(name="migrate")
# @click.option('--help/--no-help', default=False)
# def cli(help):
#     click.echo(f"Debug mode is {'on' if help else 'off'}")
#
# @cli.command()  # @cli, not @click!
# def sync():
#     click.echo('Syncing')
#
# @click.group()
# @click.option('--migrate', '-mg', type(['users', 'shares', 'data'], case_sensitiv=False))
# @click.command()
# @click.argument('srcdata')
# @click.argument('dstdata')
# @click.option('--dry-run', default=True)
# def migratedata(srcdata, dstdata, dry_run):
#     click.echo(f"Migrating data from {'srcdata'} to {'dstdata'}")
#     if dry_run:
#         click.echo(f"This is dry run")
#     else:
#         click.echo(f"This ISN'T DRY RUN")
