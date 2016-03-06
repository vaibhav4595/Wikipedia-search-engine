#!/usr/bin/python

import xml.sax
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from collections import defaultdict, Counter
from math import sqrt
import re
import gc
import operator
import multiprocessing as mp
import sys
import merger

porter=PorterStemmer()
doclist = []
stopword = stopwords.words('english')
procs = mp.cpu_count()
process_queue = mp.Queue()
workers = []
#qwert = open('files/pagemap.txt', 'w')
#qwert2 = open('files/normap.txt', 'w')

pagemap = {}
#normap = {}

class tempDocs:
    def __init__(self, idd, title, text):
        self.idd = idd
        self.text = text
        self.title = title

def get_refs(text):
    results = re.search('== References ==(.*?)==', text, re.DOTALL)
    if results is not None:
        return results.group(1).strip()
    else:
        return "Norefs"

def get_links(text):
    results = re.search('==External links==(.*?)\n\n', text, re.DOTALL)
    if results is not None:
        return results.group(1).strip()
    else:
        return "Nolinks"

def get_categories(text):
    results = re.findall('\[\[Category:(.*?)\]\]', text)
    if results is not None:
        return results
    else:
        return "Nocategories"

def get_infobox(text):
    results = re.search('{{Infobox(.*?)}}', text, re.DOTALL)
    if results is not None:
        return results.group(1).strip()
    else:
        return "Noinfobox"

def tokenize(text, title):
    if len(text.split('== References ==')) > 1:
        extra = '== References ==' + text.split('== References ==')[1]
        newtext = text.split('== References ==')[0]
        categories = get_categories(extra)
        links = get_links(extra)
        refs = get_refs(extra)
    else:
        newtext = text
        categories = get_categories(newtext)
        links = get_links(newtext)
        refs = "Norefs"

    infobox = get_infobox(newtext)
    if infobox != "Noinfobox":
        infobox.lower()
        infobox = re.sub(r'[^a-z0-9 ]',' ', infobox)

    if refs != "Norefs":
        refs = refs.lower()
        refs = re.sub(r'[^a-z0-9 ]',' ', refs)

    if links != "Nolinks":
        links = links.lower()
        links = re.sub(r'[^a-z0-9 ]',' ', infobox)

    newtext.lower()
    newtext = re.sub(r'[^a-z0-9 ]',' ', newtext)
    newtext = newtext.split()
        
    newtext = [x for x in newtext if x not in stopword]
    newtext = [porter.stem(word) for word in newtext]

    title.lower()
    title = re.sub(r'[^a-z0-9 ]',' ', title)
    title = title.split()
    title = [x for x in title if x not in stopword]
    title = [porter.stem(word) for word in title]

    cats = []
    for each in categories:
        listit = each.lower()
        sendit = re.sub(r'[^a-z0-9 ]',' ', listit)
        sendit = [porter.stem(word) for word in listit]
        for every in sendit:
            cats.append(every)

#    return newtext, links, refs, categories, infobox, title
    return newtext, links, refs, cats, infobox, title

class PageHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.CurrentTag = ""
        self.flag = 0
        self.text = ""
        self.title = ""
        self.idd = ""
        self.count = 0
        self.currentDoc = ""

    def startElement(self, tag, attributes):
        self.CurrentTag = tag
        if tag == "page":
            self.count += 1
            self.flag = 0
            #print "Processing page ", self.count

    def endElement(self, tag):
        if tag == "page":
            tt = tempDocs(self.idd.strip(), self.title.strip(), self.text)
            pagemap[int(self.idd.strip())] = self.title.strip()
            process_queue.put(tt)
            self.idd = ""
            self.text = ""
            self.title = ""

    def characters(self, content):
        if self.CurrentTag == "title":
            self.title += content
        elif self.flag == 0 and self.CurrentTag == "id":
            self.idd = content
            self.flag = 1
        elif self.CurrentTag == "text":
            self.text += content

def normaliser(dic):
    sumit = 0
    for each in dic:
        sumit += (dic[each] * dic[each])
    return sqrt(sumit)

def process_in_memory(process_queue, data_queue):
    while (1):
        currentDoc = process_queue.get()
        if currentDoc == "DONE":
            process_queue.put("DONE")
            data_queue.put("DONE")
            return True

#        pagemap = p_queue.get()
#        normap = n_queue.get()

        newtext, links, refs, categories, infobox, title = tokenize(currentDoc.text, currentDoc.title)
#        pagemap[currentDoc.idd]  = currentDoc.title
#        qwert.write(currentDoc.idd.encode('ascii', 'ignore') + ":")
#        qwert.write(currentDoc.title.encode('ascii', 'ignore') + ":")
#        qwert.write('\n')

        cnt_words = Counter()
        cnt_links = Counter()
        cnt_references = Counter()
        cnt_categories = Counter()
        cnt_infobox = Counter()
        cnt_title = Counter()

#        normap[currentDoc.idd] = {}

        for words in title:
            cnt_title[words] += 1
