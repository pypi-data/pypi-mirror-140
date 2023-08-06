from gorp.readfiles import warn_first_import_error
try:
    from gorp.textcache import *
    ok_to_test = True
except ImportError: # sortedcollections is a dependency of TextCache
    warn_first_import_error("sortedcollections")
    ok_to_test = False
import string


def make_bigcache():
    if not ok_to_test:
        return
    tc = TextCache()
    for ii,letter in enumerate(string.ascii_lowercase):
        for jj,other_letter in enumerate(string.ascii_uppercase):
            tc[letter+other_letter] = (letter+other_letter)*(jj+1)*(ii+1)*100
    tc['cS'] = 'a'*7_000_000
    tc['aC'] = 'b'*9_999_000
    return tc


def main():
    '''Creates a TextCache, then adds 676 of increasingly large "strings".
Also adds two very large "files" (millions-long strings of repeated ASCII letters)
    to the TextCache to test its ability to make room for new files in an
    appropriate way.
Returns the TextCache.'''
    # the dirname containing os.__file__ is always Lib.
    if not ok_to_test:
        return
    tc = make_bigcache()
    assert tc.totsize < 25_000_000, \
        f"TextCache tc has size {tc.totsize}; should be <= 25,000,000"
    assert set(tc.files) & {'zA', 'zB', 'zC', 'zZ', 'zY', 'zX'}, \
        "TextCache should not have evicted 'zZ'-'zX' or 'zA'-'zC' because they were always either among the 3 most recent or not the fourth largest."
    assert 'cS' not in tc, \
        "'cS' should not be in tc because it was initially replaced by a big file and that big file had to be removed to make room for 'aC.py'"
    assert tuple(tc.files.keys())[:5] == ('aA', 'aB', 'aD', 'aE', 'aF'),\
        "The first files added are not ordered correctly."
    assert tc.largest_files(4) == [('aC', 19998000),
                                   ('zZ', 270400),
                                   ('zY', 260000),
                                   ('zX', 249600)], \
        "The four largest files are not correct."
    assert tc.most_recent(7) == {'aC': 19998000,
                                 'zZ': 270400,
                                 'zY': 260000,
                                 'zX': 249600,
                                 'zC': 31200,
                                 'zB': 20800,
                                 'zA': 10400}, \
        "The six most recent files are not correct."
    return tc
    
if __name__ == '__main__':
    tc = main()