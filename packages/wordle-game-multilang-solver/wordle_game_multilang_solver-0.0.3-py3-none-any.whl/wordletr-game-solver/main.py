import wordle_solver, wordle_eng

def welcome():
    print('Welcome to wordle solver..')
    print("Wordle Türkçe Çözer'e hoşgeldiniz..")

    language = input('Choose a language Turkish[tr] or English[en]: ')

    if language == 'tr':
        wordle_solver.wordle_tr_runner()

    if language == 'en':
        wordle_eng.wordle_eng_runner()
        
    if language not in ['tr','en']:
        print('Language not available right now..')


if __name__ == '__main__':
    welcome()




    
    