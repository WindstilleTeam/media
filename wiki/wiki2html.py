#!/usr/bin/env python

from genshi.template import MarkupTemplate
import genshi.builder as bldr
import creoleparser
import sys

# Creoleparser chokes on long documents
sys.setrecursionlimit(2000)

def file2string(filename):
    f = open(filename)
    s = f.read()
    f.close()   
    return s

class Wiki2HTML:
    def macro_func(self, name, arg_string, body):
        if body == None:
            return ""

        if name == "comment":
            body = self.creole_parser.generate(body)
            return bldr.tag.div(bldr.tag(bldr.tag.div(arg_string[1:], class_='user'),
                                         bldr.tag.div(body, class_= "body")), # FIXME: Recursive comments don't really work 
                                class_='comment')
        elif name == "ind":
            body = self.creole_parser.generate(body)
            return bldr.tag.div(body, class_='indent' + arg_string[1:])
        else:
            raise Exception("Invalid Macro name: %s" % name)

    def talk_links_funcs(self, str):
        return "Talk%3a" + str + ".html"

    def main(self, args):
        if args == []:
            print "Usage: wiki2html.py FILENAME..."
        else:
            self.creole_parser = creoleparser.Parser(dialect=creoleparser.Creole10(
                    wiki_links_base_url   = '',
                    wiki_links_path_func  = lambda pagename: pagename + ".html",
                    wiki_links_space_char = ' ',
                    # no_wiki_monospace   = True,
                    use_additions         = True,
                    macro_func            = self.macro_func,
                    interwiki_links_funcs={'Talk' : self.talk_links_funcs }
                    ))


            for filename in args:
                tmpl = MarkupTemplate(file2string("template.xml"))
                print tmpl.generate(body = self.creole_parser.generate(file2string(filename)),
                                    title = filename.replace(".wiki", ""))

            
if __name__ == "__main__":
    wiki2html = Wiki2HTML()
    sys.exit(wiki2html.main(sys.argv[1:]))

# EOF #
