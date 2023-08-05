import lxml
from lxml import etree
try:
    from lxml.cssselect import CSSSelector 
    # note that this adds the cssselect package as a dependency
except:
    CSSSelector = None
    print("The 'cssselect' package is required if you want to use CSS selectors as well as XPath for the XML/HTML-search 'x' option.")
from lxml.html import XHTMLParser
from .utils import get_ext, text_encodings
htmlparser = etree.HTMLParser()
xmlparser = etree.XMLParser()
xhtmlparser = XHTMLParser()

def xpath_to_element_text(fname, path, pretty_print = False, allow_css_selectors = True):
    '''fname: name of (X|HT)ML document.
path: string. An XPath (or CSS selector if fname is HTML and allow_css_selectors).
pretty_print: bool. If True, the XML string emitted by this function will be
    pretty_printed with nice indentation.
Reads the text of an (X|HT)ML document and returns a dict mapping a list of the 
    ancestors' tags to the full text (including the tags, etc.) of all elements in 
    that document that can be found by following path.'''
    html = 'ht' in get_ext(fname)
    if html:
        parsers = [htmlparser, xhtmlparser, xmlparser]
    else:
        parsers = [xmlparser, xhtmlparser]
    for parser in parsers:
        try:
            tree = etree.parse(fname, parser)
            break
        except:
            pass
    try:
        tree
    except NameError:
        return
    if html and allow_css_selectors:
        try:
            selector = CSSSelector(path)
            results = selector.evaluate(tree)
        except lxml.cssselect.SelectorSyntaxError: 
            # hopefully if it was either a valid CSS selector or a valid XPath
            results = tree.xpath(path)
    else:
        results = tree.xpath(path)
    del tree
    out = {}
    for ii, res in enumerate(results):
        fulltext = etree.tostring(res, pretty_print = pretty_print)
        ancestors = tuple(reversed([x.tag for x in res.iterancestors()]))
        out[ancestors + (ii,)] = fulltext
    return out
                