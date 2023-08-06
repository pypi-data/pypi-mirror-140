#!/usr/bin/python3
# tested in python 3.6-3.9
import os
import shutil
from gorp.readfiles import *
from gorp.k_option_del_files import killGorp
from gorp.gprint import bad_json
try:
    import yaml
except:
    yaml = None

previous_allow_remove_trees = ALLOW_REMOVE_TREES
previous_prompt_k_option = PROMPT_K_OPTION
previous_prompt_u_option = PROMPT_U_OPTION
previous_u_option_overwrites = U_OPTION_OVERWRITES

newdirname = os.path.join(gorpdir, "test", "temp")

testfiles = [
    'Manowar - Warriors of the World United.txt',
    'The Rolling Stones [ Dance Part 2.py',
    'Tool ] Rosetta Stoned.log',
    'BLUTENTHARST.sql',
    'HUNDENtharst.cpp',
    'dud(ENTHARST.java',
    'GUT)enTHARST.js',
]

def setup_tempdir():
    if os.path.exists(newdirname):
        shutil.rmtree(newdirname)
    os.mkdir(newdirname)
    os.mkdir(os.path.join(newdirname, 'subdir'))
    shutil.copy(os.path.join(gorpdir, "testDir", "dict size vs memory allocated.png"),
                os.path.join(newdirname, 'subdir'))
    with open(os.path.join(newdirname, "subdir", "subdir_file.txt"), 'w') as f:
        f.write("this can be deleted with temp/subdir/ if ALLOW_REMOVE_TREES is true.")
    for ii, fname in enumerate(testfiles):
        with open(os.path.join(newdirname, fname), 'w') as f:
            f.write(f"this is only the {ii}^th test file\n{fname}")
    with open(os.path.join(newdirname, "RAMMSTEIN 1.json"), 'w') as f:
        json.dump(bad_json, f)
    try:
        with open(os.path.join(newdirname, "RAMMSTeIN 10.yaml"), 'w') as f:
            yaml.safe_dump(bad_json, f)
    except:
        pass

