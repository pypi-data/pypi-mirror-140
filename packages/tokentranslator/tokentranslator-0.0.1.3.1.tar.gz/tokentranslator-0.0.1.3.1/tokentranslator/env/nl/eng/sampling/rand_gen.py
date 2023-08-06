# TODO: generalize:
from tokentranslator.env.equation.sampling.eq_sampling import EqSampling
from tokentranslator.env.nl.eng.data.terms.rand.patterns._list import terms_gens as rand_terms_gens


class SamplingEng(EqSampling):
    
    def __init__(self, net):
        self.net = net

    def sampling_vars_eng(self):
        self.sampling_vars(rand_terms_gens)

    def show_sampled(self):
        print(self.net.tree.flatten('rand_eng'))
