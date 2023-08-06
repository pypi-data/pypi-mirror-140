# from translator.grammar.grammars import gm_to_cnf
from tokentranslator.env.nl.eng.data.grammars.grammars import eng_grammar
from tokentranslator.translator.grammar.cyk import cyk

from tokentranslator.env.nl.eng.parser.tokenizer import Tokenizer

from tokentranslator.translator.tree.tree_converter import convert
# from translator.tree.nodes import NodeCommon


class Parser():
    
    def __init__(self, net):
        self.net = net
        self.tokenizer = Tokenizer()
        
    def parse(self):
        sent = self.net.sent
        self.from_lex = self.tokenizer.lex(sent)
        
        # transform grammar to cnf:
        # grammar_cnf = gm_to_cnf(gm_pow_f_args)  # grammar_pow_f
        grammar_cnf = eng_grammar
        goal_sent = self.from_lex
        p, t = cyk(goal=goal_sent, grammar=grammar_cnf)
        self.from_cyk = (p, t)
        self.net.sent_tree = t

        # convert parse tree to operator's tree:
        # ot = convert(t)
        # self.operator_tree = ot

    def show_lex(self):
        print(self.from_lex)

    def show_cyk(self):
        print(self.net.sent_tree)

    def show_ot(self):
        print(self.operator_tree)
