from curses.ascii import isalpha
from wordlist import wordlist
from wordlist_eng import wordlist_eng
import string

tr_alpha = 'a b c ç d e f g ğ h i ı j k l m n o ö p r s ş t u ü v y z'
tr_alpha_list = tr_alpha.split(' ')

tr_alpha_dict = {}
eng_alpha_dict = {}

for letter in string.ascii_lowercase:
    eng_alpha_dict[letter] = [0,0,0,0,0]

for letter in tr_alpha_list:
    tr_alpha_dict[letter] = [0,0,0,0,0]


def tr_alpha_occur():
    for word in wordlist:
        for index, letter in enumerate(word):
            if letter in tr_alpha_dict.keys():
                tr_alpha_dict[letter][index] += 1 

    return tr_alpha_dict

def eng_alpha_occur():
    for word in wordlist_eng:
        for index, letter in enumerate(word):
            if letter in eng_alpha_dict.keys():
                eng_alpha_dict[letter][index] += 1 

    return eng_alpha_dict

tr_freq = tr_alpha_occur()
eng_freq = eng_alpha_occur()

def word_score_tr():
    words = {}
    max_freq = [0 for i in range(5)]

    for letter in tr_freq:
        if isalpha(letter) == False:
            continue
        for i in range(0, 5):
            if max_freq[i] < tr_freq[letter][i]:
                max_freq[i] = tr_freq[letter][i]
    
    for word in wordlist:
        score = 1 
        for i in range(0,5):
            c = word[i]
            if isalpha(c) != True:
                continue
            score *= 1 + (tr_freq[c][i] - max_freq[i]) ** 2 
        words.update({word:score})
    

    possible_words = dict(sorted(words.items(), key=lambda item: item[1]))
    return possible_words

def word_score_en():
    words = {}
    max_freq = [0 for i in range(5)]

    for c in eng_freq:
        for i in range(5):
            if max_freq[i] < eng_freq[c][i]:
                max_freq[i] = eng_freq[c][i]
    for w in wordlist_eng:
        score = 1 
        for i in range(5):
            c = w[i]
            score *= 1 + (eng_freq[c][i] - max_freq[i]) ** 2 
        words.update({w:score})
    
    return words 








