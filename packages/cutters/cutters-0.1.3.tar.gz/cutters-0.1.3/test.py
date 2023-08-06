import cutters

text = """
Pravilnika o proračunskom računovodstvu i računskom planu ("Narodne novine" 119/2001, 74/2002 i 3/2004), otplata primljenih kratkoročnih zajmova i amortizacija kratkoročnih vrijednosnih papira izvrπena u istoj proraËunskoj godini iskazuje se u neto iznosu, tj. kao umanjeno zaduženjem, a ne u stavci otplata.,
"""

sentences = cutters.cut(text, "hr")

# print(sentences[4].quotes[0].sentences[0])
print(sentences)

# for sentence in sentences:
# print(f"Sentence: {sentence.str}")
# for quote in sentence.quotes:
# print(f"Quote: {quote.str}")
# for quote_sentence in quote.sentences:
# print(f"Quote sentence: {quote_sentence}")
