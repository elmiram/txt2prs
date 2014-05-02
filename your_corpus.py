#-*-coding=utf-8-*-

u"""
Здесь собраны ф-ции и переменные, которые должны подгоняться под корпус.
"""

import re
import codecs


# Corpus Specific Regex

regLat = re.compile(u'^[a-zA-Z]+$', flags=re.U)
regCaps = re.compile(u'^[A-ZА-ЯЁ]+$', flags=re.U)  # WORD
regCap = re.compile(u'^[A-ZА-ЯЁ]', flags=re.U)  # Word
regPuncWords = re.compile(u'([.,!?:;·;·\\)\\]>/])([A-Za-zА-ЯЁа-яё(\\[<{«])',
                          flags=re.U | re.DOTALL|re.I)  # punctuation inside a word
regTokenSearch = re.compile(u'^([^A-Za-zА-ЯЁа-яё0-9]*)' +\
                            u'([0-9,.\\-%]+|' +\
                            u'[A-Za-zА-ЯЁа-яё0-9\\-\'`´‘’‛/@.,]+?)' +\
                            u'([^A-Za-zА-ЯЁа-яё0-9]*)$',
                            flags=re.U | re.DOTALL)
regQuotesL = re.compile(u'([\\s(\\[{<\\-])"([A-Za-zА-ЯЁа-яё0-9\\-\'`´‘’‛@.,-‒–—―•])',
                        flags=re.U | re.DOTALL)
regQuotesR = re.compile(u'([A-Za-zА-ЯЁа-яё0-9\\-\'`´‘’‛/@.,-‒–—―•.,!?:;·;·])"([\\s)\\]}>\\-.,!])',
                        flags=re.U | re.DOTALL)

# Corpus Defined Variables

abbrs = {u'т', u'д', u'п', u'г', u'е', u'ч', u'л', u'н', u'тыс'}
# для сокращений и т.д., и т.п., т.е., 2014 г., в т.ч., какой-л., какой-н.
dictCategories = {u'S': {u'm', u'f', u'n', u'persn', u'famn', u'inan', u'anim', u'bastard'}}

# Corpus Defined Functions

# Загрузка метатаблицы.
# Аргумент функции - путь к файлу с метатаблицей.
# Функция возвращает словарь, где каждый ключ - имя файла без расширения, значение - массив с метаданными.
def load_meta(fname):
    meta = {}
    fMeta = codecs.open(fname, 'r', 'utf-8-sig')
    for line in fMeta:
        # try:
        line = line.strip('\r\n')
        metaFilename, metaAuthor, metaTitle, metaYears, metaGenre, metaGender, metaMajor, metaCourse, metaTerm, metaModule, metaDomain, metaLevel, metaTimeLimit, metaUnivCode, metaStudCode, metaIssue = line.split(u'\t')
        if metaFilename.lower().endswith(u'.txt'):  # Отрезаем расширение
            metaFilename = metaFilename[:-4]
        if u'-' not in metaYears:
            metaYear1 = metaYears
            metaYear2 = metaYears
        else:  # Делим временной промежуток типа "2000 - 2001" на две части: год начала, год окончания.
            metaYear1, metaYear2 = metaYears.split(u'-', 2)
        # Записываем все метаданные в словарь: ключ - имя файла, значение - массив со всеми метаданными.
        meta[metaFilename.lower()] = [metaAuthor, metaTitle,
                                           metaYear1, metaYear2,
                                           metaGenre, metaGender,
                                           metaMajor, metaCourse,
                                           metaTerm, metaModule,
                                           metaDomain, metaLevel,
                                           metaTimeLimit, metaUnivCode,
                                           metaStudCode, metaIssue]
        # except:
        #     print u'Wrong meta line: ' + line
    fMeta.close()
    print u'Meta read, ' + str(len(meta)) + u' entries.'
    return meta

