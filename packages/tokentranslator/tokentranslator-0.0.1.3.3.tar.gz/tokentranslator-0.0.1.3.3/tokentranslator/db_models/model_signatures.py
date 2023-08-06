'''This class is extention of BaseDB for some specific task.
It contain methods that cannot be generalised, they are specific
for task environmant.
'''
# ~/anaconda3/envs/etokentranslator/bin/./python3 -c "import tokentranslator.db_models.model_signatures as ts;ts.run()"

# import peewee as pw
from datetime import date

from tokentranslator.db_models.model_base import BaseDB

from tokentranslator.db_models.model_tables import gen_signatures_table


class SignaturesDB(BaseDB):

    '''
    db for stable.

    each entry must be:

    (predicate, signature, dialect, gen_type,
     func_name, code, comment, count_of_samples)

    where

       predicate
          name for predicate generator used to (ex: "subgroup").
    
       signature
          describe  which argument of predicate is known,
          and which must be generated.
          (ex: "(True, False, True)" for subgroup(x, Y)
           arguments which is
           x(known), Y(unknown),
            out(known (i.e. expected output
              of subgroup predicate (True or False for any predicate)))
          together with predicate collumn must represent a unique key.

       gen_type
          type either ``rand`` or ``det`` which means random or determent
          if  ``rand`` ``count_of_samples`` also must be given.

       func_name
          name of python function inside ``code`` attribute,
          which represent signature. Better choice meaningful.
          (ex: like "sub_x_Y_out" for signature (True, False, True))
       
       code
          python algorithm, described how unknown arguments of signature
          will be gotten from known one.
          (ex: for signature (True, False, True) i.e. subgroup(x, Y)
           it must find group Y such that x is subgroup of Y)

       count_of_samples
          if ``gen_type`` is ``rand`` this code is represent count of
          attempts engine will call this generator function ("sub_x_Y_out")
          before giving up.

    Examples:

        entry = {"predicate": "subgroup",
                 "signature": r"(True, False, True)",
                 "dialect": "cpp",
                 "gen_type": 'rand',
                 "func_name": "sub_x_Y_out",
                 "code": 'sub_x_Y_out = lambda: print("hello")',
                 "comment": 'hello gen',
                 "count_of_samples": 10}
    '''
    def __init__(self, dialect_name="signatures", new=False):
        
        BaseDB.__init__(self, dialect_name, new)
        
    def show_all_entries(self, table_name="signatures", silent=False):

        '''except code'''

        # out = BaseDB.show_all_entries(self, table_name=table_name,
        #                               silent=silent)

        db = self.db
        table = self.tables_dict[table_name]

        table_field_names = table._meta.sorted_field_names
        if not silent:
            print("\n table_sorted_field_names: %s" % (table_field_names))

        qs = db.execute_sql("select * from %s" % (table_name,))
        if not silent:
            print("\n %s db entries:" % table_name)
        out = []
        for q in qs:
            if not silent:
                print(q)
            code_idx = table_field_names.index("code")
            entry = list(q)
            out.append(dict(zip(table_field_names[:code_idx]
                                + table_field_names[code_idx+1:],
                                entry[:code_idx]+entry[code_idx+1:])))
        return(out)

    def add_pattern(self, entry):
        
        '''
        - ``entry`` -- entry dict to be added in db.
        see descrpition above.
        (see BaseDB.add_table_entry)

        Examples:

        entry = {"predicate": "subgroup",
                 "signature": r"(True, False, True)",
                 "dialect": "cpp",
                 "gen_type": 'rand',
                 "func_name": "sub_x_Y_out",
                 "code": 'sub_x_Y_out = lambda: print("hello")',
                 "comment": 'hello gen',
                 "count_of_samples": 10}
        '''
                      
        table = self.tables_dict["signatures"]

        if "created_date" in entry:
            entry.pop("created_date")

        self.add_table_entry(table, entry)

    def get_fields_names(self):
        return(BaseDB.get_fields_names(self, "signatures"))
    
    def select_predicate(self, predicate, silent=False):
        table = self.tables_dict["signatures"]
        res = (table.select()
               .where(table.__dict__['predicate'].field == predicate))
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
        
    def select_pattern(self, predicate, signature, silent=False):
        '''
        Select with term_name.
        (see BaseDB.select_table_entry)
        '''
        table = self.tables_dict["signatures"]
        table_field_names = table._meta.sorted_field_names
        if not silent:
            print("\n table_sorted_field_names: %s" % (table_field_names))
        '''
        table.select().where(table.__dict__['predicate'].field=='subgroup')
        '''
        signature = str(signature)
        res = (table.select()
               .where(table.__dict__['predicate'].field == predicate)
               .where(table.__dict__['signature'].field == signature))
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

    def edit_pattern(self, predicate, signature, props):
        '''
        Edit properties of entry if entries
        ``predicate`` has predicate value and
        ``signature`` has signature value.

        Inputs:

        - ``predicate`` -- value of predicate field.

        - ``signature`` -- value of signature field.

        - ``props`` -- must be dict like
        {"dialect": "cpp",
        "gen_type": 'rand',
        "func_name": "sub_x_Y_out",
        "code": 'sub_x_Y_out = lambda: print("hello")',
        "comment": 'hello gen',
        "count_of_samples": 10}'''

        print("FROM SignaturesDB.edit_pattern:")
        
        table = self.tables_dict["signatures"]
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
        table = self.tables_dict['signatures']
        signature = str(signature)

        res = (table.update(**props)
               .where(table.__dict__['predicate'].field == predicate)
               .where(table.__dict__['signature'].field == signature)
               .execute())

        print("\nupdated:")
        print(res)
        '''
        for query in res:
            print(query.__dict__)
        '''
        
    def del_pattern(self, predicate, signature):
        '''

        Delete entry if entries
        ``predicate`` has predicate value and
        ``signature`` has signature value.

        Inputs:

        - ``predicate`` -- value of predicate field.

        - ``signature`` -- value of signature field.
        '''
        print("FROM: SignaturesDB.del_pattern")

        table = self.tables_dict["signatures"]
        signature = str(signature)
        res = (table.delete()
               .where(table.__dict__['predicate'].field == predicate)
               .where(table.__dict__['signature'].field == signature)
               .execute())

        print("\ndeleted:")
        print(res)
        '''
        for query in res:
            print(query.__dict__)
        '''

    def load_all_tables(self):
        
        BaseDB.load_tables(self, [gen_signatures_table])
        
    def create_signatures_db(self):
        BaseDB.create_db(self, [gen_signatures_table], "signatures")

    def create_signatures_table(self):

        try:
            self.tables_dict
        except AttributeError:
            self.tables_dict = {}

        tables = self.load_table(gen_signatures_table)
        self.create_db_tables(tables)


