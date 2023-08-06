from gorp.readfiles import *
from zipfile import ZipFile
import shutil
from gorp.test.test_ku_options import setup_tempdir
ogdir = os.getcwd()

def main():
    setup_tempdir()
    os.chdir(os.path.join(gorpdir, 'test', 'temp'))
    session = GorpSession(print_output = False)
    try:
        # TEST 1: one file
        og_listdir = set(os.listdir())
        query = "-a 'HUND' -}} -z 'zip_test.zip'"
        session.receive_query(query)
        new_listdir = set(os.listdir())
        assert new_listdir == og_listdir | {'zip_test.zip'}, \
            f"{query} did not correctly create the new zip file 'zip_test.zip'"
        zf = ZipFile('zip_test.zip')
        files_in_zf = set(x.filename for x in zf.filelist)
        correct_files_in_zf = {'HUNDENtharst.cpp'}
        assert files_in_zf == correct_files_in_zf, \
            f"For query {query}, 'zip_test.py' should have contained only {correct_files_in_zf}, but instead contained {files_in_zf}"
        zf.close()
        os.unlink('zip_test.zip')
        
        # TEST 2: one file, working from a different directory
        og_listdir = set(os.listdir())
        query = "-a 'dict' /subdir -}} -z 'zip_test.zip'"
        session.receive_query(query)
        new_listdir = set(os.listdir())
        assert new_listdir == og_listdir | {'zip_test.zip'}, \
            f"{query} did not correctly create the new zip file 'zip_test.zip'"
        zf = ZipFile('zip_test.zip')
        files_in_zf = set(x.filename for x in zf.filelist)
        correct_files_in_zf = {"dict size vs memory allocated.png"}
        assert files_in_zf == correct_files_in_zf, \
            f"For query {query}, 'zip_test.py' should have contained only {correct_files_in_zf}, but instead contained {files_in_zf}"
        zf.close()
        os.unlink('zip_test.zip')
        
        # TEST 3: multiple files in multiple directories
        query = "-a -i -r 'dance|dict' /. -}} -z 'zip_test.zip'"
        session.receive_query(query)
        new_listdir = set(os.listdir())
        assert new_listdir == og_listdir | {'zip_test.zip'}, \
            f"{query} did not correctly create the new zip file 'zip_test.zip'"
        zf = ZipFile('zip_test.zip')
        files_in_zf = set(x.filename for x in zf.filelist)
        correct_files_in_zf = {'The Rolling Stones [ Dance Part 2.py',
                          'subdir/dict size vs memory allocated.png'}
        assert files_in_zf == correct_files_in_zf, \
            f"For query {query}, 'zip_test.py' should have contained only {correct_files_in_zf}, but instead contained {files_in_zf}"
        zf.close()
        os.unlink('zip_test.zip')
        
        # TEST 4: multiple files in multiple directories,
        #   working from a different directory
        query = "-f -r 'subdir_f' /subdir -}} -z 'zip_test.zip'"
        subsubdir = os.path.join('subdir', 'subsubdir')
        os.mkdir(subsubdir)
        with open(os.path.join(subsubdir, 'subdir_file.txt'), 'w') as f:
            f.write('blah')
        session.receive_query(query)
        new_listdir = set(os.listdir())
        assert new_listdir == og_listdir | {'zip_test.zip'}, \
            f"{query} did not correctly create the new zip file 'zip_test.zip'"
        zf = ZipFile('zip_test.zip')
        files_in_zf = set(x.filename for x in zf.filelist)
        correct_files_in_zf = {'subdir_file.txt',
                               os.path.join('subsubdir', 'subdir_file.txt')}
        other_correct_files_in_zf = {'subdir_file.txt', 
                                     'subsubdir/subdir_file.txt'}
        # on Windows, it seems that Python sometimes makes the Unix '/' pathsep
        # (which Windows is technically OK with), but the canonical os.path.sep
        # for Windows is '\\', so we wind up having to check both possibilities
        if files_in_zf != correct_files_in_zf \
        and files_in_zf != other_correct_files_in_zf:
            raise ValueError(f"For query {query}, 'zip_test.py' should have contained only {correct_files_in_zf} or {other_correct_files_in_zf}, but instead contained {files_in_zf}")
        zf.close()
        shutil.rmtree(subsubdir)
        os.unlink('zip_test.zip')
        
        # TEST 5: multiple files in same directory
        for zip_opt in ['z', 'zl', 'zb']:
            # try uncompressed, LZMA-zipped, and bzipped.
            query = f"-a 'THARST' /. -}} -{zip_opt} 'zip_test.zip'"
            session.receive_query(query)
            new_listdir = set(os.listdir())
            assert new_listdir == og_listdir | {'zip_test.zip'}, \
                f"{query} did not correctly create the new zip file 'zip_test.zip'"
            zf = ZipFile('zip_test.zip')
            files_in_zf = set(x.filename for x in zf.filelist)
            correct_files_in_zf = {'BLUTENTHARST.sql',
                                   'dud(ENTHARST.java',
                                   'GUT)enTHARST.js'}
            assert files_in_zf == correct_files_in_zf, \
                f"For query {query}, 'zip_test.py' should have contained only {correct_files_in_zf}, but instead contained {files_in_zf}"
            zf.close()
            os.unlink("zip_test.zip")
    finally:
        try:
            zf.close()
        except:
            pass
        if os.path.exists('zip_test.zip'):
            os.unlink('zip_test.zip')
        os.chdir(ogdir)
    
if __name__ == '__main__':
    main()