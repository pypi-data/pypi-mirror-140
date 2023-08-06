'''This class is extention of BaseDB for some specific task.
It contain methods that cannot be generalised, they are specific
for task environmant.
'''
# ~/anaconda3/envs/etokentranslator/bin/./python3 -c "import tokentranslator.db_models.model_examples as ts;ts.run()"

# import peewee as pw
from datetime import date

from tokentranslator.db_models.model_base import BaseDB

from tokentranslator.db_models.model_tables import gen_examples_sampler_table
from tokentranslator.db_models.model_tables import gen_examples_parser_eqs_table
from tokentranslator.db_models.model_tables import gen_examples_parser_cs_table


class ExamplesDB(BaseDB):

    '''
    db for examples of parser eqs, cs and sampler.

    Examples:

    # for eqs:
    entry = {"id": 0,
             "input": r"sin(x)",
             "comment": "",
             "net": '',
             "cpp": "sin((Block0OffsetX+idxX*DX))",
             "sympy": 'sympy.sin(x)',
             "vars": 'x'}
    '''
    def __init__(self, dialect_name, new=False):
    
        self.supported_tables_names = ["examples_sampler",
                                       "examples_parser_eqs",
                                       "examples_parser_cs"]
        if dialect_name not in self.supported_tables_names:
            self.raise_error(dialect_name)

        # here ``dialect_name`` it used for main table,
        # all methods of this class work with:
        self.table_name = dialect_name

        # and here ``dialect_name`` used for path config file key:
        BaseDB.__init__(self, dialect_name, new)
    
    def show_all_entries(self, silent=False):

        '''except code'''

        # out = BaseDB.show_all_entries(self, table_name=table_name,
        #                               silent=silent)

        db = self.db
        table_name = self.table_name

        table = self.tables_dict[table_name]

        table_field_names = table._meta.sorted_field_names
        if not silent:
            print("\n table_sorted_field_names: %s" % (table_field_names))

        # sqlite do not support "_":
        qs = db.execute_sql("select * from %s"
                            % (table_name.replace("_", ""),))
        if not silent:
            print("\n %s db entries:" % table_name)
        out = []
        for q in qs:
            if not silent:
                print(q)
            id_idx = table_field_names.index("id")
            input_idx = table_field_names.index("input")
            entry = list(q)
            out.append(dict(zip([table_field_names[id_idx],
                                 table_field_names[input_idx]],
                                [entry[id_idx], entry[input_idx]])))
        print("show_all_entries:out:")
        print(out)
        return(out)

    def add_pattern(self, entry):
        
        '''
        - ``entry`` -- entry dict to be added in db.
        see descrpition above. Differ for each of
        "examples_sampler", "examples_parser_eqs",
        "examples_parser_cs"
        (see model_tables for schema desc)
        (see also BaseDB.add_table_entry)

        Examples:

        # for eqs:
        entry = {"id": 0,
                 "input": r"sin(x)",
                 "comment": "",
                 "net": '',
                 "cpp": "sin((Block0OffsetX+idxX*DX))",
                 "sympy": 'sympy.sin(x)',
                 "vars": 'x'}
        '''
                      
        table = self.tables_dict[self.table_name]

        if "created_date" in entry:
            entry.pop("created_date")

        print("table_name:")
        print(self.table_name)
        print(table)
        self.add_table_entry(table, entry)

    def get_fields_names(self):
        return(BaseDB.get_fields_names(self, self.table_name))

    def select_fields_for_editor(self, key, silent=False):

        table = self.tables_dict[self.table_name]

        # table_field_names = table._meta.sorted_field_names
    
        res = (table.select()
               .where(table.__dict__['id'].field == key))
        if not silent:
            print("from select_fields_for_editor:")
        out = []
        for q in res:
            
            entry = q.__dict__['__data__']
            entry_to_add_ids = [elm for elm in list(entry.keys())
                                if elm not in ['created_date', 'id']]
            entry_to_add = dict(zip(entry_to_add_ids,
                                    [entry[idx] for idx in entry_to_add_ids]))
            # if self.table_name == "examples_sampler":
            #     entry_to_add = [entry[""]]
            if not silent:
                print(entry_to_add)
            out.append(entry_to_add)

        # for compatibility:
        class Res():
            def __init__(self, res):
                self.res = res
                self.count = len(res)
        return(Res(out))
    
    def select_pattern(self, key, silent=False):
        '''
        Select with term_name.
        (see BaseDB.select_table_entry)
        '''
        table = self.tables_dict[self.table_name]
        table_field_names = table._meta.sorted_field_names
        if not silent:
            print("\n table_sorted_field_names: %s" % (table_field_names))
        '''
        table.select().where(table.__dict__['predicate'].field=='subgroup')
        '''
        
        res = (table.select()
               .where(table.__dict__['id'].field == key))
        out = []
        for q in res:
            if not silent:
                print(q.__dict__['__data__'])
            out.append(q.__dict__['__data__'])

        # for compatibility:
        class Res():
            def __init__(self, res):
                self.res = res
                self.count = len(res)
        return(Res(out))

        return(out)

    def edit_pattern(self, key, props):
        '''
        Edit properties of entry

        Inputs:

        - ``id`` -- value of id field.

        - ``props`` -- must be dict like
    
        Example:
        # for eqs:
        entry = {"id": 0,
                 "input": r"sin(x)",
                 "comment": "",
                 "net": '',
                 "cpp": "sin((Block0OffsetX+idxX*DX))",
                 "sympy": 'sympy.sin(x)',
                 "vars": 'x'}
        '''

        print("FROM ExamplesDB.edit_pattern:")
        
        table = self.tables_dict[self.table_name]
        if "created_date" in props:
            props.pop("created_date")

        # convert all to str:
        for prop_name in props:
            props[prop_name] = str(props[prop_name])

        print("\nprops:")
        print(props)
        '''
        (table.update(**{"comment": "updated"})
         .where(table.__dict__['predicate'].field=='subgroup').execute())
        '''
        table = self.tables_dict[self.table_name]

        res = (table.update(**props)
               .where(table.__dict__['id'].field == key)
               .execute())

        print("\nupdated:")
        print(res)
        '''
        for query in res:
            print(query.__dict__)
        '''
        
    def del_pattern(self, key):
        '''

        Delete entry if entries
        ``id`` has id value

        Inputs:

        - ``id`` -- value of id field.
     
        '''
        print("FROM: ExamplesDB.del_pattern")

        table = self.tables_dict[self.table_name]
        
        res = (table.delete()
               .where(table.__dict__['id'].field == key)
               .execute())

        print("\ndeleted:")
        print(res)
        '''
        for query in res:
            print(query.__dict__)
        '''

    def load_all_tables(self):
        gen_table = self.check_table()
        BaseDB.load_tables(self, [gen_table])

    def change_dialect_db(self, dialect_name):
        self.table_name = dialect_name
        BaseDB.change_dialect_db(self, dialect_name)

    def create_examples_db(self):
        gen_table = self.check_table()
        BaseDB.create_db(self, [gen_table],
                         self.table_name)

    def create_examples_table(self):

        try:
            self.tables_dict
        except AttributeError:
            self.tables_dict = {}

        gen_table = self.check_table()
        tables = self.load_table(gen_table)
        self.create_db_tables(tables)
        
    def save_path(self, dialect_name, path):
        '''
        - ``dialect_name`` -- must be one of this:
        "examples_sampler", "examples_parser_eqs",
        "examples_parser_cs"
        '''
        if dialect_name not in self.supported_tables_names:
            self.raise_error(dialect_name)

        self.table_name = dialect_name
        BaseDB.save_path(self, dialect_name, path)

    def check_table(self):
        if self.table_name == "examples_sampler":
            gen_table = gen_examples_sampler_table
        elif self.table_name == "examples_parser_eqs":
            gen_table = gen_examples_parser_eqs_table
        elif self.table_name == "examples_parser_cs":
            gen_table = gen_examples_parser_cs_table
        else:
            self.raise_error(self.table_name)
        return(gen_table)

    def raise_error(self, dialect_name):
        raise(BaseException(('table_name %s not supported.'
                             % dialect_name)
                            + 'Supported names are: "examples_sampler",'
                            + ' "examples_parser_eqs",'
                            + ' "examples_parser_cs".'))
            

