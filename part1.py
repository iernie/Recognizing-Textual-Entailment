
def word_matching(text, entailment):
    words = text.split()
    hwords = entailment.split()
    intext = 0
    for h in hwords:
        if h in words:
            intext += 1

    return float(intext) / len(hwords)
