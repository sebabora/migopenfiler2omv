import click
import migrateusers

# TODO: odczytaj listę użytkowników
@click.command()
@click.option('')
@click.option('openfilersrc', help='Path to root directory of openfiler system')
@click.option('omvdst', help='Destination file system by default it assumes that you start the scrip on it')
@click.option('--white-list', '-wl', multiple=True, help='list of users ')
@click.option('--user-black-list', '-ubl', multiple=True, help='list of user excluded from migration')
@click.option('--shares-black-list', 'sbl', multiple=True, help='list of shares excluded form migration')
@click.option('--users-output-file', help='outputs users into do /etc/passwd style file')
@click.option('--dry-run-copy-data', help='don\'t copy anything just print the data')
@click.option('--dry-run-shares', help='print shares info from source system')
@click.option('--dry-run-users', help='print just the users info from ldif file')
@click.option('--dry-run', '--dry-run-all', multiple=True, help='dont make changes just print everything on the screen')

# TODO: konwertuj listę użytkowników
# TODO: utwórz użytkowników
# TODO: odczytaj udziały
# TODO: utwórz udziały i przypisz prawa 
# TODO: kopiuj pliki (dry)
# TODO: sprawdz i popraw uprawnienia
# TODO: stworz cli
# TODO: synchrnonizacja plików opcja
def cli():
    print('Koniec !')
if __name__ == "__cli__":
    cli()
# PERF: testowa lista 
# TODO:
# PERF:
# HACK:
# NOTE:
# FIX:
# WARNING:

