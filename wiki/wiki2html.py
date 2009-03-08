#!/usr/bin/env python

import traceback
import os.path
import codecs
import re
from genshi.template import MarkupTemplate
from genshi import XML
from genshi import HTML
from genshi import Stream
import genshi.builder as bldr
import creoleparser
import sys

# Creoleparser chokes on long documents
sys.setrecursionlimit(2000)

token_pat = re.compile('\s*([A-Za-z_]+) *= *"([^"]+)"\s*')

def parse_arg_string(str):
    dict = {}  
    while str:
        m = token_pat.match(str)
        if not m:
            raise Exception("Couldn't match '%s'" % str)
        dict[m.group(1)] = m.group(2)
        str = str[m.end():]
    return dict

def file2string(filename):
    f = codecs.open(filename, encoding='utf-8')
    s = f.read()
    f.close()
    return s

all_pages = ['Windstille',
             'News',
             'Rebirth',
             'Backstory',
             'Characters',
             'Suits',
             'Vehicles',
             'Planets',
             'Locations',
             'Missions',
             'Coding style',
             'Particles',
             'Navigation Mesh',
             'Dialog',
             'Scripting',
             'Squirrel',
             'Drawing Model',
             'Drawing Primitives',
             'Editor',
             'Controls',
             'Actions',
             'PDA',
             'Weapons',
             'Fighting',
             'Sector',
             'Blender',
             'BlenderToSprite3D',
             'Sprite3D',
             'Sprite',
             'About']

def find_next_page(str):
    for i in range(len(all_pages)):
        if all_pages[i] == str:
            if i == len(all_pages)-1:
                return "Windstille"
            else:
                return all_pages[i+1]
    raise Exception("Couldn't find next page for " + str)

def find_prev_page(str):
    for i in range(len(all_pages)):
        if all_pages[i] == str:
            if i == 0:
                return "Windstille"
            else:
                return all_pages[i-1]
    raise Exception("Couldn't find prev page for " + str)

class Wiki2HTML:
    def macro_func(self, name, arg_string, body, block_type):
        if name == "comment":
            body = self.creole_parser.generate(body)
            return bldr.tag.div(body, class_= 'comment')

        elif name == "note":
            if body:
                body = self.creole_parser.generate(body)
                return bldr.tag.div(body, class_='note')
            else:
                return None

        elif name == "class":
            if body:
                return bldr.tag.a(body, class_='class', href="../docs/class" + body + ".html")
            else:
                return None

        elif name == "thumbnail":
            dict = parse_arg_string(arg_string)
            if not dict.has_key('src'):
                raise Exception("Source argument missing from <<img>>")

            if dict.has_key('alt'):
                alt = dict['alt']
            else:
                alt = dict['src']

            if dict.has_key('title'):
                title = dict['title']
            else:
                title = None

            return bldr.tag.a(bldr.tag.img(None, src="thumbnails/" + dict['src'], alt=alt, title=title, class_="thumbnail"),
                              href="images/" + dict['src'])

        elif name == "raw":
            return HTML(body) # FIXME: Why can't we use XML()?
        
        elif name == "youtube":
            dict = parse_arg_string(arg_string)            
            
            # autoplay=1 - starts video automatically
            # rel=0      - removes the related video menu at the end
            # ap=%2526fmt%3D18 - highquality 
            return bldr.tag.object(
                bldr.tag.param(None, 
                               name="movie",
                               value="http://www.youtube.com/v/%s&hl=en&fs=1&rel=0&loop=1&ap=%%2526fmt%%3D18" % dict['src']) +
                bldr.tag.param(None, name="allowFullScreen",   value="true") +
                bldr.tag.param(None, name="allowscriptaccess", value="always") +
                bldr.tag.embed(None, 
                               src="http://www.youtube.com/v/%s&hl=en&fs=1&rel=0&loop=1&ap=%%2526fmt%%3D18" % dict['src'],
                               type="application/x-shockwave-flash",
                               allowscriptaccess="always",
                               allowfullscreen="true",
                               width="425",
                               height="344"),
                width="425", height="344",
                class_="youtube")

        elif name == "image":
            dict = parse_arg_string(arg_string)

            if not dict.has_key('src'):
                raise Exception("Source argument missing from <<img>>")

            title = None
            if dict.has_key('title'):
                title = dict['title']

            if dict.has_key('href'):
                return bldr.tag.a(bldr.tag.img(None, 
                                               src=dict['src'],
                                               alt=dict['src'], 
                                               title=title, 
                                               class_= 'image'),
                                  href=dict['href'])
            else:
                return bldr.tag.img(None, src="images/" + dict['src'], alt=dict['src'], title=title, class_= 'image')

        elif name == "ind":
            body = self.creole_parser.generate(body)
            return bldr.tag.div(body, class_='indent' + arg_string[1:])
        else:
            raise Exception("Invalid Macro name: %s" % name)

    def talk_links_funcs(self, str):
        return "Talk%3a" + str + ".html"

    def main(self, args):
        if args == []:
            print "Usage: wiki2html.py -o DIRECTORY FILENAME..."

        else:
            if len(args) < 3 or args[0] != '-o':
                raise Exception("Usage: wiki2html.py -o DIRECTORY FILENAME...")
            else:
                directory = args[1]
                args = args[2:]

                self.creole_parser = creoleparser.Parser(dialect=creoleparser.Creole10(
                        wiki_links_base_url   = '',
                        wiki_links_path_func  = lambda pagename: pagename + ".html",
                        wiki_links_space_char = ' ',
                        # no_wiki_monospace   = True,
                        use_additions         = True,
                        macro_func            = self.macro_func,
                        interwiki_links_funcs={'Talk' : self.talk_links_funcs }
                        ))

                try:
                    for filename in args:
                        tmpl = MarkupTemplate(file2string("template.xml"))
                        text = tmpl.generate(next = find_next_page(os.path.basename(filename)[:-5]),
                                             prev = find_prev_page(os.path.basename(filename)[:-5]),
                                             thispage = os.path.basename(filename),
                                             body = self.creole_parser.generate(file2string(filename)),
                                             title = filename.replace(".wiki", "")).render(method='xhtml', 
                                                                                           encoding='latin-1',
                                                                                           strip_whitespace=True)
                        f = open(directory + '/' + os.path.basename(filename)[:-5] + ".html", 'w')
                        f.write(text)
                        f.close()

                except Exception, err:
                    traceback.print_tb(sys.exc_info()[2], 10, sys.stderr)
                    sys.stderr.write(str(err) + "\n")

            
if __name__ == "__main__":
    wiki2html = Wiki2HTML()
    sys.exit(wiki2html.main(sys.argv[1:]))

# EOF #
