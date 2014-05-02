#-*-coding=utf-8-*-

import re
import os
import codecs
from collections import defaultdict


def initial_concordance(path=u'/.'):
    concordance = defaultdict(int)
    totalWords = 0
    reTokenize = re.compile(u'[\\s:;,.()\\[\\]<>{}?=+#!*«»“”…`´‘’‚‛“”„‟•"·᾿/]+',
                            flags=re.U | re.DOTALL)
    reBadWordform = re.compile(u"^[\\s\\-']*$", flags=re.U | re.I)  # ^[\\s\\-'a-z]*$
    try:
        for path, dirs, files in os.walk(path):
            print u'Processing', path, u';',
            for txt in [os.path.abspath(os.path.join(path, fname))
                        for fname in files if fname.endswith(u'.txt') and
                        u'meta.txt' not in fname and
                        u'concordance' not in fname and
                        u'freq_dict' not in fname and
                        u'sources' not in fname]:
                f = codecs.open(txt, 'r', 'utf-8-sig')
                for line in f:
                    line = line.lower()
                    for wf in reTokenize.split(line):
                        wf = wf.replace(u'-', u' ')
                        if reBadWordform.match(wf):
                            continue
                        concordance[wf] += 1
                        totalWords += 1
                f.close()
            print str(totalWords), u'so far.'
    finally:
        print 'Files read, ' + str(totalWords) + u' words total.'

    f_out = codecs.open('concordance_stats.txt', 'w', 'utf-8')
    xml_out = codecs.open('concordance_xml.txt', 'w', 'utf-8')
    for key, value in sorted(concordance.iteritems(),
                             key=lambda (k, v): (-v, k),
                             reverse=False):
        f_out.write(key + u'\t' + str(value) + u'\r\n')
        xml_out.write(key + u'\r\n')
    f_out.close()
    xml_out.close()


def delete_doubles(filename):
    fIn = codecs.open(filename, 'r', 'utf-8-sig')
    wordsList = set([w.strip(u' \r\n\t-')
                     for w in fIn.readlines()
                     if len(w.strip(u' \r\n\t-')) > 0])
    fIn.close()
    head, end = u"""<?xml version="1.0" encoding="utf-8"?>
<html>
<body>""", u"""</body>
</html>"""
    fOut = codecs.open(filename[:-4] + u'_unique' + filename[-4:], 'w', 'utf-8-sig')
    fOut.write(head + u'\r\n')
    for word in wordsList:
        fOut.write(word + u'\r\n')
    fOut.write(end + u'\r\n')
    fOut.close()


# initial_concordance('C:\\Users\\asus\\PycharmProjects\\academcorpus\\remystem\\text')
delete_doubles(u'concordance_xml.txt')