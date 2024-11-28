import shutil
# import subprocess
import subprocess
import rich.progress
import os
from pathlib import Path
from richlogging import logger as rlog 

def copyShareData(src : Path, dst : Path, dry_run = True):
    
    # rlog = rich.liogging.getLogger(__name__)
    # richlogging.logger.info('testlog')
    
    rlog.info(f'Copying data from {str(src)} to {str(dst)}' )

    rsyncPath = "/usr/bin/rsync"
    if dry_run:
        rsyncOptions =  "-avz --no-perms --no-owner --no-group --delete --dry-run"
    else:
        rsyncOptions =  "-avz --no-perms --no-owner --no-group --delete"

    rlog.debug(f'Rsync options used: {rsyncOptions}')
        
    # jesli src konczy sie do 
    if src.exists() and src.is_dir():
        rlog.debug(f'Source directory {str(src)} exists')
    else:
        rlog.error(f'Source directory {str(src)} does not exists')
        os._exit(os.EX_IOERR)


    if dst.exists() and dst.is_dir():
        print("Using destination path:", str(src))
        rlog.debug(f'Destination directory {str(dst)} exists')
    else:
        rlog.error(f'Destination directory {str(dst)} does not exists')
        os._exit(os.EX_IOERR)

    srcPathStr = str(src)
    dstPathStr = str(dst)

    if not str(srcPathStr).endswith("/"):
        srcPathStr = srcPathStr + "/"

    if not str(dstPathStr).endswith("/"):
        dstPathStr = dstPathStr + "/"

    if os.getuid() != 0:
        rlog.critical(f'Elevate privileges !')
        # exit("You need to have root privileges to run rsync script")
    else:
        try:
            proc = subprocess.check_output("{0} {1} {2} {3}".format(rsyncPath,
                                                                    rsyncOptions, 
                                                                    srcPathStr,
                                                                    dstPathStr),
                                                                    stderr=subprocess.STDOUT, 
                                                                    shell=True)
            return proc
        except subprocess.CalledProcessError as e:
            rlog.error(f'running rsync {e}')
            proc = e.output.decode()
            return proc

if __name__ == "__main__":
        copyShareData(Path("/tmp/1"), Path("/tmp/2"))
