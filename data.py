import shutil
# import subprocess
import subprocess
import rich.progress

def copydata(src, dst) -> int:
    try:
        output = run("exit 1", shell=True, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(e.returncode)
        print("dupad")
        print(e.output)
    print("copy data")
    print(output)

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
def main():
    testpath = "/home/sborawski/"
    if not testpath:
        print("Please give path to copy of openfiler system")
        exit(1)
    glob.glob(testpath + "*.xml")
    printusers("jkada")

copydata("/tmp/1", "/tmp/2")
