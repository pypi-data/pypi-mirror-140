
new_txt = open('five_letter_words.txt','w')

with open('/Users/user/Desktop/wordletr/words/kelime-listesi.txt') as f:
    for line in f:
        line = line.strip()

        if len(line.split()) > 1:
            continue

        if len(line) == 5:
            new_txt.writelines(line+'\n')

