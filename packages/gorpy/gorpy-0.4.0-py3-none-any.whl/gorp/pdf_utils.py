'''Uses pdfminer.six to extract text from PDF documents.
This uses gorp.textcache to store text between sessions.
Main functions:
    - pagecount: counts in a document (much faster than extract_text),
    - get_text (gets the document's text as one string after checking cache),
    - get_text_by_page (gets a list of text for each page in the document 
    after checking the cache).
Currently get_text_by_page is the default function used for extracting PDF 
    text, because a (page, line) tuple is more useful for locating a line in 
    a PDF than just a line number.
'''
from pdfminer.high_level import extract_text, extract_pages, LAParams
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from .textcache import TextCache
from .utils import DEFAULT_OPTIONS, PDF_PAGE_LIMIT, gorpdir, os
import functools

pdftext_loc = os.path.join(gorpdir, 'pdf_textcache.json')

def retrieve_textcache(fname = pdftext_loc):
    '''Requires TextCache from gorp.textcache.
Extracting text from PDF's with pdfminer takes an INCREDIBLY long time (we're 
talking at least 30 seconds to extract text from a 500-page document), so it 
is much better to store the most recently retrieved PDF text in a TextCache, 
which is basically a wrapper for a dict mapping fnames to text that tracks 
size and recency of addition.
    '''
    try:
        return TextCache.load(fname)
    except FileNotFoundError:
        return TextCache()

pdf_textcache = retrieve_textcache()

def pagecount(document):
    '''document: a PDFDocument object.
    Returns: an integer, the number of pages in the document.
This takes 5-20% as long as extract_text, so it's worth checking first.'''
    metadata = document.catalog
    pgs = metadata['Pages']
    pgdict = pgs.resolve()
    return pgdict['Count']


def check_cache(pdf_analyzer):
    '''pdf_analyzer: function that performs an expensive analysis of PDF documents.
The function returned by this decorator first checks the pdf_textcache for 
    the filename, then checks to see if the number of pages in the document 
    is over the limit, and only then does the expensive analysis.'''
    @functools.wraps(pdf_analyzer)
    def wrapper(fname, *args, **kwargs):
        if fname in pdf_textcache:
            text = pdf_textcache[fname]
        else:
            with open(fname, 'rb') as f:
                parser = PDFParser(f)
                document = PDFDocument(parser)
                pagenum = pagecount(document)
            if pagenum <= PDF_PAGE_LIMIT: # from DEFAULT_OPTIONS.json
                # yes, extract_text really is that slow. We won't even TRY
                # to parse documents that are too many pages (default max is 100).
                text = pdf_analyzer(fname, *args, **kwargs)
                pdf_textcache[fname] = text
            else:
                return None
        return text
    return wrapper


@check_cache
def get_text(fname, **kwargs):
    '''Gets the text for a PDF, but only if its length is less than a 
    prespecified maximum number of pages.'''
    return extract_text(fname, **kwargs)


@check_cache
def get_text_by_page(pdf_file, laparams = LAParams(), **kwargs):
    '''As get_text, but gets the text split into pages.
    '''
    pages = extract_pages(pdf_file, **kwargs)
    out = []
    for pg in pages:
        text = ''
        pg.analyze(laparams = laparams)
        for obj in pg._objs:
            if not hasattr(obj, 'get_text'):
                text += '\n'
            else:
                text += obj.get_text()
        out.append(text)
    return out

# Below are some benchmarks for run time for pagecount vs. extract_text based on PDF
# size. The run time depends a lot on how many images and other fancy non-text things,
# as well as your hardware and current CPU load.


# 2 pages, 1356 chars parsed (printout of homework assignment, almost all ASCII)
# pagecount time:
#   22.4 ms ± 507 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)
# extract_text time:
#   103 ms ± 1.94 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)


# 21 pages, 42,674 chars parsed (printout of math lecture notes with some LaTeX)
# pagecount time:
#   8.87 ms ± 755 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)
# extract_text time:
#   1.6 s ± 29.8 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)


# 92 pages, 88,334 chars parsed, many images (printout of PowerPoint presentation)
# pagecount time:
#   698 ms ± 4.99 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
# extract_text time:
#   4.03 s (one run)


# 618 pages, 1,091,335 chars parsed, low density of images (programming textbook)
# pagecount time:
#   1.48 s ± 33.8 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
# extract_text time:
#   40.1 s (one run)