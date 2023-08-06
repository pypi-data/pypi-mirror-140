import os
from .utils import run_file_default_app
import shutil
from .gprint import gprint

def killGorp(files, 
             ask_permission = True, 
             allow_remove_trees = False):
    '''Utility for looking at a list of files (or dict with files as keys) and deciding
    which to permanently delete.
ask_permission: bool, default True. If True, there's an interactive prompt that checks 
    with the user to see if they're OK with deleting the files. Turn this off if you're
    very confident that you won't screw up and accidentally delete some good files.
allow_remove_trees: bool, default False. If True, this can be used to delete
    directories.'''
    if ask_permission:
        gprint(files)
        if not files:
            return
        while True:
            print("The files displayed above have been found, and are pending deletion.")
            decision = input("Enter 'y' or 'yes' to proceed, 'GOGO!' to delete ALL remaining files, or q/quit/stop to halt execution\n")
            if decision == 'GOGO!':
                decision2 = input("Are you REALLY sure you want to delete ALL remaining files? No second chances!\n('y' or 'yes' to proceed)\t")
                if decision2 in ['y', 'yes']:
                    ask_permission = False
            elif decision in ['stop', 'quit', 'q']:
                return
            elif decision in ['y', 'yes']:
                break
            else:
                print("The only valid choices are 'stop', 'quit', 'q', 'y', 'yes', and 'GOGO!'")
    if not len(files):
        return
    skip = False
    for ii, file in enumerate(files):
        if os.path.isdir(file) and not allow_remove_trees:
            continue # we want to only delete individual files, not whole dirs
        if ask_permission:
            skip = False
            while True:
                print(f"----------\n{file} is pending deletion.")
                decision = input("Enter 'y' or 'yes' to proceed, 'GOGO!' to delete ALL remaining files, 'skip'/'n'/'no' to skip this file and look at others, 'open' or 'run' to open the file and pause execution, 'rem' or 'remaining' to see remaining files, or q/quit/stop to halt execution\n")
                if decision == 'GOGO!':
                    print(f"Are you REALLY sure you want to delete ALL {len(files)-ii} remaining files:")
                    gprint(files[ii:])
                    decision2 = input("No second chances! ('y' or 'yes' to proceed)\t")
                    if decision2 in ['y', 'yes']:
                        ask_permission = False
                        break
                elif decision in ['stop', 'quit', 'q']:
                    return
                elif decision in ['y', 'yes']:
                    break # go to file deletion
                elif decision in ['skip', 'n', 'no']:
                    skip = True
                    break
                elif decision in ['rem', 'remaining']:
                    print(f"{len(files) - ii - 1} files remaining")
                    gprint(files[ii+1:])
                elif decision in ['open', 'run']:
                    run_file_default_app(file)
                else:
                    print("The only valid choices are 'stop', 'quit', 'q', 'y', 'yes', 'GOGO!', 'open', and 'run'.")
        if not skip:
            if not os.path.isdir(file):
                try:
                    os.unlink(file)
                except Exception as ex: # probably the file is open and thus locked
                    raise ex
                    pass
            else: # it's a directory, and allow_remove_trees is True
                try:
                    shutil.rmtree(file)
                except Exception as ex:
                    # this is probably because some file in the directory is currently
                    # open, and the directory is locked
                    raise ex
                    pass