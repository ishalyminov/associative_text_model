#!/usr/bin/python

import sys
import model
        
def main(in_stream):
    text = ' '.join([line.strip() for line in in_stream])
    text_model = model.AssociativeModelBuilder(text)
    print text_model.text_as_string()
    
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: build_model.py <raw text file name>'
        sys.exit(0)
    with open(sys.argv[1]) as stream:
        main(stream)
