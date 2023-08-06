from tokentranslator.nltk import pos_tag
from tokentranslator.translator.tokenizer.words import Word


class Tokenizer():

    def lex(self, sent):

        sent = sent.split()
        tags = pos_tag(sent)
        
        return([Word(tag.lower(), [word, None, tag.lower()])
                for (word, tag) in tags])