def test_killGorp():
    os.chdir(newdirname)
    try:
        session = GorpSession()
        listdirs = []
        listdirs.append(set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir')))
        session.receive_query("DEFAULTS.PROMPT_K_OPTION = False")
        session.receive_query("DEFAULTS.ALLOW_REMOVE_TREES = False")
        assert listdirs[0] == {'Manowar - Warriors of the World United.txt',
                               'The Rolling Stones [ Dance Part 2.py',
                               'Tool ] Rosetta Stoned.log',
                               'BLUTENTHARST.sql',
                               'HUNDENtharst.cpp',
                               'dud(ENTHARST.java',
                               'GUT)enTHARST.js',
                               "RAMMSTEIN 1.json",
                               "RAMMSTeIN 10.yaml",
                               "subdir",
                               os.path.join("subdir", "dict size vs memory allocated.png"),
                               os.path.join("subdir", "subdir_file.txt")}
        session.receive_query("-f -k 'l$' /.")
        # test ability to delete multiple files based on regex
        listdirs.append(set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir')))
        assert listdirs[-1] == listdirs[-2] - {'BLUTENTHARST.sql',"RAMMSTeIN 10.yaml"},\
            "test_killGorp failed on -f -k 'l$' /."
        
        session.receive_query("-a -k '' /subdir")
        # test ability to delete files in other directories
        listdirs.append(set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir')))
        assert not os.listdir('subdir'), \
            "test_killGorp failed on -a -k '' /subdir"
        
        session.receive_query("-f -k '' /HUNDENtharst.cpp")
        # test ability to delete when the initial resultset is a specific file
        listdirs.append(set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir')))
        assert listdirs[-1] == listdirs[-2] - {'HUNDENtharst.cpp'}, \
            "test_killGorp failed on -f -k '' /HUNDENtharst.cpp"
        
        session.receive_query("-f -k 'z{4}' /GUT)enTHARST.js")
        # test ability to not delete a specific file when the regex doesn't match
        listdirs.append(set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir')))
        assert listdirs[-1] == listdirs[-2], \
            "test_killGorp failed on -f -k 'z{4}' /GUT)enTHARST.js"
        
        shutil.copy(os.path.join(gorpdir, "testDir", 
                                 "dict size vs memory allocated.png"),
                    os.path.join(newdirname, 'subdir'))
        shutil.copy('dud(ENTHARST.java',
                    os.path.join(newdirname, 'subdir'))
        session.receive_query("-f -k -r 'alloc'")
        # test not deleting non-text files when the -f option is specified
        listdirs.append(set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir')))
        assert listdirs[-1] == listdirs[-2] | {os.path.join('subdir', "dict size vs memory allocated.png"), os.path.join('subdir', 'dud(ENTHARST.java')}, \
            "test_killGorp failed on -f -k -r 'alloc'"
        
        session.receive_query("-a -k -r 'alloc'")
        # test ability to delete files found by a recursive search
        listdirs.append(set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir')))
        assert set(os.listdir("subdir")) == {'dud(ENTHARST.java'}, \
            "test_killGorp failed on -a -k -r 'alloc'"
        
        session.receive_query("-j -k 'jub~~@BOZZRERE~~@..~~@y' /.")
        # test ability to not kill based on a json search that matches nothing
        listdirs.append(set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir')))
        assert listdirs[-1] == listdirs[-2], \
            "test_killGorp failed on -j -k 'jub~~@BOZZRERE~~@..~~@y' /."
        
        session.receive_query("-j -k 'jub~~@yu~~@..~~@y' /.")
        # test ability to kill based on a json search
        listdirs.append(set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir')))
        assert listdirs[-1] == listdirs[-2] - {"RAMMSTEIN 1.json"}, \
                "test_killGorp failed on -j -k 'jub~~@BOZZRERE~~@..~~@y' /."
                                     
        session.receive_query("-i -k 'rewrerer' /.")
        # test ability to not kill if text search turns up nothing
        listdirs.append(set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir')))
        assert listdirs[-1] == listdirs[-2], \
            "test_killGorp failed on -i 'rewrerer' /."
            
        session.receive_query("-i -r -k '^DUD' /.")
        # test ability to recursively kill based on text search
        listdirs.append(set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir')))
        assert listdirs[-1] == listdirs[-2] - {os.path.join('subdir', 'dud(ENTHARST.java'), 'dud(ENTHARST.java'}, \
            "test_killGorp failed on -i -r '^DUD' /."
            
        session.receive_query("-k -d 'sub' /.")
        # make sure it doesn't kill a directory when ALLOW_REMOVE_TREES is False
        listdirs.append(set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir')))
        assert listdirs[-1] == listdirs[-2], \
            "test_killGorp failed on -k -d 'sub' /."
            
        session.receive_query("DEFAULTS.ALLOW_REMOVE_TREES = True")
        session.receive_query("-k -d 'sub' /.")
        # make sure it does kill a directory when ALLOW_REMOVE_TREES is True
        listdirs.append(set(os.listdir()))
        assert 'subdir' not in listdirs[-1], \
            "test_killGorp failed on -k -d 'sub' /."
            
        session.receive_query("-i -r '^GUT' /. -}} -k '\d'")
        # test ability to kill as the n^th subquery in a query chain
        listdirs.append(set(os.listdir()))
        assert (listdirs[-1] == listdirs[-2] - {"GUT)enTHARST.js"}), \
            "test_killGorp failed on -i -r '^GUT' /. -}} -k '\d'"
    finally:
        os.chdir(gorpdir)
        session.receive_query(f"DEFAULTS.ALLOW_REMOVE_TREES = {previous_allow_remove_trees}")
        session.receive_query(f"DEFAULTS.PROMPT_K_OPTION = {previous_prompt_k_option}")
        session.close()


def get_text_all_files(dir_ = newdirname):
    for root, dirs, files in os.walk(dir_):
        for fname in files:
            if isTextType(fname):
                fname = os.path.join(dir_, root, fname)
                with open(fname) as f:
                    yield fname, f.read()


def test_update():
    os.chdir(newdirname)
    og_text_all_files = Orddict(get_text_all_files())
    try:
        listdirs = []
        listdirs.append(set(os.listdir()))
        session = GorpSession()
        session.receive_query("DEFAULTS.PROMPT_U_OPTION = False")
        session.receive_query("DEFAULTS.U_OPTION_OVERWRITES = True")
        #~~~~~~~~~~~~~~~~~~~~~
        # TEST 1: test updating text, no file filters in path, with recursive search
        #~~~~~~~~~~~~~~~~~~~~~
        session.receive_query("-i -r '^GUT' /. -}} '\d' -}} -u 'x sub `file//FILLE`'")
        new_text_all_files = Orddict(get_text_all_files())
        assert len(new_text_all_files) == len(og_text_all_files), \
            f"Number of files changed from {len(og_text_all_files)} to {len(new_text_all_files)} when U_OPTION_OVERWRITES was True"
        fnames_changed = {os.path.join(newdirname, 'GUT)enTHARST.js')}
        for (og_fname, og_text), (new_fname, new_text) in zip(og_text_all_files.items(),
                                                            new_text_all_files.items()):
            assert og_fname == new_fname, \
                f"Filename was changed from {og_fname} to {new_fname} when -u option should not have been changing filenames"
            if og_fname in fnames_changed:
                continue
            assert og_text == new_text, f"Text of {og_fname} was changed from {og_text} to {new_text} when it should not have been changed by -i -r '^GUT' /. -}} '\d' -}} -u 'x sub `file//FILLE`'"
        for fname in fnames_changed:
            correct_new_text = re.sub('file', 'FILLE', og_text_all_files[fname])
            new_text = new_text_all_files[fname]
            assert new_text == correct_new_text, \
                f"Didn't update text of '{fname}' correctly to {correct_new_text} on -i -r '^GUT' /. -}}}} '\d' -}}}} -u 'x sub `file//FILLE`'\nInstead updated to {new_text}"
        og_text_all_files = Orddict(get_text_all_files())
        #~~~~~~~~~~~~~~~~~~~~~
        # TEST 2: test "sed" option
        #~~~~~~~~~~~~~~~~~~~~~
        query = "-i -r '^GUT' /. -}} -sed '\d//BL4H'"
        session.receive_query(query)
        new_text_all_files = Orddict(get_text_all_files())
        assert len(new_text_all_files) == len(og_text_all_files), \
            f"Number of files changed from {len(og_text_all_files)} to {len(new_text_all_files)} when U_OPTION_OVERWRITES was True"
        fnames_changed = {os.path.join(newdirname, 'GUT)enTHARST.js')}
        for (og_fname, og_text), (new_fname, new_text) in zip(og_text_all_files.items(),new_text_all_files.items()):
            assert og_fname == new_fname, \
                f"Filename was changed from {og_fname} to {new_fname} when -u option should not have been changing filenames"
            if og_fname in fnames_changed:
                continue
            assert og_text == new_text, f"Text of {og_fname} was changed from {og_text} to {new_text} when it should not have been changed by \"{query}\""
        for fname in fnames_changed:
            correct_new_text = re.sub('\d', 'BL4H', og_text_all_files[fname])
            new_text = new_text_all_files[fname]
            assert new_text == correct_new_text, \
                f"Didn't update text of '{fname}' correctly to {correct_new_text} on \"{query}\"\nInstead updated to {new_text}"
        og_text_all_files = Orddict(get_text_all_files())
        #~~~~~~~~~~~~~~~~~~~~~
        # TEST 3: test updating fnames, with recursive search
        #~~~~~~~~~~~~~~~~~~~~~
        session.receive_query("-f -r 'i[lt]e' -}} -u 'x sub `file//FILLE`'")
        new_text_all_files = Orddict(get_text_all_files())
        assert len(new_text_all_files) == len(og_text_all_files), \
            f"Number of files changed from {len(og_text_all_files)} to {len(new_text_all_files)} when U_OPTION_OVERWRITES was True"
        fnames_changed = set(os.path.join(newdirname, fname) for fname in 
                                ['Manowar - Warriors of the World United.txt',
                                 os.path.join('subdir', 'subdir_file.txt')])
        for (og_fname, og_text), (new_fname, new_text) in zip(og_text_all_files.items(),
                                                            new_text_all_files.items()):
            if og_fname in fnames_changed:
                continue
            assert og_fname == new_fname, \
                f"Filename was changed from {og_fname} to {new_fname} when -u option should not have been changing that filename"
            assert og_text == new_text, f"Text of {og_fname} was changed from {og_text} to {new_text} when it should not have been changed by -i -r '^GUT' /. -}} '\d' -}} -u 'x sub `file//FILLE`'"
        for fname in fnames_changed:
            new_fname = re.sub("file", "FILLE", fname)
            correct_new_text = og_text_all_files[fname]
            new_text = new_text_all_files[new_fname]
            assert new_text == correct_new_text, \
                f"Updated text of '{fname}'to {new_text} on -f -r 'i[lt]e' -}}}} -u 'x sub `file//FILLE`'\nNo update should have been made; this query should only change filenames."
        og_text_all_files = Orddict(get_text_all_files())
        #~~~~~~~~~~~~~~~~~~~~~
        # TEST 4: test updating non-text fnames
        #~~~~~~~~~~~~~~~~~~~~~
        og_listdir = set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir'))
        session.receive_query("-a 'dict' /subdir -}} -u 'x sub `alloc//Moloch`'")
        new_listdir = set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir'))
        new_text_all_files = Orddict(get_text_all_files())
        assert len(new_text_all_files) == len(og_text_all_files), \
            f"Number of files changed from {len(og_text_all_files)} to {len(new_text_all_files)} when U_OPTION_OVERWRITES was True"
        fname_changed = os.path.join('subdir', "dict size vs memory allocated.png")
        for (og_fname, og_text), (new_fname, new_text) in zip(og_text_all_files.items(), new_text_all_files.items()):
            if og_fname == fname_changed:
                continue
            assert og_fname == new_fname, \
                f"Filename was changed from {og_fname} to {new_fname} when -u option should not have been changing that filename"
            assert og_text == new_text, f"Text of {og_fname} was changed from {og_text} to {new_text} when it should not have been changed by -a 'dict' /subdir -}} -u 'x sub `alloc//Moloch`'"
        new_fname = re.sub("alloc", "Moloch", fname_changed)
        assert (fname_changed not in new_listdir) and (new_fname in new_listdir), \
            f"-u option did not correctly change {fname_changed} to {new_fname} with -a 'dict' /subdir -}} -u 'x sub `alloc//Moloch`'"
        og_text_all_files = Orddict(get_text_all_files())
        #~~~~~~~~~~~~~~~~~~~~~
        # TEST 5: test updating dirnames; this shouldn't do anything
        #~~~~~~~~~~~~~~~~~~~~~
        og_listdir = set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir'))
        session.receive_query("-d -r 'fjerejw' -}} -u 'x sub `dir//dar`'")
        new_listdir = set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir'))
        new_text_all_files = Orddict(get_text_all_files())
        assert len(new_text_all_files) == len(og_text_all_files), \
            f"Number of files changed from {len(og_text_all_files)} to {len(new_text_all_files)} when U_OPTION_OVERWRITES was True"
        fnames_changed = set()
        for (og_fname, og_text), (new_fname, new_text) in zip(og_text_all_files.items(), new_text_all_files.items()):
            assert og_fname == new_fname, \
                f"Filename was changed from {og_fname} to {new_fname} when -u option should not have been changing that filename"
            assert og_text == new_text, f"Text of {og_fname} was changed from {og_text} to {new_text} when it should not have been changed by -i -r '^GUT' /. -}} '\d' -}} -u 'x sub `file//FILLE`'"
        fname_changes = og_listdir ^ new_listdir
        assert not fname_changes, f"The names {fname_changes} occurred when the query shouldn't have done anything."
        og_text_all_files = Orddict(get_text_all_files())
        #~~~~~~~~~~~~~~~~~~~~~
        # TEST 6: test updating dirnames; this should change a name
        #~~~~~~~~~~~~~~~~~~~~~
        og_listdir = set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir'))
        session.receive_query("-d -r 'sub' -}} -u 'x sub `dir//dar`'")
        new_listdir = set(os.listdir()) | set(os.path.join('subdar', x) for  x in os.listdir('subdar'))
        new_text_all_files = Orddict(get_text_all_files())
        assert len(new_text_all_files) == len(og_text_all_files), \
            f"Number of files changed from {len(og_text_all_files)} to {len(new_text_all_files)} when U_OPTION_OVERWRITES was True"
        fnames_changed = set()
        for (og_fname, og_text), (new_fname, new_text) in zip(og_text_all_files.items(),
                                                            new_text_all_files.items()):
            if os.path.dirname(new_fname).endswith('subdar'):
                new_fname = os.path.join(newdirname, 'subdir', os.path.basename(new_fname))
            assert og_fname == new_fname, \
                f"Filename was changed from {og_fname} to {new_fname} when -u option should not have been changing that filename"
            assert og_text == new_text, f"Text of {og_fname} was changed from {og_text} to {new_text} when it should not have been changed by -d -r 'sub' -}} -u 'x sub `dir//dar`'"
        assert ('subdir' not in new_listdir) and ('subdar' in new_listdir), f"The names {fname_changes} occurred when the query shouldn't have done anything."
        og_text_all_files = Orddict(get_text_all_files())
        #~~~~~~~~~~~~~~~~~~~~~
        # TEST 7: test changing YAML when file constraints are in path
        #~~~~~~~~~~~~~~~~~~~~~
        if yaml:
            og_listdir = set(os.listdir()) | set(os.path.join('subdar', x) for  x in os.listdir('subdar'))
            session.receive_query("-f -v -i 'st$' -}} -y 'blutentharst~~@nn1' -}} -u 'float(x*3)'")
            new_listdir = set(os.listdir()) | set(os.path.join('subdar', x) for  x in os.listdir('subdar'))
            new_text_all_files = Orddict(get_text_all_files())
            assert len(new_text_all_files) == len(og_text_all_files), \
                f"Number of files changed from {len(og_text_all_files)} to {len(new_text_all_files)} when U_OPTION_OVERWRITES was True"
            fname_changed = 'RAMMSTeIN 10.yaml'
            for (og_fname,og_text),(new_fname,new_text) in zip(og_text_all_files.items(), new_text_all_files.items()):
                if os.path.basename(og_fname) == fname_changed:
                    continue
                assert og_fname == new_fname, \
                    f"Filename was changed from {og_fname} to {new_fname} when -u option should not have been changing that filename"
                assert og_text == new_text, f"Text of {og_fname} was changed from {og_text} to {new_text} when it should not have been changed by -f -v -i 'st$' -}} -y 'blutentharst~~@nn1' -}} -u 'float(x*3)'"
            with open(fname_changed) as f:
                bad_yaml = yaml.safe_load(f)
                assert bad_yaml['blutentharst'][1] == float(bad_json['blutentharst'][1]*3),\
                    f"'RAMMSTeIN 10.yaml' was not correctly updated from {bad_json} to {bad_yaml}."
        og_text_all_files = Orddict(get_text_all_files())
        #~~~~~~~~~~~~~~~~~~~~~
        # TEST 8: test changing files when U_OPTION_OVERWRITES is False
        #~~~~~~~~~~~~~~~~~~~~~
        og_listdir = set(os.listdir()) | set(os.path.join('subdar', x) for  x in os.listdir('subdar'))
        session.receive_query("DEFAULTS.U_OPTION_OVERWRITES = False")
        session.receive_query("-i '^GUT' /. -}} '\d' -}} -u 'x sub `file//FILLE`'")
        new_text_all_files = Orddict(get_text_all_files())
        fname_added = os.path.abspath('GUT)enTHARST_0.js')
        assert fname_added in new_text_all_files, \
            '-u option did not correctly create a new file with incremented fname when U_OPTION_OVERWRITES was False'
        new_file_text = new_text_all_files.pop(fname_added)
        correct_new_text = 'this is only the BL4H^th test FILLE\nGUT)enTHARST.js'
        assert new_file_text == correct_new_text, \
            f"-u option did not correctly change the file text from '{og_text_all_files['GUT)enTHARST.js']}' to '{correct_new_text}'\nInstead it was changed to {new_file_text}"
        assert len(new_text_all_files) == len(og_text_all_files), \
            f"The number of files changed from {len(og_text_all_files)} to {len(new_text_all_files)} when U_OPTION_OVERWRITES was True"
        for (og_fname, og_text), (new_fname, new_text) in zip(og_text_all_files.items(), new_text_all_files.items()):
            assert og_fname == new_fname, \
                f"Filename was changed from {og_fname} to {new_fname} when -u option should not have been changing filenames"
            assert og_text == new_text, f"Text of {og_fname} was changed from {og_text} to {new_text} when it should not have been changed by -i '^GUT' /. -}} '\d' -}} -u 'x sub `file//FILLE`'"
        og_text_all_files = Orddict(get_text_all_files())
        #~~~~~~~~~~~~~~~~~~~~~
        # TEST 9: test changing JSON files when -j option preceded by -f option
        #~~~~~~~~~~~~~~~~~~~~~
        og_listdir = set(os.listdir()) | set(os.path.join('subdar', x) for  x in os.listdir('subdar'))
        session.receive_query("-f -r 'M{2,3}S' -}} -j 'zz^j~~@..~~@\d$vvnn:' -}} -u 'str(x/4.5)'")
        new_text_all_files = Orddict(get_text_all_files())
        fname_added = os.path.abspath('RAMMSTEIN 1_0.json')
        assert fname_added in new_text_all_files, \
            '-u option did not correctly create a new file with incremented fname when U_OPTION_OVERWRITES was False'
        new_file_text = new_text_all_files.pop(fname_added)
        correct_new_text = '{"a": false, "b": "3", "6": 7, "9": "ball", "jub": {"uy": [1, 2, NaN], "yu": [[6, {"y": "b", "m8": "2.0"}], null], "status": "jubar"}, "9\\"a\\"": 2, "blutentharst": ["\\n\'\\"DOOM\\" BOOM, AND I CONSUME\', said Bludd, the mighty Blood God.\\n\\t", true]}'
        assert new_file_text == correct_new_text, \
            f"-u option did not correctly change the file text from '{og_text_all_files['RAMMSTEIN 1.json']}' to '{correct_new_text}'\nInstead it was changed to {new_file_text}"
        assert len(new_text_all_files) == len(og_text_all_files), \
            f"The number of files changed from {len(og_text_all_files)} to {len(new_text_all_files)} when U_OPTION_OVERWRITES was True"
        for (og_fname, og_text), (new_fname, new_text) in zip(og_text_all_files.items(),
                                                            new_text_all_files.items()):
            assert og_fname == new_fname, \
                f"Filename was changed from {og_fname} to {new_fname} when -u option should not have been changing filenames"
            assert og_text == new_text, f"Text of {og_fname} was changed from {og_text} to {new_text} when it should not have been changed by -f -r 'M{2,3}S' -}} -j 'zz^j~~@..~~@\d$vvnn:' -}} -u 'str(x/4.5)'"
        og_text_all_files = Orddict(get_text_all_files())
    finally:
        os.chdir(gorpdir)
        session.receive_query(f"DEFAULTS.PROMPT_U_OPTION = {previous_prompt_u_option}")
        session.receive_query(f"DEFAULTS.U_OPTION_OVERWRITES = {previous_u_option_overwrites}")
        session.close()


def main():
    setup_tempdir()
    print("~~~~~~~~~~~\ntest_killGorp()")
    test_killGorp()
    os.chdir(gorpdir)
    setup_tempdir()
    print("~~~~~~~~~~~\ntest_update()")
    test_update()
    # setup_tempdir()

if __name__ == '__main__':
    main()