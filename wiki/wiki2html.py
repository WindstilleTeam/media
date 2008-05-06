#!/usr/bin/env python

import creoleparser
import sys

def main(args):
    if args == []:
        print "Usage: wiki2html.py FILENAME..."
    else:
        for filename in args:
            f = open(filename)
            print creoleparser.text2html(f.read())
            f.close()
            
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

# EOF #
