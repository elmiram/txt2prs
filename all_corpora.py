#-*-coding=utf-8-*-
import os
import codecs
import re
import HTMLParser
from your_corpus import *

# Common Regex
regSpaces1 = re.compile(u' {2,}| +|\t+|&nbsp;| ', flags=re.U | re.DOTALL)
regSpaces2 = re.compile(u'(?: *\r\n)+ *', flags=re.U | re.DOTALL)
regTags = re.compile(u'</?(?:a|img|span|div|p|body|html|head)(?: [^<>]+)?>|[\0⌐-♯]+',
                     flags=re.U | re.DOTALL)
regNonstandardQuotesL = re.compile(u'[“]', flags=re.U | re.DOTALL)
regNonstandardQuotesR = re.compile(u'[”]', flags=re.U | re.DOTALL)
regEndSentence = re.compile(u'(?:[.!?;;]+(?:[)\\]}>/»\r\n]|$)|^\r?\n$|\\\\n)',
                            flags=re.U | re.DOTALL)
regSeparatePunc = re.compile(u'^(.*?([.?!;;]+[)\\]>}»]+)*(\\\\n|[.?!;;])+)(.*)$',
                             flags=re.U | re.DOTALL)
regPuncSpaceL = re.compile(u'^[(\\[<{«-‒–—―]', flags=re.U)
regPuncSpaceR = re.compile(u'[)\\]>}»-‒–—―.,:?!;;%‰‱··]$', flags=re.U)
regDigit = re.compile(u'^(?:[0-9]{1,2}|[0-9][0-9\\-.,]+[0-9][%‰‱]?)$',
                      flags=re.U)

hPrs = HTMLParser.HTMLParser()


class Analysis:

    regGrSplit = re.compile(u'[.,]', flags=re.U)
    
    def __init__(self, lex, gr, transl_en):
        self.lex = lex
        self.grdic, self.gramm = self.separate_gramm(gr)
        self.transl_en = transl_en

    def separate_gramm(self, gr):
        if len(gr) <= 0:
            return u'', u''
        categories = self.regGrSplit.split(gr)
        if len(categories) <= 0:
            return gr, u''
        pos = categories[0]
        grdic = [pos]
        if pos in dictCategories:
            gramm = []
            setGrdic = dictCategories[pos]
            for c in categories[1:]:
                if c in setGrdic:
                    grdic.append(c)
                else:
                    gramm.append(c)
        else:
            gramm = categories[1:]
        return u' '.join(grdic), u' '.join(gramm)

    def __unicode__(self):
        # ATTENTION!! trans is printed two times!! you might need to delete one of them
        return u'\t'.join([self.lex, self.transl_en, self.transl_en, self.grdic,
                           self.gramm, u''])


class Wordform:
    dictAna = {}
    regAnalyses = re.compile(u'<ana[^<>]+></ana>\\s*', flags=re.U)
    regAnalysis = re.compile(u'<ana *lex="([^<>"]+)" *gr="([^<>"]+)" *' +
                             u'(transl_en="([^<>"]+)")?></ana>', flags=re.U)
    
    def __init__(self, token):
        if len(Wordform.dictAna) <= 0:
            self.load_analyses(u'C:\\Users\\asus\\PycharmProjects\\academcorpus\\remystem\\concordance_xml_unique.xml')
        token = token.replace(u'\r\n', u'\\n').replace(u'\n', u'\\n').replace(u'\r', u'').strip()
        self.text = token
        self.grdic = u''
        self.gramm = u''
        self.tokenType = u'wf'
        self.sentencePos = u''
        self.sentno = u''
        self.wordno = u''
        self.lang = u''
        self.graph = u''
        self.nlems = 0
        self.nvars = 0
        self.punctl = u''
        self.punctr = u''

    def define_type(self):
        if regLat.search(self.text):
            self.lang = u'lat'
        elif regDigit.search(self.text):
            self.lang = u'digit'
        if regCaps.search(self.text):
            self.graph = u'caps'
        elif regCap.search(self.text):
            self.graph = u'cap'

    def transform_ana(self, sAna):
        setAna = set(self.regAnalyses.findall(sAna.replace(u'\t', u'')))
        analyses = []
        for ana in setAna:
            m = self.regAnalysis.search(ana)
            if m is None:
                continue
            lex, gr = m.group(1), m.group(2)
            transl_en = u''
            if m.group(3) is not None:
                transl_en = m.group(4)
            analyses.append(Analysis(lex, gr, transl_en))
        return analyses
    
    def load_analyses(self, fname):
        Wordform.dictAna = {}
        f = codecs.open(fname, 'r', 'utf-8-sig')
        regWords = re.compile(u'<w>(<ana.*?/ana>)([^<>]+)</w>',
                              flags=re.U | re.DOTALL)
        text = f.read()
        f.close()
        analyses = regWords.findall(text)
        for ana in analyses:
            word = ana[1].strip(u'-#%*·;·‒–—―•…‘’‚“‛”„‟"\'')
            if len(word) <= 0:
                continue
            ana = self.transform_ana(ana[0])
            if word not in Wordform.dictAna:
                Wordform.dictAna[word] = ana
        print u'Concordance read.'

    def analyze(self):
        self.define_type()
        if self.text in self.dictAna:
            self.analyses = self.dictAna[self.text]
            self.nlems = len(set(ana.lex for ana in self.analyses))
            self.nvars = len(self.analyses)
            return True
        elif self.text.lower() != self.text and\
             self.text.lower() in self.dictAna:
            self.analyses = self.dictAna[self.text.lower()]
            self.nlems = len(set(ana.lex for ana in self.analyses))
            self.nvars = len(self.analyses)
            return True
        else:
            self.analyses = [Analysis(u'', u'', u'')]
            self.nlems = 0
            return False
    
    def xml_clean(self, s):
        return s.replace(u'&', u'&amp;').replace(u'<', u'&lt;').replace(u'>', u'&gt;').replace(u'\'', u'&apos;')

    def __unicode__(self):
        self.analyses.sort(key = lambda ana: (ana.lex, ana.grdic, ana.gramm))
        leftPart = u'\t'.join([unicode(self.sentno), unicode(self.wordno),
                               self.lang, self.graph,
                               self.text, u'', unicode(self.nvars),
                               unicode(self.nlems)]).replace(u'\r\n', u'\\n').replace(u'\n', u'\\n').replace(u'\r', u'')
        rightPart = u'\t'.join([self.punctl, self.punctr, self.sentencePos]).replace(u'\r\n', u'\\n').replace(u'\n', u'\\n').replace(u'\r', u'')
        result = u'\r\n'.join(u'\t'.join([leftPart, unicode(iAna + 1),
                                          unicode(self.analyses[iAna]),
                                          rightPart]).replace(u'\r\n', u'\\n').replace(u'\n', u'\\n').replace(u'\r', u'')
                              for iAna in range(len(self.analyses))) + u'\r\n'
        result = self.xml_clean(result)
        return result


