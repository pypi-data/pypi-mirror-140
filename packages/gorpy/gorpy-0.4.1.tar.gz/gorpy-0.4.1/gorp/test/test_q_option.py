from gorp.readfiles import *
from gorp.test.test_ku_options import setup_tempdir

previous_allow_remove_trees = ALLOW_REMOVE_TREES
previous_prompt_k_option = PROMPT_K_OPTION
previous_prompt_u_option = PROMPT_U_OPTION
previous_u_option_overwrites = U_OPTION_OVERWRITES

def main():
    session = GorpSession(print_output = False)
    try:
        session.receive_query(f"cd {os.path.join(gorpdir, 'testDir')}")
        ################
        ## TEST 1: Basic -q option; no overlap between the resultsets' files
        ################
        session.receive_query(" 'Queen' -}} -q -i 'html' /walnut")
        for fname, lines in session.resultset.items():
            for line in lines:
                if os.path.dirname(fname) == os.path.join(gorpdir, 'testDir'):
                    assert 'Queen' in line, f'Failure on {fname} at line {line}'
                else:
                    assert 'html' in line.lower(), f'Failure on {fname} at line {line}'
        ################
        ## TEST 2: Making sure that files shared by the two resultsets contain lines
        ##         from both subqueries
        ################
        session.receive_query(" 'Queen' -}} -q -i -r 'html'")
        for fname, lines in session.resultset.items():
            for line in lines:
                if os.path.dirname(fname) == os.path.join(gorpdir, 'testDir'):
                    assert ('Queen' in line) or ('html' in line.lower()), \
                            f'Failure on {fname} at line {line}'
                else:
                    assert 'html' in line.lower(), f'Failure on {fname} at line {line}'
        ################
        ## TEST 3: Check that the -k postprocessing option of the second subquery is
        ##         used on the files from both subqueries
        ################
        setup_tempdir()
        session.receive_query("DEFAULTS.PROMPT_K_OPTION = False")
        session.receive_query("cd ../test/temp")
        og_listdir = set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir'))
        session.receive_query("-r -f 'i[lt]e' -}} -q -k 'BLUT'")
        new_listdir = set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir'))
        files_to_remove = {'BLUTENTHARST.sql',
                           os.path.join('subdir', 'subdir_file.txt'),
                           'Manowar - Warriors of the World United.txt'}
        assert (og_listdir ^ new_listdir == og_listdir - new_listdir) \
                and (og_listdir - new_listdir == files_to_remove), \
            (f"-r -f 'i[lt]e' -}}}} -q -k 'BLUT' should have removed {files_to_remove}\n"
             f"but instead removed {og_listdir - new_listdir}")
        ################
        ## TEST 4: Check that the -u postprocessing option of the second subquery is
        ##         used on the files from both subqueries when renaming files
        ################
        session.receive_query("DEFAULTS.PROMPT_U_OPTION = False")
        og_listdir = set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir'))
        session.receive_query("-a -i 'dict' /subdir -}} -f -q 'Dance' -}} -u 'x sub `e//E`'")
        new_listdir = set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir'))
        files_to_remove = {os.path.join('subdir', 'dict size vs memory allocated.png'),
                           'The Rolling Stones [ Dance Part 2.py'}
        files_to_add = {os.path.join('subdir', 'dict sizE vs mEmory allocatEd.png'),
                        'ThE Rolling StonEs [ DancE Part 2.py'}
        assert og_listdir - new_listdir == files_to_remove, \
            (f"-a -i 'dict' /subdir -}} -f -q 'Dance' -}} -u 'x sub `e//E`' should have removed {files_to_remove}\n"
             f"but instead removed {og_listdir - new_listdir}")
        assert new_listdir - og_listdir == files_to_add, \
            (f"-a -i 'dict' /subdir -}} -f -q 'Dance' -}} -u 'x sub `e//E`' should have added {files_to_add}\n"
             f"but instead added {new_listdir - og_listdir}")
        ################
        ## TEST 5: Check that the -w postprocessing option of the second subquery writes
        ##         the results from both subqueries to file
        ################
        og_listdir = set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir'))
        session.receive_query("-a -i 'dict' /subdir -}} -f -q -i 'Dance' -}} -w 'dance_dict.json'")
        new_listdir = set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir'))
        files_to_add = {'dance_dict.json'}
        assert new_listdir - og_listdir == files_to_add, \
            (f"a -i 'dict' /subdir -}} -f -q -i 'Dance' -}} -w 'dance_dict.json' should have added {files_to_add}\n"
             f"but instead added {new_listdir - og_listdir}")
        with open("dance_dict.json") as f:
            dancedict = json.load(f)
        assert dancedict == {
    os.path.join(gorpdir, 'test', 'temp', "ThE Rolling StonEs [ DancE Part 2.py"): 0,
    os.path.join(gorpdir, 'test', 'temp', 'subdir', "dict sizE vs mEmory allocatEd.png"): 0
}, "The -w option did not write the correct set of files when used with the -q option."
        try:
            import yaml
        except ImportError:
            yaml = None
        if yaml is not None:
            og_listdir = set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir'))
            session.receive_query("-a -i 'dict' /subdir -}} -f -q -i 'Dance' -}} -w 'dance_dict.yaml'")
            new_listdir = set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir'))
            files_to_add = {'dance_dict.yaml'}
            assert new_listdir - og_listdir == files_to_add, \
                (f"a -i 'dict' /subdir -}} -f -q -i 'Dance' -}} -w 'dance_dict.yaml' should have added {files_to_add}\n"
                 f"but instead added {new_listdir - og_listdir}")
            with open("dance_dict.yaml") as f:
                dancedict = yaml.safe_load(f)
            assert dancedict == {
    os.path.join(gorpdir, 'test', 'temp', "ThE Rolling StonEs [ DancE Part 2.py"): 0,
    os.path.join(gorpdir, 'test', 'temp', 'subdir', "dict sizE vs mEmory allocatEd.png"): 0,
    os.path.join(gorpdir, 'test', 'temp', "dance_dict.json"): 0,
}, "The -w option did not write the correct set of files when used with the -q option."
        ################
        ## TEST 6: Testing that the -m and -s options work properly with -q option
        ################
        session.receive_query(f"cd {gorpdir}")
        session.receive_query("-f -m -s -v 'pdf_textcache\.json' -}} -q -f -r 'py$' -}} -m -s -f 'textcache'")
        for fname, lines in session.resultset.items():
            assert isinstance(lines, tuple), '-m and -s options did not combine to give last mod time and file size with -q option'
            assert (('textcache' in fname) and fname.endswith('py')) or ((os.path.dirname(fname)==gorpdir) and ('pdf_textcache.json' not in fname)), \
                "a file is in the resultset for the -q option that shouldn't be there."
        else:
            pass
    finally:
        session.receive_query(f"DEFAULTS.ALLOW_REMOVE_TREES = {previous_allow_remove_trees}")
        session.receive_query(f"DEFAULTS.PROMPT_K_OPTION = {previous_prompt_k_option}")
        session.receive_query(f"DEFAULTS.PROMPT_U_OPTION = {previous_prompt_u_option}")
        session.receive_query(f"DEFAULTS.U_OPTION_OVERWRITES = {previous_u_option_overwrites}")
        session.close()
        
if __name__ == '__main__':
    main()