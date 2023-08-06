import os
import shutil
import logging

logger = logging.getLogger("ssh_client")


def rm(path):
    """ Remove a file or directory """
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)
    logger.info("Remove: %s", path)
