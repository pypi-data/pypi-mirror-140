import random
from tokentranslator.env.nl.eng.data.terms.tokens._list import tokens

terms_gens = dict([(key, lambda lkey=key: random.choice(tokens[lkey].split()))
                   for key in tokens])

