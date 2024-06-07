"""Override methods to log infos."""

from shutil import move as mv
import src.constants as cst
from os import mkdir as m__, rmdir as rm__, remove as remove__

def move(src: str, dest: str):
    """Add logging to move function."""
    mv(src, dest)
    
    cst.review_log.info(f"File moved '{src.replace(cst.project + '/', '')}'\t->\t'{dest.replace(cst.project + '/', '')}'")
    
def mkdir(dest: str):
    """Add logging to mkdir function."""
    m__(dest)
    
    cst.review_log.info(f"Folder '{dest.replace(cst.project + '/', '')}' created. This folder will be deleted if it stays empty.")
    
def rmdir(dir: str):
    """Adding logging to rmdir function."""
    rm__(dir)
    
    cst.review_log.info(f"Folder '{dir}' deleted.")
    
def remove(file: str):
    """Add logging ro remove function."""
    remove__(file)
    
    cst.review_log.info(f"File '{file}' deleted.")