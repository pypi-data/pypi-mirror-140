from gorp.readfiles import warn_first_import_error
from gorp.textcache import TextCache
from gorp.utils import gorpdir
from gorp.test.test_ku_options import setup_tempdir
import json
import os
import time

testdir = os.path.join(gorpdir, 'test')
tempdir = os.path.join(testdir, 'temp')

def populate_cache(tc):
    ogdir = os.getcwd()
    os.chdir(tempdir)
    try:
        for fname in os.listdir(tempdir):
            fname = os.path.join(tempdir, fname)
            if os.path.isfile(fname):
                with open(fname) as f:
                    tc[fname] = f.read().split('\n')
    finally:
        os.chdir(ogdir)


def main():
    '''Creates a TextCache containing the '''
    # the dirname containing os.__file__ is always Lib.
    ogdir = os.getcwd()
    os.chdir(testdir)
    try:
        db_fname = os.path.join(testdir, 'temp_textcache.sqlite')
        tc = TextCache(db_fname)
        # check that database was created
        assert os.path.exists('temp_textcache.sqlite'), \
            f"Calling TextCache('temp_textcache.sqlite') should have created temp_textcache.sqlite"
        
        # make temp files, populate cache, check that rows were added
        setup_tempdir()
        populate_cache(tc)
        files = tc.files
        assert len(files) == 9, f"TextCache from tempdir should have 9 keys, got {len(files)}"
        
        # test that row was retrieved correctly
        guten_fname = os.path.join(tempdir, 'GUT)enTHARST.js')
        guten = tc.get_all_data(guten_fname)
        assert len(guten) == 1 and len(guten[0]) == 5, f"tc.get_all_data({guten_fname}) has wrong # of elements"
        
        # test that text is fine
        fname, text, modtime, insert_time, size = guten[0]
        true_guten_text = open(guten_fname).read().split('\n')
        assert text == json.dumps(true_guten_text), f"Expected tc's text to be {repr(true_guten_text)}, got {repr(text)}"
        
        # test that insertion when no record exists does not do anything
        tc[guten_fname] = true_guten_text
        guten2 = tc.get_all_data(guten_fname)
        assert guten2 == guten, f"Attempted insertion of unmodified file perturbed the database to make row {guten2}, but it should be unmodified ({guten})"
        
        # test that tc overwrites old record when a file already in the
        # database is changed.
        new_guten_text = ["new guten text", "blah"]
        with open(guten_fname, 'w') as f:
            f.write('\n'.join(new_guten_text))
        tc[guten_fname] = new_guten_text
        guten3 = tc.get_all_data(guten_fname)
        assert len(guten3) == 1, "Insertion of (filename, text) pair where filename already in database should replace the old record, not add a new one."
        assert guten3 != guten, f"Attempted insertion of modified file should perturb the database, but it didn't"
        
        # test that deletion works
        tc.pop(guten_fname)
        assert guten_fname not in tc, f"tc.pop should remove {guten_fname}"
        assert tc.get(guten_fname, 3) == 3, "tc.get should return default if key doesn't exist"
        
        # re-add file, make sure it's added correctly
        time.sleep(1)
        with open(guten_fname, 'w') as f:
            f.write('\n'.join(new_guten_text))
        tc[guten_fname] = new_guten_text
        assert guten_fname in tc, "File deleted should be re-added"
        
        # test smallest
        smallest = tc.smallest_files(9)
        assert len(smallest) == 9, f"Wanted smallest to have 9 elements, has {len(smallest)}"
        assert guten_fname == smallest[0][0], f"Smallest file should be {guten_fname}, but instead it's {smallest[0][0]}"
        
        # test largest
        largest = tc.largest_files(9)
        assert len(largest) == 9, f"Wanted smallest to have 9 elements, has {len(largest)}"
        assert guten_fname == largest[8][0], f"Least large file should be {guten_fname}, but instead it's {largest[8][0]}"
        
        # test newest
        newest = tc.newest_files()
        assert len(newest) == 1, f"Newest should have 1 element has {len(newest)}"
        assert guten_fname == newest[0][0], f"Newest file should be {guten_fname}, but instead it's {newest[0][0]}"
        # test largest
        oldest = tc.oldest_files(9)
        assert guten_fname == oldest[8][0], f"Least old file should be {guten_fname}, but instead it's {oldest[8][0]}"
    except Exception as ex:
        raise ex
    finally:
        os.unlink('temp_textcache.sqlite')
        os.chdir(ogdir)

    
if __name__ == '__main__':
    main()