from wordle.dictionary import words
from datetime import datetime as dt
import random
import math

UNIX_reference = 1645678800
jumbled_words = random.sample(words, len(words))

def random_answer(daily: bool):
    """Picks a random answer every day."""
    if daily == True:
        UNIX = dt.now().timestamp()
        iteration = int(math.floor((UNIX - UNIX_reference)/86400000))
        return jumbled_words[iteration]