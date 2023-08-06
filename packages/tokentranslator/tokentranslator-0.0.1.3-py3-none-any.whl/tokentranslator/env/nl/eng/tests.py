''' python3 tests.py'''
from tokentranslator.env.nl.eng.lang_main import Eng

import traceback
import sympy


tests = ["cat move",
         "horse jump"]


def test_one(_id=0, verbose=False):
    eq = Eng(tests[_id])
    print("\n=== test %s: %s ===" % (_id, tests[_id]))
    try:
        try:
            eq.parser.parse()
            eq.args_editor.get_vars()
            eq.sampling.sampling_vars_eng()

        except BaseException as e:
            # print(eq.from_lex)
            # print(eq.from_cyk)
            if verbose:
                print(e)
                traceback.print_exc()
            pass

        # eq.replacer.cpp.editor.set_default()
        # eq.replacer.cpp.make_cpp()

        print('\noriginal:')
        eq.show_original()
        
        print('\nlex:')
        eq.parser.show_lex()
        
        print('\ncyk:')
        eq.parser.show_cyk()
        
        # print('\nargs:')
        # eq.args_editor.show_args()
        
        print('\nvars:')
        eq.args_editor.show_vars()

        print('\nsampling_vars_eng:')
        eq.sampling.show_sampled()
        
        # print('\noperator tree:')
        # eq.parser.show_ot()
        
        return(True)
    except BaseException as e:
        print("fail test %s" % (_id))
        if verbose:
            print(e)
            traceback.print_exc()
        return(False)


def test_all():

    succesed = []
    failed = []

    for _id, test in enumerate(tests):
        if test_one(_id):
            succesed.append(_id)
        else:
            failed.append(_id)

    print("\ntests failed %s from %s:"
          % (len(failed), len(failed)+len(succesed)))
    print(failed)
    
    '''
    outs.append(eq.flatten('original')
    outs.append(eq._sym_step(test))

    cpp_fl = flatten(eq.operator_tree, eq.tree_cpp_replacer)
    cpp_fl = eq.operator_tree.flatten('cpp')
    cpp_map = map_tree(eq.operator_tree, eq.tree_cpp_replacer)
    cpp_map_postproc = map_tree_postproc(cpp_map, eq.tree_cpp_replacer)

    print("original:")
    print(cpp_map_postproc.flatten('original'))
    print("cpp:")
    print(cpp_map_postproc.flatten('cpp'))

    return(cpp_map_postproc)
    return(cpp_map)
    return(cpp_fl)
    '''


def test_rand():
    e = Equation("a*c + d*U+f(y)+sin(x)=cos(x)")
    # e = Equation("a*D[U,{x,2}] + d*D[U,{y,2}]=cos(x)")
    e.parser.parse()

    print("\noriginal")
    e.show_original()

    e.sampling.sympy.sampling_subs()
    print("\nsampling_subs:")
    e.sampling.sympy.show_sampled()

    e.sampling.sympy.sampling_vars()
    print("\nsampling_vars:")
    e.sampling.sympy.show_sampled()

    # substitute U:
    # get_vars alredy called by
    # sampling_subs or sampling_vars:
    U = sympy.symbols('U')
    e.args_editor.subs(U=U)

    e.slambda.sympy.lambdify_sem()
    out = e.slambda.sympy.lambdify()
    print("\nlambdify:")
    print(out())
    
    print("\nvariables:")
    for var in e.vars:
        print(var['variable'])


if __name__ == '__main__':
    # test_all()
    # test_rand()
    test_one(0, verbose=True)