def test_create(dialect_name):
    '''
    dialect_name = "examples_sampler"
    or "examples_parser_eqs" or "examples_parser_cs":
    '''
    if dialect_name == "examples_sampler":
        test_create_sampler()
    elif dialect_name == "examples_parser_eqs":
        test_create_eqs()
    elif dialect_name == "examples_parser_cs":
        test_create_cs()


def test_create_sampler():

    print("\ntest create db")

    # dialect_name = "examples_sampler"
    # or "examples_parser_eqs" or "examples_parser_cs":
    agent = ExamplesDB("examples_sampler", new=True)
    
    '''
    # for creating new db file:
    path = "/absolute/path/to/tokentranslator/translator/sampling/data/examples/examples_sampler.db"
    agent.save_path("examples_sampler", path)
    '''
    agent.create_examples_db()
       
    agent.add_pattern({
        "id": 0,
        "input": r"subgroup(H, G)",
        "comment": "for test",
        "sampler_output": "",
        "net": '',
        "parser_output": ''})
                      
    agent.add_pattern({
        "id": 1,
        "input": r"abelian(G)",
        "comment": "for test",
        "sampler_output": "",
        "net": '',
        "parser_output": ''})

    agent.edit_pattern(0,
                       {"comment": "test edited"})

    # agent.del_pattern("pred")
    
    agent.show_all_entries()

    return(agent)


