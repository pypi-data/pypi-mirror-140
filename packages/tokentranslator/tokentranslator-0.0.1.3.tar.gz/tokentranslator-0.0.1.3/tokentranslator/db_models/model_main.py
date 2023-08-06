'''This class is extention of BaseDB for some specific task.
It contain methods that cannot be generalised, they are specific
for task environmant.
'''
# parser$ ~/anaconda3/bin/python3 -m db_models.model_main

# import peewee as pw
from datetime import date

from tokentranslator.db_models.model_base import BaseDB
from tokentranslator.db_models.model_tables import gen_tokens_table
from tokentranslator.db_models.model_tables import gen_users_table


class TokenizerDB(BaseDB):

    '''
    db consist from one dialect table,
    composed from the entries.

    each entry must be:
    (term_name, template, grammar_type, pattern_type)
    where
       template
          either re or txt or ex template.

       grammar_type type is list like one of thats:

          ('br_left', [True, False, False])
          ('br_right', [True, False, False])
          ('br_mid', [False, True, False])
          ('a',)

       pattern_type is list like one of thats:

          ('re', [+ order])
          ('txt', [+ order])
          ('ex',)

          where order is optional pattern order.

    Examples:

        ('let', r"Let(${defs}in:${clauses}",
        ('br_left', [True, True, False]),
        ('txt',)

        ('func', r"${{pred}}\(${args}",
        ('br_left', [True, False, False]),
        ('re', 6.1))

        # x, xs, normal_form_0
        ('var', r"(?P<obj>[a-z|_|0-9]+)", ('a'),
        ('re', 2)),

        ('eq', "Eq(${eqs})Eq",
        ('a',), ('ex',)),
    '''
    def __init__(self, dialect_name="eqs", new=False):
        
        BaseDB.__init__(self, dialect_name, new)

    def create_dialect_db(self):
        BaseDB.create_db(self, [gen_tokens_table,
                                gen_users_table],
                         "tokens")

    def create_users_table(self):
       
        try:
            self.tables_dict
        except AttributeError:
            self.tables_dict = {}

        users_table = self.load_table(gen_users_table)
        self.create_db_tables(users_table)

    def create_model_table(self):

        try:
            self.tables_dict
        except AttributeError:
            self.tables_dict = {}

        model_table = self.load_table(gen_tokens_table)
        self.create_db_tables(model_table)

    def load_all_tables(self):

        BaseDB.load_tables(self, [gen_tokens_table,
                                  gen_users_table])

    def clear_all_entries_dialect(self):
        self.clear_all_entries(self.tables_dict["tokens"])

    def set_entries_from_list(self, input_list):
        table = self.tables_dict["tokens"]
        self.clear_all_entries(table)
    
        for entry in input_list:
            self.add_pattern({"term_name": entry[0],
                              "template": entry[1],
                              "grammar_type": entry[2],
                              "pattern_type": entry[3]})

    def get_entries_to_list(self, silent=True):

        '''Extract all entries in list,
        acceptable by ``parser_general``'''

        entries = self.show_all_entries(silent=True)
        # (idx, term_name, template, grammar_type,
        #                 pattern_type, created_date)
        out_list = []
        for entry in entries:
            if not silent:
                print(entry)
            out_list.append((entry["term_name"], entry["template"],
                             eval(entry["grammar_type"]),
                             eval(entry["pattern_type"])))
        
        '''
        out_list = [(entry["term_name"], entry["template"],
                     eval(entry["grammar_type"]), eval(entry["pattern_type"]))
                    for entry in entries]
        '''
        return(out_list)

    def show_all_entries(self, table_name="tokens", silent=False):

        out = BaseDB.show_all_entries(self, table_name=table_name,
                                      silent=silent)
        return(out)

    def fill_dialect_db(self):
        
        db = self.db
        table = self.tables_dict["tokens"]

        db.connect()

        # create entry:
        table.create(term_name="let",
                     template=r"Let(${defs}in:${clauses}",
                     grammar_type="('br_left', [True, True, False])",
                     pattern_type="('txt',)")
        # expirydate=date(2100, 1, 1)

        db.close()
        
    def add_pattern(self, entry):
        
        '''
        - ``entry`` -- entry dict to be added in db.
        see descrition above.
        (see BaseDB.add_table_entry)

        Examples:

        entry = {"term_name": "let",
                 "template": r"Let(${defs}in:${clauses}",
                 "grammar_type": ('br_left', [True, True, False]),
                 "pattern_type": ('txt',)}
        '''
                      
        table = self.tables_dict["tokens"]

        if "created_date" in entry:
            entry.pop("created_date")

        self.add_table_entry(table, entry)

    def select_pattern(self, term_name):
        '''
        Select with term_name.
        (see BaseDB.select_table_entry)
        '''
        table = self.tables_dict["tokens"]
        res = self.select_table_entry(table, 'term_name', term_name)

        # for compatibility:
        class Res():
            def __init__(self, res):
                self.res = res
                self.count = len(res)
        return(Res(res))

    def edit_pattern(self, term_name, props):
        '''
        Edit  properties of pattern's with term_name.
        (see BaseDB.edit_table_entry)
        '''
        table = self.tables_dict["tokens"]
        if "created_date" in props:
            props.pop("created_date")

        self.edit_table_entry(table, 'term_name', term_name,
                              props)

    def del_pattern(self, term_name):
        '''
        Delete pattern with term_name.
        (see ``BaseDB.del_table_entry``)
        '''
        table = self.tables_dict["tokens"]
        self.del_table_entry(table, 'term_name', term_name)