# Записываем метаданные в prs-файл.
# Должен быть код, который ходит по заданной папке, читает хмл-файлы, считает в них кол-во предложений, кол-во слов, открывает файл прс с соответсвующим названием, а потом из этого кода вызывается функция write_meta.
# Аргументы функции: открытый файл (объект), имя файла (без расширения), номер файла (просто по порядку), словарь с метатаблицей, кол-во слов, кол-во предложений.
# Функция просто записывает в файл метаданные.
def write_meta(f, fname, docid, meta, wordsCnt, sentsCnt):
    f.write(u'#sentno\t#wordno\t#lang\t#graph\t#word\t#indexword\t'
            u'#nvars\t#nlems\t#nvar\t#lem\t#trans\t#trans_ru\t#lex\t#gram\t#flex\t'
            u'#punctl\t#punctr\t#sent_pos\r\n')
    m = re.match(u'^(?:.*\\\\)?([^\\\\]*?)\\.[^\\\\]+$', fname)
    fnameStripped = m.group(1).lower()
    f.write(u'#meta.docid\t' + str(docid) + u'\r\n')
    date_displayed = u'–'
    if fnameStripped in meta:
        f.write(u'#meta.author\t' + meta[fnameStripped][0] + u'\r\n')
        f.write(u'#meta.title\t' + meta[fnameStripped][1] + u'\r\n')
        f.write(u'#meta.date1\t' + meta[fnameStripped][2] + u'\r\n')
        f.write(u'#meta.date2\t' + meta[fnameStripped][3] + u'\r\n')
        f.write(u'#meta.genre\t' + meta[fnameStripped][4] + u'\r\n')
        f.write(u'#meta.gender\t' + meta[fnameStripped][5] + u'\r\n')
        f.write(u'#meta.major\t' + meta[fnameStripped][6] + u'\r\n')
        f.write(u'#meta.course\t' + meta[fnameStripped][7] + u'\r\n')
        f.write(u'#meta.term\t' + meta[fnameStripped][8] + u'\r\n')
        f.write(u'#meta.module\t' + meta[fnameStripped][9] + u'\r\n')
        f.write(u'#meta.domain\t' + meta[fnameStripped][10] + u'\r\n')
        f.write(u'#meta.level\t' + meta[fnameStripped][11] + u'\r\n')
        f.write(u'#meta.time-limit\t' + meta[fnameStripped][12] + u'\r\n')
        f.write(u'#meta.university-code\t' + meta[fnameStripped][13] + u'\r\n')
        f.write(u'#meta.student-code\t' + meta[fnameStripped][14] + u'\r\n')
        f.write(u'#meta.issue\t' + meta[fnameStripped][15] + u'\r\n')
        if meta[fnameStripped][2] == meta[fnameStripped][3]:
            date_displayed = meta[fnameStripped][2]
        else:
            date_displayed = meta[fnameStripped][2] + u'–' + meta[fnameStripped][3]
    else:
        f.write(u'#meta.author\t–\r\n')
        f.write(u'#meta.title\t–\r\n')
        f.write(u'#meta.date1\t2011\r\n')
        f.write(u'#meta.date2\t2014\r\n')
        f.write(u'#meta.genre\t\r\n')
        f.write(u'#meta.gender\t\r\n')
        f.write(u'#meta.major\t\r\n')
        f.write(u'#meta.course\t\r\n')
        f.write(u'#meta.term\t\r\n')
        f.write(u'#meta.module\t\r\n')
        f.write(u'#meta.domain\t\r\n')
        f.write(u'#meta.level\t\r\n')
        f.write(u'#meta.time-limit\t\r\n')
        f.write(u'#meta.university-code\t\r\n')
        f.write(u'#meta.student-code\t\r\n')
        f.write(u'#meta.issue\t\r\n')
    f.write(u'#meta.words\t' + str(wordsCnt) + u'\r\n')
    f.write(u'#meta.sentences\t' + str(sentsCnt) + u'\r\n')
    f.write(u'#meta.date_displayed\t' + date_displayed + u'\r\n')


