from gorp.readfiles import *
from gorp.test.test_ku_options import setup_tempdir
import itertools

og_dirname = os.getcwd()

def get_combos():
    setup_tempdir()
    os.chdir(os.path.join(gorpdir, 'test', 'temp'))
    base_query = " -b '[bp]l[uo]t' /."
    gorptags = ['-r', '-l', '-h', '-i', '-c', '-o', '-n', '-v']
    tag_combos = (c for combos in \
                  (itertools.combinations(gorptags,ii) for ii in range(9)) \
                  for c in combos)             
    query_results = {}
    bad_combos = {}
    session = GorpSession(print_output = False)
    try:
        for combo in tag_combos:
            Combo = ' '.join(combo)
            try:
                session.receive_query(Combo+base_query)
                out = session.old_queries['prev'].resultset
                query_results[frozenset(re.findall('[a-z]+',Combo))] = out
            except Exception as ex:
                bad_combos[frozenset(re.findall('[a-z]+', Combo))] = repr(ex)
    finally:
        session.close()
        os.chdir(og_dirname)
        return query_results,bad_combos
        
def test_combo_results():
    query_results, bad_combos = get_combos()
    assert len(bad_combos) == 0, \
        'At least one combination of options raised an error under normal circumstances'
    return query_results, bad_combos
        
if __name__ == '__main__':
    query_results, bad_combos = test_combo_results()