def change_eqs(dialect):
    model = TokenizerDB()

    if dialect == "tex":
        model.change_eqs_to_tex()
    elif dialect == "wolfram":
        model.change_eqs_to_wolfram()
    else:
        raise(Exception("dialect must be either tex or wolfram"))


def test_create():

    print("\ntest create db")

    agent = TokenizerDB()
    agent.create_dialect_db()
    agent.fill_dialect_db()

    agent.add_pattern({"term_name": "func",
                       "template": r"${{pred}}\(${args}",
                       "grammar_type": ('br_left', [True, False, False]),
                       "pattern_type": ('re', 6.1)})
                      
    # sin, abelian, a:
    agent.add_pattern({"term_name": "pred",
                       "template": r"(?P<obj>\w+)",
                       "grammar_type": ('part',),
                       "pattern_type": ('re',)})

    agent.edit_pattern("pred", {"grammar_type": ('a',)})

    agent.del_pattern("pred")
    
    agent.show_all_entries()

    return(agent)


def test_load():

    print("\ntest load tables")

    agent = TokenizerDB()
    agent.load_all_tables()
    
    agent.show_all_entries()

    return(agent)


def test_change_path():

    print("\ndialect_name = eqs:")
    dialect_name = "eqs"
    agent = TokenizerDB(dialect_name)
    agent.show_all_entries()
    print("\ncurrent dialect path:")
    print(agent.get_path_of_dialect_db(dialect_name))

    print("\ndialect_name changed to cs:")
    dialect_name = "cs"
    agent.change_dialect_db(dialect_name)
    agent.show_all_entries()
    print("\ncurrent dialect path:")
    print(agent.get_path_of_dialect_db(dialect_name))


def test_from_list(dialect_name):

    '''Cleare all entries and fill them from tables'''

    agent = TokenizerDB(dialect_name=dialect_name)
    agent.load_all_tables()
    
    if dialect_name == "eqs":
        from tokentranslator.translator.tokenizer.patterns.patterns_list\
                            .tests.dialects import eqs as dialect
    elif dialect_name == "cs":
        from tokentranslator.translator.tokenizer.patterns.patterns_list\
                            .tests.dialects import cs as dialect
    else:
        raise(BaseException("no such dialect"))

    agent.set_entries_from_list(dialect)
    agent.show_all_entries()


def test_to_list(dialect_name):

    '''Transform to list for ``parser_general``'''
    agent = TokenizerDB(dialect_name=dialect_name)
    agent.load_all_tables()
    
    out_list = agent.get_entries_to_list()
    print("\nout_list:")
    print(out_list)
    return(out_list)


def test_select():

    print("\ntest select:")

    agent = test_load()
    res = agent.select_pattern("let")
    
    print("\nresults count:")
    print(res.count)

    return(agent)


def test_create_user_table():

    agent = TokenizerDB()
    agent.create_users_table()
    data = {
        "username": "admin",
        "is_admin": True,
        "password": "13",
        "email": "email"}
    agent.create_new_user(data)
    userexist = agent.check_user_exist(data)
    print("\nuserexist:")
    print(userexist)

    checkuser = agent.check_user(data)
    print("\ncheckuser:")
    print(checkuser)

    agent.show_all_entries(table_name="user")

    
def test_show_all_entries_user():
    agent = TokenizerDB()
    agent.load_all_tables()
    agent.show_all_entries(table_name="user")


def run():
    # path = "env/equation_net/data/terms/input/demo_dialect.db"
    # path = "env/clause/data/terms/input/demo_dialect.db"
    dialect_name = "eqs"
    # test_create()
    # test_create_user_table()
    ### test_load()
    test_select()
    # test_show_all_entries_user()
    # test_change_path()

    ### test_to_list(dialect_name)
    # test_from_list(path, "cs")


if __name__ == '__main__':

    import sys
    if "-eqs_to_tex" in sys.args:
        change_eqs("tex")
    elif "-eqs_to_wolfram" in sys.args:
        change_eqs("wolfram")
    else:
        # run tests
        run()
