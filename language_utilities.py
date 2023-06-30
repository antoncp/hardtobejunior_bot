def choose_noun_case(score, word):
    ending = ''
    remainder = score % 10
    if remainder >= 5 or remainder == 0:
        ending = 'ов'
    elif 1 < remainder < 5:
        ending = 'a'
    return f'{score} {word}{ending}'

