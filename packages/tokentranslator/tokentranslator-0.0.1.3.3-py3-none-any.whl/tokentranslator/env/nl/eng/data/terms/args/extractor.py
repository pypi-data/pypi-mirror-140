from tokentranslator.env.nl.eng.replacer.replacer import GenEng

import logging

# create logger
log_level = logging.INFO  # logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger('extractor.py')
logger.setLevel(level=log_level)


class ArgsGen(GenEng):
    
    def __init__(self):
        self.args = []

    def translate_brackets(self, node_br):
 
        pass

    def translate(self, node):

        try:
            node.args
        except AttributeError:
            logger.debug("no args for node:")
            logger.debug(self.get_term_value(node))
            self.get_args(node)

        args_exist = [arg for arg in self.args
                      if node.args['id'] == arg['id']]
        if len(args_exist) > 0:
            arg_exist = args_exist[0]
            arg_exist['nodes'].append(node)
        else:
            self.args.append({'id': node.args['id'], 'nodes': [node]})
        
    def postproc(self, node):
        pass
    
