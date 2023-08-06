from pathlib import Path
wordlist_eng = []

path = str(Path.cwd()) + '/words/wordle_eng.txt'


with open(path) as f:
            for line in f:
                line.strip()
                line.lower()
                actual_line = line.split()

                if len(actual_line) > 1:
                    pass

                if len(line) == 6:
                    wordlist_eng.append(line.strip())