def test_create():

    print("\ntest create db")

    agent = SignaturesDB(new=True)
    '''
    agent.save_path("signatures", path)
    '''
    agent.create_signatures_db()

    agent.add_pattern({
        "predicate": "subgroup",
        "signature": str((True, False, True)),
        "dialect": "cpp",
        "gen_type": 'rand',
        "func_name": "sub_x_Y_out",
        "code": ('var = "hello"\n'
                 + 'sub_x_Y_out = lambda: print(var)'),
        "comment": 'hello gen',
        "count_of_samples": 10})
                      
    agent.add_pattern({
        "predicate": "subgroup",
        "signature": str((False, True, True)),
        "dialect": "cpp",
        "gen_type": 'rand',
        "func_name": "sub_X_y_out",
        "code": ('var = "hello1"\n'
                 + 'sub_X_y_out = lambda: print(var)'),
        "comment": 'hello1 gen',
        "count_of_samples": 10
    })

    agent.edit_pattern("subgroup", str((False, True, True)),
                       {"comment": "edited"})

    # agent.del_pattern("pred")
    
    agent.show_all_entries()

    return(agent)


def test_load():

    print("\ntest load tables")

    agent = SignaturesDB()
    agent.load_all_tables()
    
    res = agent.show_all_entries()
    print("\ntest_load results:")
    print(res)
    return(agent)


def test_select():

    print("\ntest select:")

    agent = test_load()
    res = agent.select_pattern("subgroup", str((True, False, True)))

    print("\nfields names:")
    print(agent.get_fields_names())

    print("\nresults of select_pattern:")
    print(res.res)

    res = agent.select_predicate("subgroup")
    
    print("\nresults of select_predicate:")
    print(res.res)
    
    return(agent)


def test_edit():

    print("\ntest edit:")

    agent = test_load()
    res = agent.select_pattern("subgroup", str((True, False, True)))
    
    print("\nresults:")
    print(res)

    agent.edit_pattern("subgroup", str((True, False, True)),
                       {"comment": "edited"})
    
    res = agent.select_pattern("subgroup", str((True, False, True)))
    
    print("\nresults:")
    print(res)


def test_add():
    agent = test_load()

    agent.add_pattern({
        "predicate": "subgroup",
        "signature": str((True, True, True)),
        "dialect": "cpp",
        "gen_type": 'rand',
        "func_name": "sub_x_Y_out",
        "code": ('var = "hello"\n'
                 + 'sub_x_Y_out = lambda: print(var)'),
        "comment": 'hello gen',
        "count_of_samples": 10})


def test_delete():
    print("\ntest edit:")

    agent = test_load()
    
    res = agent.del_pattern("subgroup", str((True, True, True)))
    print("\nresults:")
    print(res)

    
def run():
    # test_create()
    # test_load()
    test_select()
    # test_edit()
    # test_delete()
    # test_add()


if __name__ == '__main__':
    run()
