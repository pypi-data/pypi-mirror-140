'''A utility for storing PDF text.
Since pdfminer.six takes a VERY LONG TIME to extract text from PDF's, it's
better to store the text in a database and query that database whenever
you need the text for a file.'''
import datetime
import functools
import json
import os
import sqlite3
from .utils import last_mod_time

dbdef = '''
CREATE TABLE IF NOT EXISTS files(
    fname TEXT,
    text TEXT,
    modtime TEXT,
    insertion_time TEXT,
    size INT
);
CREATE INDEX idx ON files(fname)
'''


def with_connection(meth):
    '''Connect to the database at the file path of a TextCache's dbname,
    try to perform the method's function, commit if successful,
    clean up if there's an error, and finally close the database.'''
    @functools.wraps(meth)
    def wrapper(*args, **kwargs):
        tc = args[0]
        tc.con = sqlite3.connect(tc.dbname)
        try:
            out = meth(*args, **kwargs)
        except Exception as ex:
            tc.con.rollback()
            raise ex
        else:
            # print(f'commited transaction from method {meth} with args {args} and kwargs {kwargs}')
            tc.con.commit()
            return out
        finally:
            tc.con.close()
            tc.con = None

    return wrapper


class TextCache:
    '''A wrapper around a SQLite database containing filenames, file modification times, file sizes, and text.
    
    Contains functions for getting files with different properties.
    
    Also has __getitem__ and __setitem__ defined so that you can add
    (file, text) pairs and retrieve files as if this were a dict.'''
    def __init__(self, dbname='pdf_textcache.sqlite'):
        self.dbname = dbname
        self.con = None # filled in when calling with_connection methods
        # create the database if there isn't one already.
        # add an index on filenames to speed searches.
        if not os.path.exists(dbname):
            con = sqlite3.connect(dbname)
            try:
                con.executescript(dbdef)
            except Exception as ex:
                con.rollback()
                raise ex
            else:
                con.commit()
            finally:
                con.close()

    @with_connection
    def __contains__(self, fname):
        out = self.con.execute("SELECT fname FROM files WHERE fname = ?",
                            (fname,)).fetchone()

        return bool(out)

    @with_connection
    def __getitem__(self, fname):
        txt = self.con.execute("SELECT text FROM files WHERE fname = ?",
                                 (fname,)).fetchone()
        if not txt:
            raise KeyError(f"{fname} is not in this TextCache")

        return json.loads(txt[0])

    @with_connection
    def __setitem__(self, fname, txt):
        row = self.con.execute("SELECT * FROM files WHERE fname = ?",
                               (fname,)).fetchone()
        modtime = str(last_mod_time(fname))
        now = str(datetime.datetime.now())
        txtstr = json.dumps(txt)
        size = len(txtstr)
        # print(locals())
        if row:
            insertion_time = row[3]
            oldtext = row[1]
            # print(f'{modtime = }, {insertion_time = }')
            if insertion_time >= modtime and hash(oldtext) == hash(txtstr):
                # do nothing if the file hasn't changed
                # usually comparing modtimes is adequate, but it's possible
                # that the pdf was modified within the last second,
                # so we'll check that as a fallback
                return
            else:
                # print('updating') # replace data associated with fname
                self.con.execute("UPDATE files SET (text, modtime, insertion_time, size) = (?, ?, ?, ?) WHERE fname = ?",
                                (txtstr, modtime, now, size, fname))
        else: # add new data
            self.con.execute("INSERT INTO files VALUES(?, ?, ?, ?, ?)",
                             (fname, txtstr, modtime, now, size))
    
    @with_connection
    def keys(self):
        '''a list of the files in this TextCache'''
        out = self.con.execute("SELECT fname FROM files").fetchall()
        if not out:
            return []

        return [x[0] for x in out]
    
    @property
    def files(self):
        return self.keys()
    
    @with_connection
    def get_all_data(self, fname):
        '''get all rows associated with fname. There should only be one per
        file.'''
        return self.con.execute("SELECT * FROM files WHERE fname = ?", 
                                (fname,)).fetchall()
    
    def get(self, fname, default=None):
        try:
            return self[fname]
        except KeyError:
            return default
            
    @with_connection
    def __delitem__(self, fname):
        self.con.execute("DELETE FROM files WHERE fname = ?", (fname,))
    
    pop = __delitem__
    
    @with_connection
    def largest_files(self, n=1):
        return self.con.execute("SELECT fname, size FROM FILES ORDER BY size DESC LIMIT ?", (n,)).fetchall()
        
    @with_connection
    def smallest_files(self, n=1):
        return self.con.execute("SELECT fname, size FROM FILES ORDER BY size LIMIT ?", (n,)).fetchall()
        
    @with_connection
    def oldest_files(self, n=1):
        return self.con.execute("SELECT fname, modtime FROM FILES ORDER BY modtime LIMIT ?", (n,)).fetchall()
        
    @with_connection
    def newest_files(self, n=1):
        return self.con.execute("SELECT fname, modtime FROM FILES ORDER BY modtime DESC LIMIT ?", (n,)).fetchall()
    
    @with_connection
    def execute(self, query):
        out = self.con.execute(query)
        return out.fetchall()