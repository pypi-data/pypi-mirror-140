from gorp.readfiles import *
ogdir = os.getcwd()
newdir = os.path.join(gorpdir, 'testDir')

def main():
    os.chdir(newdir)
    session = GorpSession(print_output = False)
    try:
        ###########
        ## TEST 1: Test CSS selectors
        ###########
        fname = os.path.join(newdir, 'bluddGame.htm')
        query = f"-x 'img.Bludd' /{fname}"
        session.receive_query(query)
        correct_output = {f'{fname}': ['b\'<img class="Bludd" id="Bludd" src=".\\\\viking pics\\\\Bludd.png" height="100" width="100" alt="Bludd, Blood God" title="Bludd, the Blood God (of Blood!)"/>&#13;\\n\'']}
        assert session.resultset == correct_output, \
            f"{query} should have returned {correct_output};\nInstead returned {session.resultset}"
        ###########
        ## TEST 1: Test XPath and ability to handle multiple results per file
        ###########
        fname = os.path.join(newdir, 'books.xml')
        query = f"-x -n '//bookstore//book[@category]' /{fname}"
        session.receive_query(query)
        correct_output = {fname:
    {('bookstore', 0): 'b\'<book category="cooking">\\n    <title lang="en">Everyday Italian</title>\\n    <author>Giada De Laurentiis</author>\\n    <year>2005</year>\\n    <price>30.00</price>\\n  </book>\\n  \'',
    ('bookstore', 1): 'b\'<book category="children">\\n    <title lang="en">Harry Potter</title>\\n    <author>J K. Rowling</author>\\n    <year>2005</year>\\n    <price>29.99</price>\\n  </book>\\n  \'',
    ('bookstore', 2): 'b\'<book category="web">\\n    <title lang="en">Learning XML</title>\\n    <author>Erik T. Ray</author>\\n    <year>2003</year>\\n    <price>39.95</price>\\n  </book>\\n\''}
}
        assert session.resultset == correct_output, \
            f"{query} should have returned {correct_output};\nInstead returned {session.resultset}"
    finally:
        os.chdir(ogdir)
        session.close()
        
if __name__ == '__main__':
    main()
        