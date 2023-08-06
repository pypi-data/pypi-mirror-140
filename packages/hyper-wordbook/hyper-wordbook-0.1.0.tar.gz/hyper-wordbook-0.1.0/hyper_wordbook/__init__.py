__version__ = '0.1.0'

import os
import threading

loading = None

def f():
    import time
    while loading == True:
        print("Loading")
        time.sleep(0.05)
        os.system("clear")

F = threading.Thread(target = f)

try:
    import nltk
except:
    loading = True
    F.start()
    os.system("pip install nltk")
    loading = False
    
nltk.download("words", quiet = True)

def dictionary():
    x = []
    for i in nltk.corpus.words.words():
        x.append(i.lower())
    return x

def dictionaryfile(file_name):
    x = []
    file = open(file_name, "a")
    for i in nltk.corpus.words.words():
        x.append(i.lower())
    for o in x:
        file.write(o)
        file.write("\n")
    file.close()

def wordsize(word_size):
    x = []
    for i in nltk.corpus.words.words():
        if len(i) == word_size:
            x.append(i.lower())
    return x

def wordstart(start_of_word):
    sow = start_of_word.lower()
    x = []
    for i in nltk.corpus.words.words():
        if i.lower()[0] == sow:
            x.append(i.lower())
    return x