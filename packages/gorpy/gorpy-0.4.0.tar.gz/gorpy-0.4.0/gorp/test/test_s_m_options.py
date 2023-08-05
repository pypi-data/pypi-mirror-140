from gorp.readfiles import *
from gorp.test.test_ku_options import setup_tempdir
from datetime import datetime, date
import re

now = str(datetime.now())
today = str(date.today())
og_dir = os.getcwd()
newdirname = os.path.join(gorpdir, 'test', 'temp')

def main():
    setup_tempdir()
    try:
        session = GorpSession(print_output = False)
        os.chdir(newdirname)
        ################
        ## S TEST 1: TEST S OPTION IN SIMPLE CASE; NO QUALIFIER
        ################
        query = "-s -a -r ''"
        session.receive_query(query)
        results = session.resultset
        assert len(results) == 11, \
            f'For query {query}, expected 11 results, got {len(results)}'
        assert all((isinstance(v, str) and ('b' in v.lower())) \
                   for v in results.values()), \
            f'For query {query}, expected a dict mapping fnames to file size strings, got {results}'
        ################
        ## S TEST 2: TEST S OPTION WITH FILTERING <
        ################
        query = "-r -a -s<0.5kb ''"
        session.receive_query(query)
        results = session.resultset
        assert len(results) == 10, \
            f'For query {query}, expected 11 results, got {len(results)}'
        assert not any(('dict size vs' in x) for x in results), \
            f'Expected results not to contain the 29kb png file, but it contained {results}'
        ################
        ## S TEST 2: TEST S OPTION WITH FILTERING >=
        ################
        query = "-r -a -s>=50,000MB ''"
        session.receive_query(query)
        results = list(session.resultset.items())
        assert len(results) == 0, \
            f'For query {query}, expected no results, got {len(results)}'
        ################
        ## M TEST 1: TEST M OPTION IN SIMPLE CASE; NO QUALIFIER
        ################
        query = "-m -a -r ''"
        session.receive_query(query)
        results = session.resultset
        assert len(results) == 11, \
            f'For query {query}, expected 11 results, got {len(results)}'
        assert all(isinstance(v, str) and (v[:10] == today) \
                   for v in results.values()), \
            f'For query {query}, expected a dict mapping fnames to date strings, got {results}'
        ################
        ## M TEST 1: TEST M OPTION WITH FILTERING >=
        ################
        query = f"-m>={today} -a -r ''"
        session.receive_query(query)
        results = session.resultset
        assert len(results) == 11, \
            f'For query {query}, expected 11 results, got {len(results)}'
        ################
        ## M TEST 1: TEST M OPTION WITH FILTERING <
        ################
        query = f"-m<{today} -a -r ''"
        session.receive_query(query)
        results = session.resultset
        assert len(results) == 0, \
            f'For query {query}, expected no results, got {len(results)}'
        ################
        ## S + M TEST 1: TEST S AND M OPTIONS TOGETHER IN SIMPLE CASE
        ################
        query = "-m -r -s -a ''"
        session.receive_query(query)
        results = session.resultset
        assert len(results) == 11, \
            f'For query {query}, expected 11 results, got {len(results)}'
        assert all(isinstance(v, tuple) \
                    and (v[0][:10] == today and ('b' in v[1].lower())) \
                   for v in results.values()), \
            f'For query {query}, expected a dict mapping fnames to (date string, file size string), got {results}'
        ################
        ## S + M TEST 1: TEST S AND M OPTIONS TOGETHER;
        ##    FILTERING FOR >1kb and today or later
        ################
        query = f"-m>={today} -r -s>1kb -a ''"
        session.receive_query(query)
        results = session.resultset
        results = list(session.resultset.items())
        assert len(results) == 1, \
            f'For query {query}, expected 1 result, got {len(results)}'
        assert ('dict size vs' in results[0][0]), \
            f'Expected results to contain only the 29kb png file, but it contained {results}'
        ################
        ## S + M TEST 1: TEST S AND M OPTIONS TOGETHER WITH NUM OPTION;
        ##    FILTERING FOR >1kb and today or later, and at most 5 files
        ################
        query = f"-m>={today} -r -s>1kb -5 -a ''"
        session.receive_query(query)
        results = session.resultset
        results = list(session.resultset.items())
        assert len(results) == 1, \
            f'For query {query}, expected 1 result, got {len(results)}'
        assert ('dict size vs' in results[0][0]), \
            f'Expected results to contain only the 29kb png file, but it contained {results}'
    finally:
        os.chdir(og_dir)
        session.close()
    
if __name__ == '__main__':
    main()