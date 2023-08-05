from gorp.readfiles import *
import itertools
# tested on Python 3.6 - 3.9

def test_pdf_option():
    try:
        import gorp.pdf_utils # just importing to get any ImportErrors out of the way
    except ImportError:
        warn_first_import_error("pdfminer")
        warn_first_import_error("sortedcollections")
        return None, None
    os.chdir(gorpdir)
    base_query = "-r -a 'pdf$' -}} "
    regex_dirname = " -pdf 'WORLD|html' /testDir"
    options = ['-l', '-h', '-i', '-c', '-o', '-n']
    all_combos = (itertools.combinations(options, ii) for ii in range(6))
    opt_combos = [c for combos in all_combos for c in combos]
    bad_combos = {}
    query_results = {}
    with GorpSession(print_output = False) as session:
        for combo in opt_combos:
            Combo = ' '.join(combo)
            comboset = frozenset(re.findall('[a-z]+', Combo))
            query = base_query + Combo + regex_dirname
            try:
                session.receive_query(query)
                query_results[comboset] = session.resultset
            except Exception as ex:
                bad_combos[comboset] = repr(ex)
    return query_results, bad_combos

    
def main():
    query_results, bad_combos = test_pdf_option()
    assert not bad_combos, 'At least one query with the pdf option failed'
    return query_results, bad_combos

if __name__ == '__main__':
    query_results, bad_combos = main()