import os

path = 'outputs/'

def parse_line(line):
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


def writeToFile(listt, fp):
    fp.write(listt[0].encode('ascii', 'ignore') + ":")
    for each in listt[1]:
        fp.write("_" + str(each))
        for doc in listt[1][each]:
            fp.write("|" + str(doc[0])+ "," + str(doc[1]))
    fp.write('\n')

def writ(word, number, fp):
    fp.write(word.encode('ascii', 'ignore') + ":")
    fp.write(number)
    fp.write('\n')

def get_it(listit):
    send = []
    count = 0
    champ_max = 60
    length = len(listit)
    while (count < length) and (count < champ_max):
        send.append(listit[count])
        count += 1
    return send, length
        
def readfile(filename):
    fpw = open('files/' + 'champ', 'w')
    fpw2 = open('files/' + 'words', 'w')
    champ_max = 30
    with open(filename) as f1:
        line = f1.readline()
        while line != '':
            counter = 0
            dic = {}
            data = parse_line(line)
            if data[1].has_key('b'):
                dic['b'], it = get_it(data[1]['b'])
                counter += it
            if data[1].has_key('t'):
                dic['t'], it = get_it(data[1]['t'])
                counter += it
            if data[1].has_key('l'):
                dic['l'], it = get_it(data[1]['l'])
                counter += it
            if data[1].has_key('i'):
                dic['i'], it = get_it(data[1]['i'])
                counter += it
            if data[1].has_key('r'):
                dic['r'], it = get_it(data[1]['r'])
                counter += it
            if data[1].has_key('c'):
                dic['c'], it = get_it(data[1]['c'])
                counter += it
        
            writeToFile([data[0], dic], fpw)
            writ(data[0], str(counter), fpw2)
            line = f1.readline()

    fpw.close()
    fpw2.close()

def cmonow():
    files = os.listdir('outputs/')
    readfile('outputs/' + files[0])

if __name__ == "__main__":
    cmonow()
