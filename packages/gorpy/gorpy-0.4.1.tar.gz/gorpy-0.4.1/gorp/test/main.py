from gorp.test import test_ku_options
from gorp.test import test_jsonpath
from gorp.test import test_textcache
from gorp.test import test_option_combos
from gorp.test import test_pdf_option
from gorp.test import test_q_option
from gorp.test import test_e_w_options
from gorp.test import test_zip
from gorp.test import test_x_option
from gorp.test import test_b_option
from gorp.test import test_s_m_options
import doctest

def main():
    print("WARNING: If you put any files into testDir other than what's in there by default, some of the tests are likely to fail.")
    print("===============\nTesting TextCache")
    tc = test_textcache.main()
    print("===============\nTesting killing and updating of files")
    test_ku_options.main()
    print("===============\nTesting jsonpath (no output means everything is fine)")
    doctest.testmod(test_jsonpath)
    doctest.testmod(test_jsonpath.aggregate)
    print("===============\nTesting many different combinations of options")
    test_option_combos.test_combo_results()
    print("===============\nTesting the PDF option")
    test_pdf_option.main()
    print("===============\nTesting the q option for unioning resultsets")
    test_q_option.main()
    print("===============\nTesting e and w options for writing/reading resultsets to/from file")
    test_e_w_options.main()
    print("===============\nTesting -z option for zipping files together")
    test_zip.main()
    print("===============\nTesting -x option for reading XML and HTML")
    test_x_option.main()
    print("===============\nTesting -b option for reading files as raw bytes")
    test_b_option.test_combo_results()
    print("===============\nTesting -m and -s options for getting mod times and sizes of files")
    test_s_m_options.main()
    
if __name__ == '__main__':
    main()