import os
import shutil

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

def readfile(filename):
    fp = open(filename, 'r')
    for each in fp.readlines():
        word, dic = parse_lines(each.strip())
        print word, dic


def writeToFile(listt, fp):
    fp.write(listt[0].encode('ascii', 'ignore') + ":")
    for each in listt[1]:
        fp.write("_" + str(each))
        for doc in listt[1][each]:
            fp.write("|" + str(doc[0])+ "," + str(doc[1]))
    fp.write('\n')

def smallermerger(key, data1, data2):
    list1 = []
    list2 = []
    newlist = []
    if data1[1].has_key(key):
        list1 = data1[1][key]
    if data2[1].has_key(key):
        list2 = data2[1][key]
    count1, count2 = 0, 0
    len1, len2 = len(list1), len(list2)
    while (count1 < len1) and (count2 < len2):
        if list1[count1][1] > list2[count2][1]:
            newlist.append(list1[count1])
            count1 += 1
        else:
            newlist.append(list2[count2])
            count2 += 1
    if count1 < len1:
        while count1 < len1:
            newlist.append(list1[count1])
            count1 += 1
    if count2 < len2:
        while count2 < len2:
            newlist.append(list2[count2])
            count2 += 1

    return newlist

def mergerinto(filename1, filename2, writeinto):
    flag = None
    fp = open(writeinto, 'w')
    with open(filename1, 'r') as f1, open(filename2, 'r') as f2:
        line1 = f1.readline()
        data1 = parse_line(line1)
        line2 = f2.readline()
        data2 = parse_line(line2)

        while (line1 != '') and (line2 != ''):
            if data1[0] < data2[0]:
                writeToFile(data1, fp)
                line1 = f1.readline()
                data1 = parse_line(line1)
                flag = 1
            elif data1[0] > data2[0]:
                writeToFile(data2, fp)
                line2 = f2.readline()
                data2 = parse_line(line2)
                flag = 2
            elif data1[0] == data2[0]:
                newdic = {}
                lister = smallermerger('b', data1, data2)
                if lister != []:
                    newdic['b'] = lister
                lister = smallermerger('r', data1, data2)
                if lister != []:
                    newdic['r'] = lister
                lister = smallermerger('i', data1, data2)
                if lister != []:
                    newdic['i'] = lister
                lister = smallermerger('l', data1, data2)
                if lister != []:
                    newdic['l'] = lister
                lister = smallermerger('t', data1, data2)
                if lister != []:
                    newdic['t'] = lister
                lister = smallermerger('c', data1, data2)
                if lister != []:
                    newdic['c'] = lister
                writeToFile([data1[0], newdic], fp)
                line1 = f1.readline()
                line2 = f2.readline()
                data1 = parse_line(line1)
                data2 = parse_line(line2)

        if line1 != '':
            while line1 != '':
                writeToFile(data1, fp)
                line1 = f1.readline()
                data1 = parse_line(line1)
        if line2 != '':
            while line2 != '':
                writeToFile(data2, fp)
                line2 = f2.readline()
                data2 = parse_line(line2)
    fp.close()

def divideandrule():
    level = 1
    files = os.listdir('outputs/')
    length = len(files)
    while length != 1:
        if length % 2 == 0:
            counter = 0
            while counter < length:
                filename1 = 'outputs/' + files[counter]
                filename2 = 'outputs/' + files[counter + 1]
                filetowrite = 'outputs/' + str(level) + 'level' + str(counter)
                mergerinto(filename1, filename2, filetowrite)
                counter += 2
        else:
            counter = 0
            while counter < length - 1:
                filename1 = 'outputs/' + files[counter]
                filename2 = 'outputs/' + files[counter + 1]
                filetowrite = 'outputs/' + str(level) + 'level' + str(counter)
                mergerinto(filename1, filename2, filetowrite)
                counter += 2
            shutil.copy('outputs/' + files[counter], 'outputs/' + str(level) + 'level' + str(counter))

        tempfiles = os.listdir('outputs/')
        files = []
        for each in tempfiles:
            if each.startswith(str(level)):
                files.append(each)
            else:
                os.remove('outputs/' + each)
        length = len(files)
        level += 1
            
#mergerinto('outputs/cmon_19', 'outputs/cmon_20')
