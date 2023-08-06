from wordlist_eng import wordlist_eng
from pro_guesser import word_score_en
class Wordle:
    def __init__(self):
        self.wordlist = wordlist_eng #List we remove elements from
        self.word_tuple = tuple(self.wordlist) #We wouldn't wanna remove elements from the list we iterate 
        self.count_dict = word_score_en()

    def suggestor(self):
        min_ = [float('inf'),' ']
        for wrd in self.count_dict.keys():
            if self.count_dict[wrd] < min_[0]:
                min_[0] = self.count_dict[wrd]
                min_[1] = wrd
            
        return f'Suggested word: {min_[1]}'

    def solver(self):
        counter = 5
        color_letters = {} #to eliminate the letters we used before we will store the letters which we mark them 'green, yellow, red'
        color_letters['g'] = []
        color_letters['y'] = []
        color_letters['r'] = []
        seen_words = set()
        
        itr = 1 

        while counter > 0:
            
            print(self.suggestor())
            word = input('Word: ')
            colors = input('Color Comb: ')

            if colors == 'eeeee':
                del self.count_dict[word]
                counter += 1 
                itr -= 1
                print(self.suggestor())

            elif colors == 'ggggg':
                print(f'🎉 Congrats well played did it in {itr} enjoy 🎉')
                break

            
            

            for i in range(5): #Creating the dictionary
                if colors[i] == 'g':
                    if word[i] in seen_words:
                        continue
                    else:
                        color_letters['g'].append((i,word[i]))
                        seen_words.add(word[i])
                        

                if colors[i] == 'y':
                    if word[i] in seen_words:
                        continue
                    else:
                        color_letters['y'].append((i,word[i]))
                        seen_words.add(word[i])

                if colors[i] == 'r':
                    if word[i] in seen_words:
                        continue
                    else:
                        color_letters['r'].append((i,word[i]))
                        seen_words.add(word[i])

            for w in self.word_tuple:
                w = w.lower()
                for key in color_letters.keys():
                    if color_letters[key] != []:
                        if key == 'g':
                            for index, letter in color_letters['g']: #color_letters['g'] = [(1,'a'),(2,'b'),(3,'c')]
                                if w[index] != letter and w in self.wordlist and w in self.count_dict.keys(): # after the and part we want to check again if the word still in wordlist 
                                    self.wordlist.remove(w) # if we don't check program will try to remove the same word 
                                    del self.count_dict[w]
                                    break

                        if key == 'r':
                            for index, letter in color_letters['r']:
                                if letter in w and w in self.wordlist and w in self.count_dict.keys():
                                    self.wordlist.remove(w)
                                    del self.count_dict[w]
                                    break
                        
                        if key == 'y':
                            for index, letter in color_letters['y']:
                                if w[index] == letter and w in self.wordlist:
                                    self.wordlist.remove(w)
                                    break
                                elif letter not in w and w in self.wordlist and w in self.count_dict.keys():
                                    self.wordlist.remove(w)
                                    del self.count_dict[w]
                                    break
            
            print(self.wordlist)

            itr += 1
            counter -= 1 

    

    # def another_solver(self):
    #     for i in range(5):
    #         word = input('Word: ')
    #         colors = input('Color combination: ')
    #         for w in self.word_tuple:
    #             for i in range(5):
    #                 if colors[i] == 'r' and word[i] in w:
    #                     self.wordlist.remove(w)
    #                     break

    #                 elif colors[i] == 'g' and word[i] != w[i]:
    #                     self.wordlist.remove(w)
    #                     break

    #                 elif colors[i] == 'y' and word[i] not in w:
    #                     self.wordlist.remove(w)
    #                     break

    #                 elif colors[i] == 'y' and word[i] == w[i]:
    #                     self.wordlist.remove(w)
    #                     break
    #         return self.wordlist


def wordle_eng_runner():
    w = Wordle()
    w.solver()



        



        