import click
import os
# import users
# import omvapi
# import omvusers
# import shares
# import data
              
# @click.group()
# @click.option('--debug/--no-debug', default=False)
# def cli(debug):
#     click.echo(f"Debug mode is {'on' if debug else 'off'}")
# @cli.command()
# def sync():
#     click.echo('Syncing')
# CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
# @click.group(context_settings=CONTEXT_SETTINGS)
# def cli():
#     click.echo("help")
#     pass
#
# # @cli.argument(hidden=True)
# @click.pass_context
# def help(ctx):
#     click.echo(ctx.parent.get_help())
#     pass

class Repo(object):
    def __init__(self, home=None, debug=False):
        self.home = os.path.abspath(home or '.')
        self.debug = debug


@click.group()
@click.option('--repo-home', envvar='REPO_HOME', default='.repo')
@click.option('--debug/--no-debug', default=False,
              envvar='REPO_DEBUG')
@click.pass_context
def cli(ctx, repo_home, debug):
    ctx.obj = Repo(repo_home, debug)

@cli.command()
@click.argument('src', required=True)
@click.argument('dst', required=True)
@click.pass_obj
def migrate(repo, src, dst):
    pass

@cli.command()
@click.option('--ldif-file')
@click.option('--blacklist')
@click.pass_obj
def migrateusers(ldif_file, blacklist):
    click.echo(ldif_file, blacklist)
    pass

    
 # @cli.command()
# @click.argument('srcdata')
# @click.argument('dstdata')
# @click.option('--dry-run', default=True)
# def migratedata(srcdata, dstdata, dry_run):
#     click.echo(f"Migrating data from {'srcdata'} to {'dstdata'}")
#     if dry_run:
#         click.echo(f"This is dry run")
#     else:
#         click.echo(f"This ISN'T DRY RUN")
# @cli.command()

# @click.echo('Migrating users')
# @click.echo('Migrating shares')
# @click.echo('Migrating data')
# @click.echo('Syncing')

# @click.group()
# @click.option('--debug/--no-debug', default=False)
# def cli(debug):
#     click.echo(f"Debug mode is {'on' if debug else 'off'}")
#
# @cli.command()
# def sync():
#     clic.echo('Syncing')
# def cli_help():

#     """ This script is build to convert openfiler fileserver to openmediavuault
#     
#     Requirements:
#     - exported ldap database to ldif file
#     - make list of black listed or whitelisted users in csv file format
#     - mounted old data storage on new openmediavault system
#     - run script with appropriate arguments and parameters
#
#     """

# @click.command()
# @click.argument('', type=click.Path(exists=True))
# @click.option('--white-list', '-wl', multiple=True, help='list of users ')
# @click.option('--user-black-list', '-ubl', multiple=True, help='list of user excluded from migration')
# @click.option('--users-output-file', help='outputs users into do /etc/passwd style file')
# @click.option('--dry-run-users', help='prints just the users info from ldif file')
# # TODO: odczytaj listę użytkowników
# # TODO: konwertuj listę użytkowników
# # TODO: utwórz użytkowników
# def migrateUsers(wl):
#     print(wl)
#     click.echo("Migrateing users")
# #
# #     
# @click.command()
# @click.option('--shares-black-list', 'sbl', multiple=True, help='list of shares excluded form migration')
# @click.option('--dry-run-shares', help='prints shares info from source system')
# # TODO: odczytaj udziały
# # TODO: utwórz udziały i przypisz prawa 
# def migrateShares():
#     click.echo("Migrating shares")
# #
# #
# @click.command()
# @click.argument('srcdatapath', narg=1, help='Path to root directory of openfiler system')
# @click.argument('dstdatapath', narg=1, help='Destination file system by default it assumes that you start the scrip on it')
# @click.option('--dry-run-copy-data', help='don\'t copy anything just click.echo the data')
# # TODO: kopiuj pliki (dry)
# # TODO: sprawdz i popraw uprawnienia
# # TODO: synchrnonizacja plików opcja
# def migrateData(openfilesrc):
#     click.echo("Migrating data")
#
#
# @click.command()
# @click.option('--dry-run', '--dry-run-all', multiple=True, help='dont make changes just click.echo everything on the screen')
# def migrateAll():
#     click.echo("Migrate all")
# PERF: testowa lista 
# TODO:
# PERF:
# HACK:
# NOTE:
# FIX:
# WARNING:
# if __name__ == "__cli__":
#     cli()
