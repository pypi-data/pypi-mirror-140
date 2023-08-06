import os

def make_relpaths(paths):
    '''Find the longest path shared by all of paths (os.path.commonpath),
    and cut off all the paths at the point. Also return the common path.'''
    commondir = os.path.commonpath(paths)
    if not commondir.endswith(os.path.sep):
        commondir += os.path.sep
    return [p[len(commondir):] for p in paths], commondir