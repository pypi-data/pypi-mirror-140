from tokentranslator.env.clause.clause_main import Clause


def run():
    sent = "abelian(G) \\and subgroup(H, G,) => abelian(H)"
    print("\noriginal:")
    print(sent)
    
    eq = Clause(sent)
    eq.parser.parse()
    
    print("\nresult:")
    print(eq.show_net_json_original())


if __name__ == "__main__":
    run()
    
