import peewee as pw


def gen_examples_parser_cs_table(db):
    '''Create table for sampler examples.'''

    ModelBase = create_base_model(db)

    class ExamplesParserCs(ModelBase):

        # automatic primary key named 'id'
        input = pw.TextField(default="")
        comment = pw.TextField(default="")
        net = pw.TextField(default="")
        vars = pw.TextField(default="")
        created_date = pw.DateTimeField(default=pw.datetime.datetime.now)

    return({"examples_parser_cs": ExamplesParserCs})


def gen_examples_parser_eqs_table(db):
    '''Create table for sampler examples.'''

    ModelBase = create_base_model(db)

    class ExamplesParserEqs(ModelBase):

        # automatic primary key named 'id'
        input = pw.TextField(default="")
        comment = pw.TextField(default="")
        net = pw.TextField(default="")
        cpp = pw.TextField(default="")
        sympy = pw.TextField(default="")
        vars = pw.TextField(default="")
        created_date = pw.DateTimeField(default=pw.datetime.datetime.now)

    return({"examples_parser_eqs": ExamplesParserEqs})


def gen_examples_sampler_table(db):
    '''Create table for sampler examples.'''

    ModelBase = create_base_model(db)

    class ExamplesSampler(ModelBase):

        # automatic primary key named 'id'
        input = pw.TextField(default="")
        comment = pw.TextField(default="")
        sampler_output = pw.TextField(default="")
        net = pw.TextField(default="")
        parser_output = pw.TextField(default="")
        created_date = pw.DateTimeField(default=pw.datetime.datetime.now)

    return({"examples_sampler": ExamplesSampler})


def gen_signatures_table(db):
    '''Create table for signatures.'''

    ModelBase = create_base_model(db)

    code_default = ""

    class Signatures(ModelBase):

        # automatic primary key named 'id'
        predicate = pw.CharField()
        signature = pw.CharField()
        dialect = pw.CharField(default="cpp")
        gen_type = pw.CharField(default="det")
        func_name = pw.CharField()
        count_of_samples = pw.IntegerField(default=10)

        code = pw.TextField(default=code_default)
        output = pw.TextField(default="")
        comment = pw.TextField(default="")

        created_date = pw.DateTimeField(default=pw.datetime.datetime.now)

    return({"signatures": Signatures})


def gen_replacer_table(db):
    '''Create table for replacer (for use in codemirror)'''

    ModelBase = create_base_model(db)

    grammar_type_default = "('br_left', [True, False, False])"

    class Replacers(ModelBase):

        # automatic primary key named 'id'
        term_name = pw.CharField()
        template = pw.CharField()

        grammar_type = pw.TextField(default=grammar_type_default)
        pattern_type = pw.TextField(default="('re', 0)")

        created_date = pw.DateTimeField(default=pw.datetime.datetime.now)

    return({"replacers": Replacers})


def gen_tokens_table(db):

    '''Create table for tokens'''

    ModelBase = create_base_model(db)

    grammar_type_default = "('br_left', [True, False, False])"

    class Tokens(ModelBase):

        # automatic primary key named 'id'
        term_name = pw.CharField()
        template = pw.CharField()

        grammar_type = pw.TextField(default=grammar_type_default)
        pattern_type = pw.TextField(default="('re', 0)")

        created_date = pw.DateTimeField(default=pw.datetime.datetime.now)

    return({"tokens": Tokens})


def gen_users_table(db):

    '''Create users tables'''

    ModelBase = create_base_model(db)

    class User(ModelBase):
        # automatic primary key named 'id'
        username = pw.CharField(unique=True)
        is_admin = pw.BooleanField(default=False)
        password = pw.CharField()  # TODO hash
        comment = pw.CharField(default="")
        email = pw.CharField()
        # expirydate = pw.DateField()

    return({"user": User})


def create_base_model(db):

    '''Create base table for all tables'''

    class ModelBase(pw.Model):
        class Meta:
            database = db

    return(ModelBase)