class Text:
    def __init__(self, fname):
        try:
            f = codecs.open(fname, 'r', 'utf-8')
            self.text = f.read()
            f.close()
        except:
            print u'Error when loading text ' + fname
            self.text = u''
        self.wordsCnt = 0
        self.sentsCnt = 0
        self.clean_text()

    def clean_text(self):
        self.convert_html()
        self.clean_spaces()
        self.separate_words()
        self.convert_quotes()
        self.clean_other()

    def convert_html(self):
        self.text = regTags.sub(u'', self.text)  # deletes all tags in angle brackets
        self.text = hPrs.unescape(self.text)  # changes all escaped characters (like &quot;) back to their normal view (like ")

    def clean_spaces(self):
        if u'\r' not in self.text:
            self.text = self.text.replace(u'\n', u'\r\n')
        self.text = regSpaces1.sub(u' ', self.text.strip())  # unify all spaces
        self.text = regSpaces2.sub(u'\r\n ', self.text)  # normalize new lines

    def separate_words(self):
        # punctuation inside a word
        self.text = regPuncWords.sub(u'\\1 \\2', self.text)  # adds a space between punctuation and next letter

    def convert_quotes(self):
        self.text = regQuotesL.sub(u'\\1«\\2', self.text)
        self.text = regQuotesR.sub(u'\\1»\\2', self.text)
        self.text = regNonstandardQuotesL.sub(u'«', self.text)
        self.text = regNonstandardQuotesR.sub(u'»', self.text)

    def clean_other(self):
        self.text = self.text.replace(u'…', u'...')
        self.text = self.text.replace(u'\\', u'/')
        # print self.text

    def get_word_r(self, iWf):
        """Finds the first word in self.wfs after the item with index iWf."""
        for i in range(iWf + 1, len(self.wfs)):
            if self.wfs[i].tokenType == u'wf':
                return self.wfs[i]
        return None
    
    def tokenize(self):
        self.rawTokens = self.text.split(u' ')
        self.wfs = []
        wordsAnalyzed = 0
        totalWords = 0
        for token in self.rawTokens:
            if len(token) <= 0:
                continue
            m = regTokenSearch.search(token)
            if m is None:
                if token in u'\r\n':
                    self.wfs.append(Wordform(u'\r\n'))
                    self.wfs[-1].tokenType = u'punc'
                elif len(token) > 0:
                    self.wfs.append(Wordform(token))
                    self.wfs[-1].analyze()
                continue
            puncl = Wordform(m.group(1))
            wf = Wordform(m.group(2))
            puncr = Wordform(m.group(3))
            if len(puncl.text) > 0:
                self.wfs.append(puncl)
                self.wfs[-1].tokenType = u'punc'
            if wf.text in u'\r\n':
                wf.text = u'\r\n'
                self.wfs.append(wf)
                self.wfs[-1].tokenType = u'punc'
            elif len(wf.text) > 0:
                self.wfs.append(wf)
                totalWords += 1
                bAnalyzable = self.wfs[-1].analyze()
            if bAnalyzable:
                wordsAnalyzed += 1
            if len(puncr.text) > 0:
                self.wfs.append(puncr)
                self.wfs[-1].tokenType = u'punc'
        self.wordsCnt = totalWords
        return totalWords, wordsAnalyzed

    def split_sentences(self):
        prevWord = None
        sentno = 1
        wordno = 1
        firstWord = self.get_word_r(-1)
        firstWord.sentencePos = u'bos'
        for iWf in range(len(self.wfs)):
            wf = self.wfs[iWf]
            if wf.tokenType == u'punc' and\
               regEndSentence.search(wf.text) is not None:
                wordR = self.get_word_r(iWf)
                if prevWord is not None and\
                   wordR is not None and len(wordR.text) > 0 and\
                   (wordR.text[0].isupper() or wordR.text[0].isdigit()) and\
                   (prevWord.text not in abbrs and (len(prevWord.text) > 1 or\
                    prevWord.text.islower())):
                    if prevWord.sentencePos == u'':
                        prevWord.sentencePos = u'eos'
                    wordR.sentencePos = u'bos'
                    wordno = 1
                    sentno += 1
            elif wf.tokenType == u'wf':
                wf.sentno = sentno
                wf.wordno = wordno
                wordno += 1
                prevWord = wf
        self.sentsCnt = sentno

    def separate_punc(self, punc):
        m = regSeparatePunc.search(punc)
        if m is None:
            return punc, punc
        return self.add_space_to_punc(m.group(1)),\
               self.add_space_to_punc(m.group(4))

    def add_space_to_punc(self, punc):
        if regPuncSpaceL.search(punc):
            punc = u' ' + punc
        if regPuncSpaceR.search(punc):
            punc += u' '
        return punc
    
    def add_punc(self):
        """Adds punctuation to the words."""
        prevPunc = u''
        prevWord = None
        for wf in self.wfs:
            if wf.tokenType == u'wf':
                if prevWord is not None and\
                   (prevWord.sentno != wf.sentno or u'\\n' in prevPunc):
                    punc1, punc2 = self.separate_punc(prevPunc)
                else:
                    prevPunc = self.add_space_to_punc(prevPunc)
                    punc1, punc2 = prevPunc, prevPunc
                if prevWord is not None:
                    prevWord.punctr = punc1
                wf.punctl = punc2
                prevWord = wf
                prevPunc = u''
            elif wf.tokenType == u'punc':
                prevPunc += wf.text.replace(u'\'', u'’')
        if prevWord is not None:
            prevWord.punctr = prevPunc

    def process(self):
        totalWords, wordsAnalyzed = self.tokenize()
        self.split_sentences()
        self.add_punc()
        return totalWords, wordsAnalyzed

    def write_out(self, fname, docid, meta):
        f = codecs.open(fname, 'w', 'utf-8-sig')
        write_meta(f, fname, docid, meta, self.wordsCnt, self.sentsCnt)
        for wf in self.wfs:
            if wf.tokenType == u'wf':
                f.write(unicode(wf))
        f.close()


