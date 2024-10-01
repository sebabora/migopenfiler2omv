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
    click.echo('Debug mode is %s' % ('ON' if debug else 'off'))
    ctx.ensure_object(dict)
    if usage:
        click.echo('Print standard usage of the application')
    ctx.obj['DEBUG'] = debug
    ctx.obj['USAGE'] = usage

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
    
@cli.command()
@click.argument('ldifPath', required=True, type=click.Path()) 
@click.option('--users-white-list', '-uwl', 'usersWhiteList', type=click.Path(), help='list of users ')
@click.option('--users-black-list', '-ubl', 'usersBlackList', type=click.Path(), help='list of user excluded from migration')
@click.option('--users-output-file', '-uo', 'usersOutputFile', type=click.Path(), help='Parsed user output file')
@click.option('--dry-run-users', '-dru', 'dryRunUsers', is_flag=True, help='prints just the users info from ldif file')
@click.pass_context
def migrate(ctx, ldifPath,
            usersOutputFile,
            usersWhiteList,
            usersBlackList,
            dryRunUsers):
    click.echo("migrate")
    click.echo(click.format_filename(ldifPath))

    # users.parseLDIFile(ldifPath)
    # if len(users.ofUsersList) > 0:
    #     click.echo(f'Parsed %{len(users.ofUsersList)} users')
    # if len(users.ofGroupsList) > 0:
    #     click.echo(f'Parsed %{len(users.ofGroupsList)} groups')

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

@cli.command(name="test")
@click.pass_context
def tests(ctx):
    logHandler = logging.StreamHandler(sys.stdout)
    log = logging.getLogger("my-loger")
    log.addHandler(logHandler)
    log.error("hello world")
    log.info("hello world info")

    test_user = {"name" :"rpcUsr",
                 "groups" : ["rpcUsrGr","users"],
                 "password" : "dupamaryski",
                 "email" : "", 
                 "disallowusermod" : False, 
                 "sshpubkeys" : []}
    createOmvUser(test_user, True)
    test_group = {"name" : "rpcGroup",
                  "gid" : "1045",
                  "members" : ["rpcUsr"]}
    createOmvGroup(test_group, True)
    pass

# TODO: odczytaj listę użytkowników
# TODO: konwertuj listę użytkowników
# TODO: utwórz użytkowników
# def migrateUsers(wl):
#     print(wl)
#     click.echo("Migrateing users")
# @cli.command()
# @click.option

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
