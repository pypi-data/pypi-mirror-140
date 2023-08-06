'''

CD: numeral, cardinal
     DM2,000 ...
DT: determiner
    
EX: existential there
FW: foreign word
IN: preposition or conjunction, subordinating
     ...
JJ: adjective or numeral, ordinal
JJR: adjective, comparative
     ...
JJS: adjective, superlative
     ...
LS: list item marker
MD: modal auxiliary
NN: noun, common, singular or mass
 ...
NNP: noun, proper, singular
NNPS: noun, proper, plural
NNS: noun, common, plural
PDT: pre-determiner

POS: genitive marker
    ' 's
PRP: pronoun, personal
PRP$: pronoun, possessive
    her his mine my our ours their thy your
RB: adverb
RBR: adverb, comparative
RBS: adverb, superlative
RP: particle
SYM: symbol

TO: "to" as preposition or infinitive marker

UH: interjection
VB: verb, base form
VBD: verb, past tense
VBG: verb, present participle or gerund
VBN: verb, past participle
VBP: verb, present tense, not 3rd person singular
VBZ: verb, present tense, 3rd person singular
WDT: WH-determiner

WP: WH-pronoun

WP$: WH-pronoun, possessive
WRB: Wh-adverb

'''

_tokens = [
    ("CD", ("mid-1890 nine-thirty forty-two one-tenth ten million"
            + " 0.5 one forty-seven 1987 twenty 79 zero two 78-degrees"
            + " eighty-four IX 60s .025 fifteen 271,124 dozen quintillion")),
    ("DT", ("all an another any both del each either every half la"
            + " many much nary neither no some such that the them"
            + " these this those")),
    ("EX", "there"),
    ("FW", ("gemeinschaft hund ich jeux habeas Haementeria Herr"
            + r" K'ang-si vous lutihaw alai je jour objets salutaris"
            + " fille quibusdam pas trop Monte terram fiche oui corporis")),
    ("IN", ("astride among uppon whether out inside pro despite on"
            + " by throughout below within for towards near behind atop"
            + " around if like until below next into if beside")),
    ("JJ", ("third ill-mannered pre-war regrettable oiled calamitous first"
            + " separable ectoplasmic battery-powered participatory"
            + " fourth still-to-be-named multilingual multi-disciplinary")),
    ("JJR", ("bleaker braver breezier briefer brighter brisker broader"
             + " bumper busier calmer cheaper choosier cleaner clearer closer"
             + " colder commoner costlier cozier creamier crunchier cuter")),
    ("JJS", ("calmest cheapest choicest classiest cleanest clearest closest"
             + " commonest corniest costliest crassest creepiest crudest"
             + " cutest darkest deadliest dearest deepest densest dinkiest")),
    ("LS", (r"A A. B B. C C. D E F First G H I J K One SP-44001 SP-44002"
            + r" SP-44005 SP-44007 Second Third Three Two * a b c d first"
            + " five four one six three two")),
    ("MD", ("can cannot could couldn't dare may might must need ought shall"
            + " should shouldn't will would")),
    ("NN", ("common-carrier cabbage knuckle-duster Casino afghan shed"
            + " thermostat investment slide humour falloff slick wind hyena"
            + " override subhumanity machinist")),
    ("NNP", ("Motown Venneboerger Czestochwa Ranzer Conchita Trumplane"
             + "Christos Oceanside Escobar Kreisler Sawyer Cougar Yvette"
             + " Ervin ODI Darryl CTCA Shannon A.K.C. Meltex Liverpool")),
    ("NNPS", ("Americans Americas Amharas Amityvilles Amusements"
              + " Anarcho-Syndicalists Andalusians Andes Andruses Angels"
              + " Animals Anthony Antilles Antiques Apache Apaches Apocrypha")),
    ("NNS", ("undergraduates scotches bric-a-brac products bodyguards facets"
             + " coasts divestitures storehouses designs clubs fragrances"
             + " averages subjectivists apprehensions muses factory-jobs")),
    ("PDT", "all both half many quite such sure this"),
    ("PRP", ("hers herself him himself hisself it itself me myself one oneself"
             + " ours ourselves ownself self she thee theirs them themselves"
             + " they thou thy us")),
    ("RB", ("occasionally unabatingly maddeningly adventurously professedly"
            + " stirringly prominently technologically magisterially"
            + " predominately swiftly fiscally pitilessly")),
    ("RBR", ("further gloomier grander graver greater grimmer harder harsher"
             + " healthier heavier higher however larger later leaner"
             + " lengthier less-perfectly lesser lonelier longer louder"
             + " lower more")),
    ("RBS", ("best biggest bluntest earliest farthest first furthest hardest"
             + " heartiest highest largest least less most nearest second"
             + " tightest worst")),
    ("RP", ("aboard about across along apart around aside at away back before"
            + " behind by crop down ever fast for forth from go high i.e."
            + " in into just later low more off on open out over per pie"
            + " raising start teeth that through under unto up up-pp"
            + " upon whole with you")),
    ("SYM", r"% & ' '' ''. ) ). * + ,. < = > @ A[fj] U.S U.S.S.R * ** ***"),
    ("TO", "to"),
    ("UH", ("Goodbye Goody Gosh Wow Jeepers Jee-sus Hubba Hey Kee-reist Oops"
            + "amen huh howdy uh dammit whammo shucks heck anyways whodunnit"
            + " honey golly man baby diddle hush sonuvabitch")),
    ("VB", ("ask assemble assess assign assume atone attention avoid bake"
            + " balkanize bank begin behold believe bend benefit bevel"
            + " beware bless boil bomb boost brace break bring broil"
            + " brush build")),
    ("VBD", ("dipped pleaded swiped regummed soaked tidied convened halted"
             + " registered cushioned exacted snubbed strode aimed adopted"
             + " belied figgered speculated wore appreciated contemplated")),
    ("VBG", (r"telegraphing stirring focusing angering judging stalling"
             + r" lactating hankerin' alleging veering capping approaching"
             + " traveling besieging encrypting interrupting erasing wincing")),
    ("VBN", ("multihulled dilapidated aerosolized chaired languished"
             + " panelized used experimented flourished imitated reunifed"
             + " factored condensed sheared unsettled primed dubbed desired")),
    ("VBP", ("predominate wrap resort sue twist spill cure lengthen brush"
             + " terminate appear tend stray glisten obtain comprise detest"
             + " tease attract emphasize mold postpone sever return wag")),
    ("VBZ",  ("bases reconstructs marks mixes displeases seals carps weaves"
              + " snatches slumps stretches authorizes smolders pictures"
              + " emerges stockpiles seduces fizzes uses bolsters slaps"
              + " speaks pleads")),
    ("WDT", "that what whatever which whichever"),
    ("WP", "that what whatever whatsoever which who whom whosoever"),
    (r"WP$", "whose"),
    ("WRB", ("how however whence whenever where whereby"
             + " whereever wherein whereof why"))]

tokens = dict([(tok.lower(), words) for (tok, words) in _tokens])
