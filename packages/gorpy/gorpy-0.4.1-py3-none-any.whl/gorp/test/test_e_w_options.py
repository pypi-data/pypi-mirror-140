from gorp.readfiles import *
from gorp.test.test_ku_options import setup_tempdir

og_dir = os.getcwd()
newdirname = os.path.join(gorpdir, 'test', 'temp')

def main():
    setup_tempdir()
    try:
        session = GorpSession(print_output = False)
        os.chdir(newdirname)
        ################
        ## W TEST 1: TEST W OPTION IN SIMPLE CASE; WRITING TO CURRENT DIRECTORY
        ################
        og_listdir = set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir'))
        query = "-a -i -r 'dict|dance' /. -}} -w 'dance_dict.json'"
        session.receive_query(query)
        new_listdir = set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir'))
        files_to_add = {'dance_dict.json'}
        assert new_listdir - og_listdir == files_to_add, \
            (f"{query} should have added {files_to_add}\n"
             f"but instead added {new_listdir - og_listdir}")
        with open("dance_dict.json") as f:
            dancedict = json.load(f)
        correct_dancedict = {
            os.path.join(newdirname, "The Rolling Stones [ Dance Part 2.py"): 0,
            os.path.join(newdirname, 'subdir', "dict size vs memory allocated.png"): 0
        }
        assert dancedict == correct_dancedict, f"{query} should have written {gprint(correct_dancedict, str)} to {files_to_add}, instead wrote {gprint(dancedict, str)}."
        ################
        ## E TEST 1: TEST E OPTION IN SIMPLE CASE; READING FROM CURRENT DIRECTORY
        ################
        og_listdir = set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir'))
        query = "-e -a '' /dance_dict.json -}} -a 'png'"
        session.receive_query(query)
        new_listdir = set(os.listdir()) | set(os.path.join('subdir', x) for  x in os.listdir('subdir'))
        assert new_listdir == og_listdir, \
            (f"{query} should not have changed the directory\n"
             f"but instead changed {new_listdir ^ og_listdir}")
        correct_resultset = [os.path.join(newdirname, 'subdir', 
                                'dict size vs memory allocated.png')]
        assert session.resultset == correct_resultset, \
                f'{query} should have given resultset {correct_resultset}\nbut instead gave {session.resultset}' 
    finally:
        os.chdir(og_dir)
        session.close()
    
if __name__ == '__main__':
    main()