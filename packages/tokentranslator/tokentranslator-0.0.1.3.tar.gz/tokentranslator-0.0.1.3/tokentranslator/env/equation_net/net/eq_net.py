from tokentranslator.translator.tree.maps import map_tree, map_tree_postproc, flatten

import logging

# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
logger = logging.getLogger('equation.tree')

# if using directly uncoment that:
'''
# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('equation')
logger.setLevel(level=log_level)
'''


class NetEditor():
    def __init__(self, net):

        self.net = net
        
    def map_out(self, replacer):

        '''Add out to self.eq_net (from self.parse)'''

        _map = map_tree(str(['s']), replacer)
        _map_postproc = map_tree_postproc(_map, replacer)
        return(_map_postproc)

    def flatten(self, key, replacer=None):
        '''     
        Example 0:
        >>> e = Equation('sin(x+y)')
        >>> e.parser.parse()
        >>> from tokentranslator.env.equation_net.data.terms.output.sympy.replacer_sympy import SympyGen
        >>> gen = SympyGen()
        >>> gen.set_parsed_net()
        >>> gen.set_mid_replacers(e.parser.mid_replacers)
        >>> e.net_editor.map_out(gen)
        >>> # here net_editor is linked to eq_net.py
        >>> e.net_editor.flatten('sympy', gen)
        ['sympy.sin(', 'x', '+', 'y', ')']

        Example 1:
        >>> from tokentranslator.env.equation_net.equation import Equation

        >>> e = Equation('sin(x+y)')
        >>> e.parser.parse()

        >>> from tokentranslator.translator.sampling.vars.vars_extractor import Extractor
        >>> import tokentranslator.translator.sampling.vars.vars_maps as vms
        >>> vars_extractor = Extractor("eqs")
        >>> net_vars = vms.get_args(str(['s']), e.net_out, vars_extractor)  
        >>> vms.subs(e.net_out, net_vars,x=3.14)

        >>> from tokentranslator.env.equation_net.data.terms.output.sympy.replacer_sympy import SympyGen
        >>> gen = SympyGen()
        >>> gen.set_parsed_net(e.net_out)
        >>> gen.set_mid_replacers(e.parser.mid_replacers)
        >>> e.net_editor.map_out(gen)
        
        # here net_editor is linked to eq_net.py
        >>> e.net_editor.flatten('values', gen)
        ['sympy.sin(', 3.14, '+', 'y', ')']

        Example 2:
        # see run function below.
        '''

        if replacer is None:
            # use any available:
            replacer = self.net.replacer.cpp.gen
        out = flatten(replacer, str(['s']), replacer.get_extractor(key))
        return(out)


def run():

    '''Run flatten with external extractor'''

    from tokentranslator.env.equation_net.equation import Equation

    e = Equation('sin(x+y)')
    e.parser.parse()
    from tokentranslator.translator.sampling.vars.vars_extractor import Extractor
    import tokentranslator.translator.sampling.vars.vars_maps as vms
    vars_extractor = Extractor("eqs")
    net_vars = vms.get_args(str(['s']), e.net_out, vars_extractor)
    vms.subs(e.net_out, net_vars, x=3.14)
    
    from tokentranslator.env.equation_net.data.terms.output.sympy.replacer_sympy import SympyGen
    gen = SympyGen()
    gen.set_parsed_net(e.net_out)
    gen.set_mid_replacers(e.parser.mid_replacers)
   
    def extractor_sympy_val(self, node_idd):
        # here self is point to replacer
        # (gen in that case)

        # out = self.get_var_val(node_idd)
        
        node = self.get_node(node_idd)
        try:
            data = node["data"]["vars"]['self']['val']
            out = data
        except (KeyError, TypeError):
            out = self.extractor_sympy(node_idd)
        return(out)

    extractor = gen.make_extractor(extractor_sympy_val)
    # return(extractor)
    e.net_editor.map_out(gen)
    replacer = gen
    out = flatten(replacer, str(['s']), extractor)
    # here net_editor is linked to eq_net.py
    # out = e.net_editor.flatten('values', gen)
    print(out)