def test_create_eqs():

    print("\ntest create db")

    # dialect_name = "examples_sampler"
    # or "examples_parser_eqs" or "examples_parser_cs":
    agent = ExamplesDB("examples_parser_eqs", new=True)
    
    '''
    # for creating new db file:
    path = "/absolute/path/to/tokentranslator/env/equation_net/data/examples/examples_parser_eqs.db"
    agent.save_path("examples_parser_eqs", path)
    '''
    agent.create_examples_db()
       
    agent.add_pattern({
        "id": 0,
        "input": r"sin(x)",
        "comment": "for test",
        "net": '',
        "cpp": "sin((Block0OffsetX+idxX*DX))",
        "sympy": 'sympy.sin(x)',
        "vars": 'x'})
                      
    agent.add_pattern({
        "id": 1,
        "input": r"cos(x)",
        "comment": "for test",
        "net": '',
        "cpp": "cos((Block0OffsetX+idxX*DX))",
        "sympy": 'sympy.cos(x)',
        "vars": 'x'})

    agent.edit_pattern(0,
                       {"comment": "test edited"})

    # agent.del_pattern("pred")
    
    agent.show_all_entries()

    return(agent)


def test_create_cs():

    print("\ntest create cs db")

    # dialect_name = "examples_sampler"
    # or "examples_parser_eqs" or "examples_parser_cs":
    agent = ExamplesDB("examples_parser_cs", new=True)
    
    '''
    # for creating new db file:
    path = "/absolute/path/to/tokentranslator/env/clause/data/examples/examples_parser_cs.db"
    agent.save_path("examples_parser_cs", path)
    '''
    agent.create_examples_db()
       
    agent.add_pattern({
        "id": 0,
        "input": r"subgroup(H, G)",
        "comment": "for test",
        "net": '',
        "vars": 'H, G'})
                      
    agent.add_pattern({
        "id": 1,
        "input": r"abelian(G)",
        "comment": "for test",
        "net": '',
        "vars": 'G'})

    agent.edit_pattern(0,
                       {"comment": "test edited"})

    # agent.del_pattern("pred")
    
    agent.show_all_entries()

    return(agent)


def test_load(dialect_name):
    '''
    dialect_name = "examples_sampler"
    or "examples_parser_eqs" or "examples_parser_cs":
    '''
    print("\ntest load tables")

    agent = ExamplesDB(dialect_name=dialect_name)
    agent.load_all_tables()
    
    res = agent.show_all_entries()
    print("\ntest_load results:")
    print(res)
    return(agent)


def test_select(dialect_name):
    '''
    dialect_name = "examples_sampler"
    or "examples_parser_eqs" or "examples_parser_cs":
    '''

    print("\ntest select:")

    agent = test_load(dialect_name)
    res = agent.select_pattern(0)

    print("\nfields names:")
    print(agent.get_fields_names())

    print("\nresults of select_pattern:")
    print(res.res)

    res = agent.select_fields_for_editor(0)
    
    print("\nresults of select_fields_for_editor:")
    print(res.res)

    return(agent)


def test_edit(dialect_name):
    '''
    dialect_name = "examples_sampler"
    or "examples_parser_eqs" or "examples_parser_cs":
    '''
    print("\ntest edit:")

    agent = test_load(dialect_name)
    res = agent.select_pattern(0)
    
    print("\nresults:")
    print(res)

    agent.edit_pattern(0,
                       {"comment": "test edited"})
    
    res = agent.select_pattern(0)
    
    print("\nresults:")
    print(res)


def test_add(dialect_name):
    '''
    dialect_name = "examples_sampler"
    or "examples_parser_eqs" or "examples_parser_cs":
    '''
    agent = test_load(dialect_name)

    agent.add_pattern({
        "id": 2,
        "comment": "for test add/delete"})


def test_delete(dialect_name):
    '''
    dialect_name = "examples_sampler"
    or "examples_parser_eqs" or "examples_parser_cs":
    '''

    print("\ntest edit:")

    agent = test_load(dialect_name)
    
    res = agent.del_pattern(2)
    print("\nresults:")
    print(res)

    
def run():
    '''
    dialect_name = "examples_sampler"
    or "examples_parser_eqs" or "examples_parser_cs":
    '''
    dialect_name = "examples_parser_cs"
    # test_create(dialect_name)
    # test_load(dialect_name)
    test_select(dialect_name)
    # test_edit(dialect_name)
    # test_add(dialect_name)
    # test_delete(dialect_name)
    # test_load(dialect_name)


if __name__ == '__main__':
    run()