class Corpus:
    def __init__(self):
        self.meta = {}
        
    def process_dir(self, dirname, outdirname, restricted=None):
        if restricted is None:
            restricted = []     # directories to be omitted
        restricted = set(restricted)
        totalWords = 1
        wordsAnalyzed = 0
        docid = 1
        for root, dirs, files in os.walk(dirname):
            curdirnames = set(re.findall(u'[^/\\\\]+', root, flags=re.U))
            if len(curdirnames & restricted) > 0:
                print u'Skipping ' + root
                continue
            print u'Processing %s : currently %s words, %s%% parsed.' % (root, totalWords, wordsAnalyzed * 100.0 / totalWords)
            for fname in files:
                if not fname.endswith(u'.txt') or fname == u'meta.txt' or\
                   u'concordance' in fname or u'freq_dict' in fname:
                    continue
                fname = os.path.join(root, fname)
                t = Text(fname)
                curWords, curAnalyzed = t.process()  #
                totalWords += curWords
                wordsAnalyzed += curAnalyzed
                
                # write the output to the output directory,
                # change the extension to .prs
                fnamePrs = fname[:-4] + u'.prs'
                fnamePrs = re.sub(u'^[^/\\\\]+([/\\\\])', outdirname + u'\\1',
                                  fnamePrs)
                fnamePrs = fnamePrs.replace(u'\'', u'_').replace(u'"', u'_')
                outPath = os.path.dirname(fnamePrs)
                if not os.path.exists(outPath):
                    os.makedirs(outPath)
                t.write_out(fnamePrs, docid, self.meta)
                docid += 1
        return totalWords, wordsAnalyzed


c = Corpus()
c.meta = load_meta(u'academmeta.txt')
totalWords, wordsAnalyzed = c.process_dir(u'text', u'parsed_texts_2014.03',
                                          [u'dirs', u'thatAreNotToBe', u'searched'])
print u'The texts have been processed,', totalWords, u'words total,',\
      wordsAnalyzed * 100.0 / totalWords, u'% analyzed.'
