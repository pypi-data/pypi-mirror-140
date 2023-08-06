from gorp.readfiles import GorpSession, gorpdir
import itertools
import os
try:
    import gorp.pdf_utils # just importing to get any ImportErrors out of the way
except ImportError:
    warn_first_import_error("pdfminer")
# tested on Python 3.6 - 3.9

def test_pdf_option():
    ogdir = os.getcwd()
    os.chdir(gorpdir)
    base_query = "-r -a 'pdf$' /testDir -}} "
    regex_dirname = " -i -pdf 'WORLD|html'"
    opt_combos = [('-c', '-n'), ('-n',), ('-c',)]
    bad_combos = {}
    query_results = {}
    with GorpSession(print_output = False) as session:
        for combo in opt_combos:
            Combo = ' '.join(combo)
            comboset = frozenset(combo)
            query = base_query + Combo + regex_dirname
            try:
                session.receive_query(query)
                query_results[comboset] = session.resultset
                assert query_results[comboset], f"Resultset for query {query} should not be empty, but it is."
            except Exception as ex:
                bad_combos[comboset] = repr(ex)
    os.chdir(ogdir)
    return query_results, bad_combos

    
def main():
    query_results, bad_combos = test_pdf_option()
    if bad_combos:
        print('At least one query with the pdf option failed')
    return query_results, bad_combos

if __name__ == '__main__':
    if gorp.pdf_utils:
        query_results, bad_combos = main()