#!/usr/bin/env python

class Node:
    def __init__(self):
        self.word = None
        self.norm = None
        self.nodes = {}
        
    def __get_all__(self):
        x = []
        
        for key, node in self.nodes.iteritems() : 
            if(node.word is not None):
                x.append(node.word)
            
            x += node.__get_all__()
                
        return x
    
    def __str__(self):
        return str(self.word)
    
    def __insert__(self, word, lineno, norm, string_pos = 0):
        current_letter = word[string_pos]
  
        if not self.nodes.has_key(current_letter):
            self.nodes[current_letter] = Node();

        if(string_pos + 1 == len(word)):
            self.nodes[current_letter].word = lineno
            self.nodes[current_letter].norm = norm
        else:
        	self.nodes[current_letter].__insert__(word, lineno, norm, string_pos + 1)
            
    	return True
    
    def __get_all_with_prefix__(self, prefix, string_pos):
        x = []
        
        for key, node in self.nodes.iteritems() : 
            if(string_pos >= len(prefix) or key == prefix[string_pos]):
            	if(node.word is not None):
                	x.append(node.word)
                    
                if(node.nodes != {}):
                    if(string_pos + 1 <= len(prefix)):
                        x += node.__get_all_with_prefix__(prefix, string_pos + 1)
                    else:
            			x += node.__get_all_with_prefix__(prefix, string_pos)
    
        return x       

    def search(self, word):
        length = 0
        iterator = self.nodes
        while length < len(word):
            if iterator.has_key(word[length]):
                if length == len(word) - 1:
                    return iterator[word[length]].word, iterator[word[length]].norm
                iterator = iterator[word[length]].nodes
                length += 1
            else:
                return False
        return False

class Trie:
    def __init__(self):
        self.root = Node()
        
    def insert(self, word, lineno, norm):
        self.root.__insert__(word, lineno, norm)
        
    def get_all(self):
        return self.root.__get_all__()

    def get_all_with_prefix(self, prefix, string_pos = 0):
        return self.root.__get_all_with_prefix__(prefix, string_pos)

    def search(self, word):
        return self.root.search(word)

def test():
    trie = Trie()
    trie.insert("go", 1, 2)
    trie.insert("gone", 2, 2)
    trie.insert("gi", 3, 2)
    trie.insert("cool", 4, 2)
    trie.insert("comb", 5, 2)
    trie.insert("grasshopper", 6, 2)
    trie.insert("home", 7, 2)
    trie.insert("hope", 8, 2)
    trie.insert("hose", 9, 2)
    trie.insert(" ", 9, 11)

    print str(trie.root.nodes['g'].nodes['o'])
    print str(trie.root.nodes['g'].nodes['i'])
    print str(trie.root.nodes['c'].nodes['o'].nodes['o'].nodes['l'])
    print "\n"

    print "print all words to make sure they are all there: "
    print trie.get_all()
    print "\n"

    print "print out all the words with the given prefixes: "
    print trie.get_all_with_prefix("g")
    print trie.get_all_with_prefix("go")
    print trie.get_all_with_prefix("co")
    print trie.get_all_with_prefix("hom")
    print trie.get_all_with_prefix("gr")
    print trie.search("gone")
    print trie.search("abc")

#test()
