import re
from AppKit import NSFontManager, NSFont, NSMacOSRomanStringEncoding, NSItalicFontMask
from random import choice

__all__ = ('grid', 'random', 'choice', 'files', 'fonts', 'autotext', '_copy_attr', '_copy_attrs')

### Utilities ###

def grid(cols, rows, colSize=1, rowSize=1, shuffled = False):
    """Returns an iterator that contains coordinate tuples.
    
    The grid can be used to quickly create grid-like structures. A common way to use them is:
        for x, y in grid(10,10,12,12):
            rect(x,y, 10,10)
    """
    # Prefer using generators.
    rowRange = xrange(int(rows))
    colRange = xrange(int(cols))
    # Shuffled needs a real list, though.
    if (shuffled):
        rowRange = list(rowRange)
        colRange = list(colRange)
        shuffle(rowRange)
        shuffle(colRange)
    for y in rowRange:
        for x in colRange:
            yield (x*colSize,y*rowSize)

def random(v1=None, v2=None):
    """Returns a random value.
    
    This function does a lot of things depending on the parameters:
    - If one or more floats is given, the random value will be a float.
    - If all values are ints, the random value will be an integer.
    
    - If one value is given, random returns a value from 0 to the given value.
      This value is not inclusive.
    - If two values are given, random returns a value between the two; if two
      integers are given, the two boundaries are inclusive.
    """
    import random
    if v1 != None and v2 == None: # One value means 0 -> v1
        if isinstance(v1, float):
            return random.random() * v1
        else:
            return int(random.random() * v1)
    elif v1 != None and v2 != None: # v1 -> v2
        if isinstance(v1, float) or isinstance(v2, float):
            start = min(v1, v2)
            end = max(v1, v2)
            return start + random.random() * (end-start)
        else:
            start = min(v1, v2)
            end = max(v1, v2) + 1
            return int(start + random.random() * (end-start))
    else: # No values means 0.0 -> 1.0
        return random.random()

def files(path="*"):
    """Returns a list of files.
    
    You can use wildcards to specify which files to pick, e.g.
        f = files('*.gif')
    """
    from glob import glob
    if not type(path)==unicode:
        path = path.decode('utf-8')
    return glob(path)

from nodebox.util.foundry import family_weights
def fonts(like=None, western=True, weights=False):
    """Returns a list of all fonts installed on the system (with filtering capabilities)

    If `like` is a string, only fonts whose names contain those characters will be returned.

    If `western` is True (the default), fonts with non-western character sets will be omitted.
    If False, only non-western fonts will be returned.

    If `weights` is True, rather than returning a list, a dictionary will be returned with
    keys representing the matching family names. Their values are a mapping of Postscript
    fontnames for the family members and their corresponding numeric weight values.
    """
    fm = NSFontManager.sharedFontManager()
    def in_region(famname):
        # find font encoding (as a best guess to the region)
        facename = fm.availableMembersOfFontFamily_(famname)[0][0]
        face = NSFont.fontWithName_size_(facename, 12)
        enc = face.mostCompatibleStringEncoding()
        
        # filter out the system menu fonts
        if face.fontName().startswith('.'):
            return False

        # filter by region
        if western: return enc==NSMacOSRomanStringEncoding
        else: return enc!=NSMacOSRomanStringEncoding

    
    all_fams = [f for f in fm.availableFontFamilies() if in_region(f)]
    if like:
        all_fams = [name for name in all_fams if like.lower() in name.lower()]

    if weights:
        families = {}
        for famname in all_fams:
            families[famname] = dict(italic=family_weights(famname, italic=True), 
                                     roman=family_weights(famname))
        return families
        
    return all_fams

def autotext(sourceFile):
    from nodebox.util.kgp import KantGenerator
    k = KantGenerator(sourceFile)
    return k.output()

def _copy_attr(v):
    if v is None:
        return None
    elif hasattr(v, "copy"):
        return v.copy()
    elif isinstance(v, list):
        return list(v)
    elif isinstance(v, tuple):
        return tuple(v)
    elif isinstance(v, (int, str, unicode, float, bool, long)):
        return v
    else:
        raise NodeBoxError, "Don't know how to copy '%s'." % v

def _copy_attrs(source, target, attrs):
    for attr in attrs:
        setattr(target, attr, _copy_attr(getattr(source, attr)))
