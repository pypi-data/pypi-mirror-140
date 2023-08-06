import logging
import subprocess

logger = logging.getLogger('ssh_client')


def shell_exec(cmd, check=False, capture_output=True, ignore_exit=False):
    if capture_output:
        p = subprocess.run(cmd, shell=True, check=check, capture_output=capture_output)
    else:
        p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           shell=True, check=check, capture_output=capture_output)
    logger.info(f"[{p.args}] --> {p.returncode}")
    if p.stdout:
        logger.info(str(p.stdout, encoding='utf-8'))
    if p.stderr:
        logger.info(str(p.stderr, encoding='utf-8'))

    if not ignore_exit:
        assert p.returncode == 0
