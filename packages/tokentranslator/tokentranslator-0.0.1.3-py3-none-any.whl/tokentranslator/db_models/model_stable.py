from tokentranslator.db_models.model_signatures import SignaturesDB

from functools import reduce
from collections import OrderedDict


class ModelStable():
    def __init__(self):
        self.db = SignaturesDB()
        self.db.load_all_tables()

    def get_stable(self):

        '''return dict lile:
        {"subgroup": [(True, False, True),
         (False, True, True), ...]}'''

        res_list = self.db.show_all_entries(silent=True)

        def succ(acc, entry):
            predicate = entry['predicate']
            signature = entry['signature']
            if predicate not in acc:
                acc[predicate] = [signature]
            else:
                acc[predicate].append(signature)
            return(acc)
        return(reduce(succ, res_list, OrderedDict()))

    def has_predicate(self, predicate):
        res = self.db.select_predicate(predicate, silent=True)
        if res.count > 0:
            return(True)
        else:
            return(False)

    def has_signature(self, predicate, signature):
        print("signature, type signature:")
        print(signature, type(signature))
        print("predicate, type predicate:")
        print(predicate, type(predicate))
        
        res = self.db.select_pattern(predicate, signature, silent=True)
        if res.count > 0:
            return(True)
        else:
            return(False)

    def get_signatures(self, predicate):
        res = self.db.select_predicate(predicate, silent=True)
        return([entry['signature'] for entry in res.res])

    def get_data(self, predicate, signature):
        res = self.db.select_pattern(predicate, signature, silent=True)
        if res.count > 1:
            raise(BaseException("predicate, signature pair not unique"))
        return(res.res[0])


def test0():
    model = ModelStable()
    print("\nmodel.get_stable:")
    print(model.get_stable())

    print('\nmodel.has_predicate("subgroup"):')
    print(model.has_predicate("subgroup"))

    print('\nmodel.has_predicate("sleep"):')
    print(model.has_predicate("sleep"))
    
    print('\nmodel.has_signature("subgroup", str((True, False, True))):')
    print(model.has_signature("subgroup", str((True, False, True))))
    
    print('\nmodel.has_signature("sleep", str((True, False, True))):')
    print(model.has_signature("sleep", str((True, False, True))))

    print('\nmodel.get_signatures("subgroup"):')
    print(model.get_signatures("subgroup"))

    print('\nmodel.get_data("subgroup", str((True, False, True))):')
    print(model.get_data("subgroup", str((True, False, True))))


def run():
    test0()


if __name__ == '__main__':
    test0()
