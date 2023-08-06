from tokentranslator.translator.tree.maps import map_tree, map_tree_postproc

import logging

# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
logger = logging.getLogger('lang.tree')

# if using directly uncoment that:
'''
# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('equation')
logger.setLevel(level=log_level)
'''


class LangTree():
    def __init__(self, net):

        self.net = net
        
    def map_out(self, replacer):

        '''Add out to self.eq_tree (from self.parse)'''

        _map = map_tree(self.net.sent_tree, replacer)
        _map_postproc = map_tree_postproc(_map, replacer)

        return(_map_postproc)

    def flatten(self, key):

        '''Return list of term as key.
        Key either original or cpp.
        Flatten is only work after map_*'''
        kernel = self.net.sent_tree

        logger.debug("kernel[0]")
        logger.debug(kernel[0])
        
        out_kernel = kernel.flatten(key, non_br_forward=True)
        logger.debug("out_kernel")
        logger.debug(out_kernel)

        return(" ".join(out_kernel))
