import os
import json
from sortedcollections import ValueSortedDict
from .utils import Orddict
# tested in 3.6, 3.7, 3.8, and 3.9.
# test_TextCache didn't work in 3.7.9 because TextCache.most_recent() raised
# the error "TypeError: 'dict' object is not reversible" on the
# enumerate(reversed(self._files)) line.
# This was fixed by making it so that collections.OrderedDicts are used for 3.6 and 3.7,
# not just 3.6.

class TextCache:
    '''Caches the text of any number of files, provided that the text's memory
    consumption is less than some fixed amount (default 25 MB).
Text consumption is estimated by assuming that each character of text takes up
    2 bytes.
This is double the space used by ASCII-heavy UTF-8, but we're being 
    conservative.
No single file is allowed to take up more than 80% of the memory allotment.
If a file would lead to memory overflow but is otherwise OK, we look through 
    the files by size descending and remove them according to a heuristic 
    described in TextCache.remove_least_desirable.__doc__.

This class is designed solely to cache text from files that are parsed to text 
    by some labor-intensive process (e.g., a PDF file parsed by pdfminer or a 
    Word doc parsed by docx), so that if those files are repeatedly grepped, 
    subsequent accesses to the text in those files is relatively painless.
    
Accessors:
    self[filename] -> text of that file
    self.largest_files(n) -> list((size, file) for the n largest files)
    self.most_recent(n) -> {filename: size for the n most recent files}
    self.get(filename, default = None) -> as the corresponding dict method.
Mutators:
    self.pop(filename) -> removes filename from cache
    self[filename] = text -> maps filename to text
    self.remove_biggest() -> removes the file with the longest text.
    self.remove_least_desirable() -> See remove_least_desirable.__doc__.
    self.remove_oldest() -> removes the file least recently cached.
    
TODO: Consider removing the TextCache class altogether and instead using a
functools.lru_cache, which works like TextCache but with only the remove_oldest
method, which is invoked when it has more files than its maxsize parameter.
See https://docs.python.org/3/library/functools.html
If I decide I'm more interested in keeping <=N PDF's in memory more
so than keeping <=B MB's worth of PDF text in memory, the lru_cache could be a
good choice, although the lack of "dump" and "load" methods is problematic.
    '''
    def __init__(self, items = None, maxsize = 25_000_000, n_most_recent = 5):
        self.sizes = ValueSortedDict()
        self.n_most_recent = n_most_recent
        self._files = Orddict()
        self.maxsize = maxsize
        self.totsize = 0
        self.last_removed = None
        self._num_iterations = 3 
        # if _num_iterations is too large, it really slows down removal of files.
        if items is not None:
            for fname, text in items:
                self[fname] = text
    
    @property
    def files(self):
        return self._files
    
    def __setitem__(self, filename, text):
        if isinstance(text, str):
            size = 2*len(text)
        else:
            size = 2*sum(len(t) for t in text)
        if size > 0.8*self.maxsize:
            return # don't cache anything that takes up more than 80% of cache memory
        while self.totsize + size >= self.maxsize:
            self.last_removed = self.remove_least_desirable()
        # assumes that all text takes of 4 bytes per character. This is a gross
        # overestimate for ASCII-heavy text (which is 1 byte per character)
        # and a gross underestimate for Unicode (which takes up 4 bytes per character.
        if filename in self._files:
            self.pop(filename)
        self._files[filename] = text
        self.sizes[filename] = size
        self.totsize += size
    
    def remove_biggest(self):
        fname, size = self.sizes.keys()[-1]
        self.pop(fname)
        return fname
    
    def remove_oldest(self):
        oldest = next(iter(self._files.keys()))
        self.pop(oldest)
        return oldest
    
    def remove_least_desirable(self):
        '''Remove the data associated with one filename according to this heuristic:
    a. remove the first file that's not "recent" OR
    b. remove the first file that takes up at least 20% of memory OR
    c. if all of the three largest files satisfy (a) and (b), remove the
    fourth largest file.'''
        most_recent = self.most_recent()
        for ii, (fname, size) in enumerate(reversed(self.sizes.items())):
            if ii == self._num_iterations or (fname not in most_recent) or (size >= self.maxsize/5):
                break
        self.pop(fname)
        return fname
    
    def pop(self, filename):
        '''Remove all data associated with filename from the TextCache.
    Returns a tuple, (filename, text associated with filename).'''
        size = self.sizes[filename]
        del self.sizes[filename]
        out = self._files[filename]
        del self._files[filename]
        self.totsize -= size
        return (filename, out)
    
    def largest_files(self, n = 1):
        return self.sizes.items()[-1:-n-1:-1] # sizes are sorted smallest to largest
    
    def __len__(self):
        return len(self._files)
    
    def __contains__(self, fname):
        return fname in self._files
    
    def most_recent(self, n = None):
        '''Retrieve the (filename, text size) pairs for the n files most recently added
    to the TextCache.'''
        if n is None:
            n = self.n_most_recent
        out = {}
        for ii, fname in enumerate(reversed(self._files)):
            if ii == n:
                break
            out[fname] = 2*len(self._files[fname])
        return out
    
    def __getitem__(self, fname):
        return self._files[fname]
    
    def get(self, fname, default = None):
        '''As the .get() method of a dict, returns self[fname] if fname is a key, 
    else returns default.'''
        try:
            return self._files[fname]
        except:
            return default
    
    def keys(self):
        '''Return all filenames in the TextCache in the order they were added.'''
        return self._files.keys()
        
    def dump(self, fname = 'pdf_textcache.json'):
        '''Writes filename-text pairs to a JSON file.'''
        with open(fname, 'w', encoding = 'utf-8') as f:
            json.dump([[k, v] for k, v in self.files.items()], 
                      f, 
                      ensure_ascii = False)
            # ensure_ascii = False means that Unicode characters in the file won't be
            # escaped. This is probably better because PDF's read in by pdfminer seem
            # to have a lot of special characters
    
    @classmethod
    def load(self, fname = 'pdf_textcache.json'):
        '''Loads a JSON file containing filename-text pairs written by TextCache.dump().
        '''
        with open(fname, 'r', encoding = 'utf-8') as f:
            stuff = json.load(f)
        return TextCache(stuff)
# See https://pynative.com/python-json-encode-unicode-and-non-ascii-characters-as-is/