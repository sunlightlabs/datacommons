# -*- coding: UTF-8 -*-

# decode_htmlentities taken from html_decode.py
# http://github.com/sku/python-twitter-ircbot
# written by JD Maturen

from htmlentitydefs import name2codepoint as n2cp
import re

def decode_htmlentities(string):
    """
    Decode HTML entities–hex, decimal, or named–in a string
    @see http://snippets.dzone.com/posts/show/4569
    
    >>> u = u'E tu vivrai nel terrore - L&#x27;aldil&#xE0; (1981)'
    >>> print decode_htmlentities(u).encode('UTF-8')
    E tu vivrai nel terrore - L'aldilà (1981)
    >>> print decode_htmlentities("l&#39;eau")
    l'eau
    >>> print decode_htmlentities("foo &lt; bar")                
    foo < bar
    """
    def substitute_entity(match):
        ent = match.group(3)
        if match.group(1) == "#":
            # decoding by number
            if match.group(2) == '':
                # number is in decimal
                return unichr(int(ent))
            elif match.group(2) == 'x':
                # number is in hex
                return unichr(int('0x'+ent, 16))
        else:
            # they were using a name
            cp = n2cp.get(ent)
            if cp: return unichr(cp)
            else: return match.group()
    
    entity_re = re.compile(r'&(#?)(x?)(\w+);')
    return entity_re.subn(substitute_entity, string)[0]

def _test():
    import doctest, html_decode
    return doctest.testmod(html_decode)

if __name__ == "__main__":
    _test()
