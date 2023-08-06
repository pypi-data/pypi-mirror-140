from tokentranslator.db_models.model_main import TokenizerDB
from tokentranslator.env.equation_net.equation import Equation
from tokentranslator.env.clause.clause_main import Clause

import sys


def run(dialect_from="eqs"):
    print("parser console. write 'q' or 'Ctrl+D' to exit.")
    model = TokenizerDB()
    model.change_dialect_db(dialect_from)
    
    if dialect_from == "cs":
        Parser = Clause
    else:
        Parser = Equation

    sent_stack = []
    last_value = ""
    while(True):
        # print("eq?> ", end='\r')
        try:
            sent = input("%s?> %s" % (dialect_from, last_value))
            if last_value != "":
                sent = last_value
            print(sent)
            print(type(sent))

            # TODO:
            # check keys codes:
            if sent == '\x1b[A':
                # if up:
                if len(sent_stack) > 0:
                    last_value = sent_stack.pop(0)
                    sent_stack.append(last_value)
                continue
            if sent == '\x1b[B':
                # if down:
                if len(sent_stack) > 0:
                    last_value = sent_stack.pop(-1)
                    sent_stack.insert(0, last_value)
                continue
            elif sent == "q":
                raise(EOFError)
            elif '"' in sent:
                sent = sent.split('"')[1]
            parser = Parser(sent=sent, db=model)
            parser.parser.parse()
            if dialect_from == "cs":
                parser.show_cyk_out()
            else:
                parser.replacer.sympy.make_sympy()
                parser.replacer.sympy.show_sympy()
            
            if last_value not in ['\x1b[A', '\x1b[B']:
                sent_stack.insert(0, sent)
            last_value = ""
        except EOFError:
            print("exiting...")
            break
        except:
            if hasattr(sys, "last_value"):
                print(sys.last_value)
                print(sys.last_traceback)
            else:
                print("error")
    # restore default for all sessions:
    if dialect_from != "eqs":
        model.change_dialect_db("eqs")


if __name__ == "__main__":
    if "-i" in sys.argv:
        dialect_from = sys.argv[sys.argv.index("-i")+1]
        if dialect_from in ["eqs", "eqs_tex", "cs"]:
            run(dialect_from)
        else:
            raise(Exception('"-i" param must be one'
                            + ' of ["eqs", "eqs_tex", "cs"]'))
    else:
        # default is "eqs"
        run()
