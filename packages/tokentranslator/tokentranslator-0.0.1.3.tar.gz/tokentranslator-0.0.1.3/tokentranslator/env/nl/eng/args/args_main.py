from tokentranslator.env.nl.eng.data.terms.args.extractor import ArgsGen


class Args():

    def __init__(self, net):
        self.net = net

    def get_vars(self):

        '''Extract variables from arguments.
        Variable is tokens ie lower case.
        (ex: nns, vbp ...).
        It also add var key to args.'''
        
        try:
            self.net.args
        except AttributeError:
            self.get_args()

        self.net.vars = []

        for arg in self.net.args:
            # alternatives:
            # if arg['id']['name'] not is None
            # 
            if arg['id']['term_id'].islower():
                arg['variable'] = {'name': arg['id']['term_id'],
                                   'value': arg['id']['name']}
                for node in arg['nodes']:
                    node.args['variable'] = arg['variable']
                self.net.vars.append(arg)
    
    def get_args(self):
        # TODO
        gen = ArgsGen()
        self.net.tree.map_out(gen)
        self.net.args = gen.args

    def show_args(self):
        print(self.net.args)

    def show_vars(self):
        print(self.net.vars)