#        norm = normaliser(cnt_title)
#        normap[currentDoc.idd]['t'] = norm
#        qwert2.write(currentDoc.idd.encode('ascii', 'ignnore') + ':')
#        qwert2.write('t,' + str(norm) + ';')

        for words in newtext:
            cnt_words[words] += 1
#        norm = normaliser(cnt_words)
#        normap[currentDoc.idd]['b'] = norm
#        qwert2.write('b,' + str(norm) + ';')

        if categories != "Nocategories":
            for words in categories:
                cnt_categories[words] += 1
        else:
            cnt_categories = {}
#        if cnt_categories != {}:
#            norm = normaliser(cnt_categories)
#            normap[currentDoc.idd]['c'] = norm
#            qwert2.write('c,' + str(norm) + ';')

        if infobox != "Noinfobox":
            for words in infobox:
                cnt_infobox[words] += 1
        else:
            cnt_infobox = {}
#        if cnt_infobox != {}:
#            norm = normaliser(cnt_infobox)
#            normap[currentDoc.idd]['i'] = norm
#            qwert2.write('i,' + str(norm) + ';')

        if links != "Nolinks":
            for words in links:
                cnt_links[words] += 1
        else:
            cnt_links = {}
#        if cnt_links != {}:
#            norm = normaliser(cnt_links)
#            normap[currentDoc.idd]['l'] = norm
#            qwert2.write('l,' + str(norm) + ';')

        if refs != "Norefs":
            for words in refs:
                cnt_references[words] += 1
        else:
            cnt_references = {}
#        if cnt_references != {}:
#            norm = normaliser(cnt_references)
#            normap[currentDoc.idd]['r'] = norm
#            qwert2.write('r,' + str(norm) + ';')

#        qwert2.write('\n')

        further_combine = {}
        further_combine['id'] = currentDoc.idd
        further_combine['title'] = cnt_title
        further_combine['text'] = cnt_words
        further_combine['r'] = cnt_references
        further_combine['c'] = cnt_categories
        further_combine['i'] = cnt_infobox
        further_combine['l'] = cnt_links

        data_queue.put(further_combine)
#        n_queue.put(normap)
#        p_queue.put(pagemap)

def writeToFile(filename, index):
    fp = open('outputs/' + filename, 'w')
    sortedlist = sorted(index.keys())
    for word in sortedlist:
    #for word in index:
        if index[word].has_key('b'):
            index[word]['b'].sort(key=operator.itemgetter(1), reverse=True)
        if index[word].has_key('i'):
            index[word]['i'].sort(key=operator.itemgetter(1), reverse=True)
        if index[word].has_key('l'):
            index[word]['l'].sort(key=operator.itemgetter(1), reverse=True)
        if index[word].has_key('r'):
            index[word]['r'].sort(key=operator.itemgetter(1), reverse=True)
        if index[word].has_key('t'):
            index[word]['t'].sort(key=operator.itemgetter(1), reverse=True)
        if index[word].has_key('c'):
            index[word]['c'].sort(key=operator.itemgetter(1), reverse=True)
            
        fp.write(word.encode('ascii', 'ignore') + ":")
        for each in index[word]:
            fp.write("_" + each)
            for doc in index[word][each]:
                fp.write("|" + str(doc[0])+ "," + str(doc[1]))
        fp.write("\n")
    fp.close()

def writeToFilee(filename, wordIndex):

    fp = open(filename, 'w')
    for each in wordIndex.keys():
        string = ""
        string = string + each + '|'

        if wordIndex[each].has_key('b'):
            temp = "b;"
            lister = wordIndex[each]['b']
            length = len(lister)
            for index in xrange(0, length - 1):
                temp = temp + str(lister[index][0]) + ':' + str(lister[index][1]) + ','
            temp = temp + str(lister[length - 1][0]) + ':' + str(lister[length - 1][1])
            string = string + temp + ';'

        if wordIndex[each].has_key('c'):
            temp = "c;"
            lister = wordIndex[each]['c']
            length = len(lister)
            for index in xrange(0, length - 1):
                temp = temp + str(lister[index]) + ','
            temp = temp + str(lister[length - 1])
            string = string + temp + ';'

        if wordIndex[each].has_key('t'):
            temp = "t;"
            lister = wordIndex[each]['t']
            length = len(lister)
            for index in xrange(0, length - 1):
                temp = temp + str(lister[index]) + ','
            temp = temp + str(lister[length - 1])
            string = string + temp + ';'

        if wordIndex[each].has_key('r'):
            temp = "r;"
            lister = wordIndex[each]['r']
            length = len(lister)
            for index in xrange(0, length - 1):
                temp = temp + str(lister[index][0]) + ':' + str(lister[index][1]) + ','
            temp = temp + str(lister[length - 1][0]) + ':' + str(lister[length - 1][1])
            string = string + temp + ';'

        if wordIndex[each].has_key('i'):
            temp = "i;"
            lister = wordIndex[each]['i']
            length = len(lister)
            for index in xrange(0, length - 1):
                temp = temp + str(lister[index][0]) + ':' + str(lister[index][1]) + ','
            temp = temp + str(lister[length - 1][0]) + ':' + str(lister[length - 1][1])
            string = string + temp + ';'

        if wordIndex[each].has_key('l'):
            temp = "l;"
            lister = wordIndex[each]['l']
            length = len(lister)
            for index in xrange(0, length - 1):
                temp = temp + str(lister[index][0]) + ':' + str(lister[index][1]) + ','
            temp = temp + str(lister[length - 1][0]) + ':' + str(lister[length - 1][1])
            string = string + temp + ';'

        string += '\n'
        fp.write(string)
    fp.close()

