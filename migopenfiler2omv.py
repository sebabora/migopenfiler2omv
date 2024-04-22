import os

def list_files(startpath):
    if not startpath:
        startpath = "/home/sebastian/"
    else:
        print("Start path ", startpath)

    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        ident = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))

def main():


    





if __name__ == "__main__":
    main()
