from tokentranslator.env.nl.eng.parser.parser_main import Parser
from tokentranslator.env.nl.eng.args.args_main import Args
from tokentranslator.env.nl.eng.tree.tree_main import LangTree
from tokentranslator.env.nl.eng.sampling.rand_gen import SamplingEng

import logging

# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
# logger = logging.getLogger('equation.tree')
 
# if using directly uncoment that:

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('lang')
logger.setLevel(level=log_level)


class Eng():
    def __init__(self, sent, trace=0):

        self.parser = Parser(self)
        self.tree = LangTree(self)
        self.args_editor = Args(self)
        
        # selr.replacer = Replacer(self)
        self.sampling = SamplingEng(self)

        self.sent = sent

    def show_original(self):
        print(self.sent)