def merger_in_memory(data_queue, index, filename):
    filecounter = 0
    count = 0
    gc.disable()
    while(1):
        data = data_queue.get()
        if data == "DONE":
            count += 1
            if count == (procs - 1):
                writeToFile(filename + '_' + str(filecounter), index)
                filecounter += 1
                return True

        else:
            doc = data['id']
            title = data['title']
            text = data['text']
            r = data['r']
            c = data['c']
            i = data['i']
            l = data['l']

            for each in title:
                if index.has_key(each):
                    if index[each].has_key("t"):
                        index[each]["t"].append((doc, title[each]))
                    else:
                        index[each]["t"] = [(doc, title[each])]
                else:
                    index[each] = {}
                    index[each] = {"t": [(doc, title[each])]}

            for each in text:
                if index.has_key(each):
                    if index[each].has_key('b'):
                        index[each]['b'].append((doc, text[each]))
                    else:
                        index[each]['b'] = [(doc, text[each])]
                else:
                    index[each] = {}
                    index[each]['b'] = [(doc, text[each])]


            for each in l:
                if index.has_key(each):
                    if index[each].has_key('l'):
                        index[each]['l'].append((doc, text[each]))
                    else:
                        index[each]['l'] = [(doc, text[each])]
                else:
                    index[each] = {}
                    index[each]['l'] = [(doc, text[each])]
           
            for each in r:
                if index.has_key(each):
                    if index[each].has_key('r'):
                        index[each]['r'].append((doc, text[each]))
                    else:
                        index[each]['r'] = [(doc, text[each])]
                else:
                    index[each] = {}
                    index[each]['r'] = [(doc, text[each])]

            for each in i:
                if index.has_key(each):
                    if index[each].has_key('i'):
                        index[each]['i'].append((doc, text[each]))
                    else:
                        index[each]['i'] = [(doc, text[each])]
                else:
                    index[each] = {}
                    index[each]['i'] = [(doc, text[each])]

            for each in c:
                if index.has_key(each):
                    if index[each].has_key('c'):
                        index[each]['c'].append((doc, text[each]))
                    else:
                        index[each]['c'] = [(doc, text[each])]
                else:
                    index[each] = {}
                    index[each]['c'] = [(doc, text[each])]

            if len(index.keys()) > 40000:
                writeToFile(filename + '_' + str(filecounter), index)
                index = {}
                filecounter += 1

    gc.enable()


def writepagemap():
    fp1 = open('files/' + 'pagemap.txt', 'w')
#    fp2 = open('files/' + 'normap.txt', 'w')
#    print pagemap
#    print normap
    filer = 0
    sortedlist = sorted(pagemap.keys())
    for each in sortedlist:
        ty = str(each)
        fp1.write(ty.encode('ascii', 'ignore') + ":")
        fp1.write(pagemap[each].encode('ascii', 'ignore'))
        fp1.write('\n')
        filer += 1
#        string = ''
#        for every in normap[each].keys():
#            string = string + every + ',' + str(normap[every]) + ';'
#        fp2.write(each.encode('ascii', 'ignore') + ":")
#        fp2.write(string)
#        fp2.write('\n')
    fp1.close()
    fp2 = open('files/' + 'info.txt', 'w')
    fp2.write(str(filer))
    fp2.write('\n')
    fp2.close()
#    fp2.close()

def main():
#    pagemap = {}
#    normap = {}
    if len(sys.argv) != 3:
        exit(1)
    index = {}

    data_queue = mp.Queue()
#    n_queue = mp.Queue()
#    p_queue = mp.Queue()
#    n_queue.put({})
#    p_queue.put({})
    c = mp.Process(target=merger_in_memory, args=(data_queue, index, sys.argv[2],))
    c.start()

    for w in xrange(procs - 1):
        p = mp.Process(target=process_in_memory, args=(process_queue, data_queue,))
        p.start()
        workers.append(p)

    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = PageHandler()
    parser.setContentHandler(Handler)
    parser.parse(sys.argv[1])

    process_queue.put("DONE")
    for w in workers:
        w.join()
    c.join()
    
    writepagemap()

if __name__ == '__main__':
    main()
    merger.divideandrule()
