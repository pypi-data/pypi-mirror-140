# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['FAdo']

package_data = \
{'': ['*']}

install_requires = \
['argparse>=1.4.0,<2.0.0',
 'black>=22.1.0,<23.0.0',
 'deprecation>=2.1.0,<3.0.0',
 'graphviz>=0.19.1,<0.20.0',
 'ipython>=8.0.1,<9.0.0',
 'jupyter>=1.0.0,<2.0.0',
 'lark-parser>=0.12.0,<0.13.0',
 'mistune>=2.0.2,<3.0.0',
 'networkx>=2.6.3,<3.0.0',
 'platformdirs>=2.5.0,<3.0.0',
 'prompt-toolkit>=3.0.27,<4.0.0',
 'tomli>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'fado',
    'version': '2.0.3',
    'description': "A library of tools to manipulate formal languages' representations  mainly automata and regular expressions.",
    'long_description': '=============\nWhat is FAdo?\n=============\n\nThe **FAdo** system aims to provide an open source extensible high-performance software library for the symbolic\nmanipulation of automata and other models of computation.\n\nTo allow high-level programming with complex data structures, easy prototyping of algorithms, and portability\n(to use in computer grid systems for example), are its main features. Our main motivation is the theoretical\nand experimental research, but we have also in mind the construction of a pedagogical tool for teaching automata\ntheory and formal languages.\n\n-----------------\nRegular Languages\n-----------------\n\nIt currently includes most standard operations for the manipulation of regular languages. Regular languages can\nbe represented by regular expressions (RegExp) or finite automata, among other formalisms. Finite automata may\nbe deterministic (DFA), non-deterministic (NFA) or generalized (GFA). In **FAdo** these representations are implemented\nas Python classes.\n\nElementary regular languages operations as union, intersection, concatenation, complementation and reverse are\nimplemented for each class. Also several combined operations are available for specific models.\n\nSeveral conversions between these representations are implemented:\n\n* NFA -> DFA: subset construction\n\n* NFA -> RE: recursive method\n\n* GFA -> RE: state elimination, with possible choice of state orderings\n\n* RE -> NFA: Thompson method, Glushkov method, follow, Brzozowski, and partial derivatives.\n\n* For DFAs several minimization algorithms are available: Moore, Hopcroft, and some incremental algorithms. Brzozowski minimization is available for NFAs.\n\n* An algorithm for hyper-minimization of DFAs\n\n* Language equivalence of two DFAs can be determined by reducing their correspondent minimal DFA to a canonical form, or by the Hopcroft and Karp algorithm.\n\n* Enumeration of the first words of a language or all words of a given length (Cross Section)\n\n* Some support for the transition semigroups of DFAs\n\n----------------\nFinite Languages\n----------------\n\nSpecial methods for finite languages are available:\n\n* Construction of a ADFA (acyclic finite automata) from a set of words\n\n* Minimization of ADFAs\n\n* Several methods for ADFAs random generation\n\n* Methods for deterministic cover finite automata (DCFA)\n\n-----------\nTransducers\n-----------\n\nSeveral methods for transducers in standard form (SFT) are available:\n\n* Rational operations: union, inverse, reversal, composition, concatenation, Star\n\n* Test if a transducer is functional\n\n* Input intersection and Output intersection operations\n\n-----\nCodes\n-----\n\nA *language property* is a set of languages. Given a property specified by a transducer, several language tests are possible.\n\n* Satisfaction i.e. if a language satisfies the property\n\n* Maximality i.e. the language satisfies the property and is maximal\n\n* Properties implemented by transducers include: input preserving, input altering, trajectories, and fixed properties\n\n* Computation of the edit distance of a regular language, using input altering transducers\n\n\n\n',
    'author': 'Rogerio Reis',
    'author_email': 'rogerio.reis@fc.up.pt',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://fado.dcc.fc.up.pt',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
