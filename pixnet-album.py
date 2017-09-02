#!/usr/bin/env python
# -.- coding: utf-8 -.-

import sys, os
from urlparse import urlparse
import re

import requests
from bs4 import BeautifulSoup


def get_soup(url):
    r = requests.get(url)
    r.encoding = 'utf-8' # force encoding, or will be ISO-8859-1
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup


def main(url):
    """ex: python pixnet-album.py http://xxxxx.pixnet.net/album/set/xxxxxx"""

    rows = []
    o = urlparse(url)
    base_url = '%s://%s' % (o.scheme, o.netloc)
    album = o.path.split('/')[-1]
    
    # 1. fetch recursive
    next_url = url    
    while next_url:
        
        soup = get_soup(next_url)
        a = soup.select('.photo-grid-list .photo-grid img')
        b = soup.select('.nextBtn')        
        if a:
            rows += a
            
        if b and b[0].get('href', ''):
            next_url = base_url + b[0]['href']
        else:
            next_url = ''

    num_rows = len(rows)
    # 2. analyis image url and download
    if len(rows):
        
        if not os.path.isdir(album):
            os.mkdir(album)
            
        n = 0
        d = 0
        for i in rows:
            
            m = re.search(r'(.+)_(.+)(.jpg|.png)', i['src'])
            if m and m.group(1) and m.group(3):
                n += 1
                img_url = m.group(1) + m.group(3)
                out_fname = '%04d-%s%s' % (n, i.get('alt', ''), m.group(3))

                print '>> %d/%d' % (n, num_rows), ' | ', out_fname
                
                # download
                r = requests.get(img_url, stream=True)                
                with open(os.path.join(album, out_fname), 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=128):
                        fd.write(chunk)
                d += 1
                
    # 3. results
    print '> get %d tags.' % (num_rows)            
    print '> analysis %d tags, downloaded %d files' % (n, d)

        
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'usage pixnet-album.py [url]'
    else:
        main(sys.argv[1])


