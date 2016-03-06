#!/usr/bin/env python

from trie import Trie
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import operator
import re
import math

porter = PorterStemmer()
file1 = 'files/words'
file2 = 'files/pagemap.txt'
file3 = 'files/info.txt'
file4 = 'files/champ'

majordict = {'b' : 0.4, 't' : 0.4, 'i' : 0.05, 'l' : 0.05, 'r' : 0.025, 'c' : 0.075}
stopword = stopwords.words('english')

def parse_main_line(line):
    if line == '':
        return False

    temp = line.split(':')
    word = temp[0]
    list2 = temp[1].split('_')
    dic = {}
    for i in xrange(1, len(list2)):
        temp2 = list2[i].split('|')
        cat = temp2[0]
        dic[cat] = []
        for i in xrange(1, len(temp2)):
            temp3 = temp2[i].split(',')
            add = (int(temp3[0]), int(temp3[1]))
            dic[cat].append(add)
    return [word, dic]

def result(query, trie, totaldocs, fpointer, line_offset, pagedict):
    query.lower()
    query = re.sub(r'[^a-z0-9 ]', ' ', query)
    query = query.split()
    query = [x for x in query if x not in stopword]
    query = [porter.stem(word) for word in query]

    lister = []
    for each in query:
        result = trie.search(each)
        if result != False:
            lister.append([each, result[0], result[1]])
    
    if len(lister) == 0:
        return False

    docdic = {}
    for each in lister:
        lineno = each[1]
        count = 0
        with open(file4, 'r') as fp:
            while count < lineno:
                count += 1
                line = fp.readline()
            line = fp.readline()
#        fpointer.seek(0)
#        fpointer.seek(line_offset[lineno])
#        line = fpointer.readline()
        data = parse_main_line(line)
#        print data
        idf = math.log((totaldocs / each[2]), 2)
#        print each[0], idf
        for key in data[1].keys():
            for tups in data[1][key]:
                if docdic.has_key(tups[0]):
                    docdic[tups[0]] += (majordict[key] * tups[1] * idf)
                else:
                    docdic[tups[0]] = (majordict[key] * tups[1] * idf)

    sorted_list = sorted(docdic.items(), key=operator.itemgetter(1), reverse=True)
    count = 0
    length = len(sorted_list)
    while (count < 10) and (count < length):
        if pagedict.has_key(sorted_list[count][0]):
            print pagedict[sorted_list[count][0]], ':', sorted_list[count][0]
        count += 1
            
def result2(query, trie, totaldocs, pagedict):
    listind = []
    for i in xrange(0, len(query)):
        if query[i] == ':':
            listind.append(i)

    keysfound = []
    for each in listind:
        if majordict.has_key(query[each - 1]):
           keysfound.append(query[each - 1])

    if len(keysfound) != 0:
        normaliser = 1.0 / len(keysfound)
    else:
        normaliser = 1.0

    docdic = {}
    for i in xrange(0, len(keysfound)):
        mainkey = keysfound[i]
        string = ''
        start = listind[i] + 1
        c = query[start]
        while (c != ':') and (start != len(query)):
            c = query[start]
            start += 1
            
        if c == ':':
            start -= 2

        for j in xrange(listind[i] + 1, start):
            string += query[j]

        string.lower()
        string = re.sub(r'[^a-z0-9 ]', ' ', string)
        string = string.split()
        string = [x for x in string if x not in stopword]
        string = [porter.stem(word) for word in string]

        lister = []
        for each in string:
            result = trie.search(each)
            if result != False:
                lister.append([each, result[0], result[1]])
    
        for each in lister:
            lineno = each[1]
            count = 0
            with open(file4, 'r') as fp:
                while count < lineno:
                    count += 1
                    line = fp.readline()
                line = fp.readline()
            data = parse_main_line(line)
            idf = math.log((totaldocs / each[2]), 2)
            for key in data[1].keys():
                if key == mainkey:
                    for tups in data[1][key]:
                        if docdic.has_key(tups[0]):
                            docdic[tups[0]] += (0.6 * tups[1] * idf)
                        else:
                            docdic[tups[0]] = (0.6 * tups[1] * idf)
                else:
                    for tups in data[1][key]:
                        if docdic.has_key(tups[0]):
                            docdic[tups[0]] += (normaliser * tups[1] * idf)
                        else:
                            docdic[tups[0]] = (normaliser * tups[1] * idf)


    sorted_list = sorted(docdic.items(), key=operator.itemgetter(1), reverse=True)
    count = 0
    length = len(sorted_list)
    while (count < 10) and (count < length):
        if pagedict.has_key(sorted_list[count][0]):
            print pagedict[sorted_list[count][0]]
        count += 1

def parse_line(line):
    data = line.split(':')
    if data[0] == '':
        data[0] = ' '
    data[1] = float(data[1])
    return data
    
def main():
    trie = Trie()
    counter = 0
    print "Constructing tries in memory .. wait"
    with open(file1, 'r') as fp1:
        line = fp1.readline()
        while line != '':
            data = parse_line(line.strip())
            trie.insert(data[0], counter, data[1])
            line = fp1.readline()
            counter += 1
    
    print "Contructing for id to page title mapping .. wait"
    pagedict = {}
    with open(file2, 'r') as fp1:
        line = fp1.readline()
        while line != '':
            data = line.strip().split(':')
            data[0] = int(data[0])
            pagedict[data[0]] = data[1]
            line = fp1.readline()

    fp = open(file3)
    lines = float(fp.readlines()[0].strip())
    totaldocs = lines

    print "Constructing offsets for fast champion list reading"
    line_offset = []
#    with open(file4, 'r') as fp4:
#        offset = 0
#        line = fp4.readline()
#        while line != '':
#            line_offset.append(offset)
#            offset += len(line)
#            line = fp4.readline()

#    fpointer = open(file4, 'r')
    fpointer = None
    print "Done --- now you can start querying"
    x = None
    while x != 'exit()':
        print ">>", 
        x = raw_input()
        if ':' in x:
            processed = result2(x, trie, totaldocs, pagedict)
        else:
            processed = result(x, trie, totaldocs, fpointer, line_offset, pagedict)

if __name__ == "__main__":
    main()
