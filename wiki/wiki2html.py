#!/usr/bin/env python

from genshi.template import MarkupTemplate
import creoleparser
import sys

# Creoleparser chokes on long documents
sys.setrecursionlimit(2000)

def file2string(filename):
    f = open(filename)
    s = f.read()
    f.close()   
    return s

def main(args):
    if args == []:
        print "Usage: wiki2html.py FILENAME..."
    else:
        creole_parser = creoleparser.Parser(dialect=creoleparser.Creole10(
                wiki_links_base_url='',
                wiki_links_path_func=lambda pagename: pagename + ".html",
                wiki_links_space_char=' ',
                # no_wiki_monospace=True,
                use_additions=True
                ))
	

        for filename in args:
            tmpl = MarkupTemplate(file2string("template.xml"))
            print tmpl.generate(body = creole_parser.generate(file2string(filename)),
                                title = filename.replace(".wiki", ""))

            
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

# EOF #
