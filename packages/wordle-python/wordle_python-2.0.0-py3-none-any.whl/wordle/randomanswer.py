from wordle.dictionary import words
from datetime import datetime as dt
import random
import math

UNIX_reference = 1645678800
jumbled_words = random.shuffle(words)

def random_answer(daily: bool):
    if daily == True:
        UNIX = dt.now().timestamp()
        iteration = int(math.floor((UNIX - UNIX_reference)/86400000))
        return jumbled_words[iteration]