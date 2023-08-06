from tokentranslator.translator.replacer.replacer import Gen

import logging

# create logger
log_level = logging.INFO  # logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger('replacer.py')
logger.setLevel(level=log_level)


class GenEng(Gen):
    def __init__(self):
        pass

    def get_term_id(self, node):

        '''Get term id from node'''
        
        try:
            term_id = node.name.lex[-1]
        except AttributeError:
            term_id = str(node.name)
        return(term_id)

    def get_term_value(self, node):
        try:
            term_value = node.name.lex[0]
        except AttributeError:
            term_value = None
        return(term_value)
