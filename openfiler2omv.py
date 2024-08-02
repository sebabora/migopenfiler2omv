### First test script to test various things :)
import os
import sys

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
def list_xml_directory_files(path2openfilersys):
    for root, dirs, files in os.walk(path2openfilersys):
        if layer == 1:
            print(files)
def main(argv):
    testpath = "/home/sborawski/"
    if not testpath:
        print("Please give path to copy of openfiler system")
        exit(1)
    list_files(testpath)
    glob.glob(testpath + "*.xml")

    





if __name__ == "__main__":
    main()
