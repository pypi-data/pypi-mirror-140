# coding=utf-8
"""Tranducers and codes tests"""
import unittest

from reex import str2regexp
from transducers import *
from codes import *
import fl


def hammingdist(s1, s2):
    return sum([int(s1[i] == s2[i]) for i in range(len(s1))])


#  Various automata; alphabet =  {0, 1}
#
# all 4-bit words:
strb4 = '@NFA 4 * 0\n0 0 1\n0 1 1\n1 0 2\n1 1 2\n2 0 3\n2 1 3\n3 0 4\n3 1 4\n'
ab4 = fio.readOneFromString(strb4)
strb5 = '@NFA 5 * 0\n0 0 1\n0 1 1\n1 0 2\n1 1 2\n2 0 3\n2 1 3\n3 0 4\n3 1 4\n4 0 5\n4 1 5\n'
ab5 = fio.readOneFromString(strb5)
strb6 = '@NFA 6 * 0\n0 0 1\n0 1 1\n1 0 2\n1 1 2\n2 0 3\n2 1 3\n3 0 4\n3 1 4\n4 0 5\n4 1 5\n5 0 6\n5 1 6\n'
ab6 = fio.readOneFromString(strb6)
strb6am = '@NFA 0 1 2 3 4 5 6 * 0\n0 0 1\n0 1 1\n1 0 2\n1 1 2\n2 0 3\n2 1 3\n3 0 4\n3 1 4\n4 0 5\n4 1 5\n5 0 6\n5 1 6\n'
ab6am = fio.readOneFromString(strb6am)
strb7 = '@NFA 7 * 0\n0 0 1\n0 1 1\n1 0 2\n1 1 2\n2 0 3\n2 1 3\n3 0 4\n3 1 4\n4 0 5\n4 1 5\n5 0 6\n5 1 6\n6 0 7\n6 1 7\n'
ab7 = fio.readOneFromString(strb7)
# accepts {0000000, 0000111, 1111111}
ap3_7 = fio.readOneFromString('@NFA 7 * 0\n0 0 1\n0 1 1a\n1 0 2\n1a 1 2a\n2 0 3\n2a 1 3a\n3 0 4\n3a 1 4a\n4 0 5\n4 1 5a\n4a 1 5a\n5 0 6\n5a 1 6a\n6 0 7\n6a 1 7\n')
#
#  Various IA transducers; alphabet =  {0, 1}.  _d means decreasing;
#
str2s_d = '@Transducer 1 2 * 0\n0 0 0 0\n0 1 1 0\n0 0 1 1\n1 0 0 1\n1 1 1 1\n1 0 1 2\n1 1 0 2\n2 0 0 2\n2 1 1 2\n'
u2s_d = fio.readOneFromString(str2s_d)
str2id_d = '@Transducer 1 2 * 0 3 6\n0 0 0 0\n0 1 1 0\n0 0 @CEpsilon 1\n0 1 @CEpsilon 1\n'\
         '1 0 0 1\n1 1 1 1\n1 0 @CEpsilon 2\n1 1 @CEpsilon 2\n2 0 0 2\n2 1 1 2\n'\
         '3 0 0 3\n3 1 1 3\n3 0 @CEpsilon 4\n4 1 1 5\n5 0 0 5\n5 1 1 5\n4 @CEpsilon 1 2\n'\
         '5 @CEpsilon 0 2\n5 @CEpsilon 1 2\n'\
         '6 0 0 6\n6 1 1 6\n6 @CEpsilon 1 7\n7 0 0 8\n8 0 0 8\n8 1 1 8\n7 0 @CEpsilon 2\n'\
         '8 0 @CEpsilon 2\n8 1 @CEpsilon 2\n'
u2id_d = fio.readOneFromString(str2id_d)
#
#  Various IP transducers; alphabet =  {0, 1}.  _d means decreasing; _ieee: from an ieee tit paper
#
t2s = fio.readOneFromString('@Transducer 0 1 2 * 0\n0 0 0 0\n0 1 1 0\n0 0 1 1\n0 1 0 1\n1 0 0 1\n1 1 1 1\n1 0 1 2\n1 1 0 2\n2 0 0 2\n2 1 1 2\n')
t2s_d = fio.readOneFromString('@Transducer 0 1 2 * 0\n0 0 0 0\n0 1 1 0\n0 0 1 1\n1 0 0 1\n1 1 1 1\n1 0 1 2\n1 1 0 2\n2 0 0 2\n2 1 1 2\n')
t1s_d = fio.readOneFromString('@Transducer 0 1 * 0\n0 0 0 0\n0 1 1 0\n0 0 1 1\n1 0 0 1\n1 1 1 1\n')
#
t1id_d = fio.readOneFromString('@Transducer 0 1 * 0\n0 0 0 0\n0 1 1 0\n0 0 @CEpsilon 1\n0 1 @CEpsilon 1\n1 0 0 1\n1 1 1 1\n')
#
t2id = fio.readOneFromString('@Transducer 0 1 2 * 0\n0 0 0 0\n0 1 1 0\n0 0 @CEpsilon 1\n0 1 @CEpsilon 1\n0 @CEpsilon 0 1\n0 @CEpsilon 1 1\n1 0 0 1\n1 1 1 1\n1 0 @CEpsilon 2\n1 1 @CEpsilon 2\n1 @CEpsilon 0 2\n1 @CEpsilon 1 2\n2 0 0 2\n2 1 1 2\n')
#
t1d_ieee = fio.readOneFromString('@Transducer 0 2 * 0\n0 0 0 0\n0 1 1 0\n0 0 @CEpsilon 1\n0 1 @CEpsilon 1\n1 0 0 1\n1 1 1 1\n1 @CEpsilon 0 2\n1 @CEpsilon 1 2\n')
#
str2id_d = '@Transducer 0 1 2 * 0 3 6\n0 0 0 0\n0 1 1 0\n0 0 @CEpsilon 1\n0 1 @CEpsilon 1\n'\
         '1 0 0 1\n1 1 1 1\n1 0 @CEpsilon 2\n1 1 @CEpsilon 2\n2 0 0 2\n2 1 1 2\n'\
         '3 0 0 3\n3 1 1 3\n3 0 @CEpsilon 4\n4 1 1 5\n5 0 0 5\n5 1 1 5\n4 @CEpsilon 1 2\n'\
         '5 @CEpsilon 0 2\n5 @CEpsilon 1 2\n'\
         '6 0 0 6\n6 1 1 6\n6 @CEpsilon 1 7\n7 0 0 8\n8 0 0 8\n8 1 1 8\n7 0 @CEpsilon 2\n'\
         '8 0 @CEpsilon 2\n8 1 @CEpsilon 2\n'
t2id_d = fio.readOneFromString(str2id_d)

#  Input preserving transducers for error-detection
#  Various IP transducers; alphabet =  {a, b}.
#
# Up to 1 substitution (IP transducer)
s1ts = '@Transducer 0 1 * 0\n'\
        '0 a a 0\n'\
        '0 b b 0\n'\
        '0 b a 1\n'\
        '0 a b 1\n'\
        '1 a a 1\n'\
        '1 b b 1\n'

# Up to 2 substitutions (IP transducer)
s2ts = '@Transducer 0 1 2 * 0\n'\
        '0 a a 0\n'\
        '0 b b 0\n'\
        '0 b a 1\n'\
        '0 a b 1\n'\
        '1 a a 1\n'\
        '1 b b 1\n'\
        '1 b a 2\n'\
        '1 a b 2\n'\
        '2 a a 2\n'\
        '2 b b 2\n'

# Up to 1 insertion and deletion (IP transducer)
id1ts = '@Transducer 0 1 * 0\n'\
        '0 a a 0\n'\
        '0 b b 0\n'\
        '0 @CEpsilon a 1\n'\
        '0 @CEpsilon b 1\n'\
        '0 a @CEpsilon 1\n'\
        '0 b @CEpsilon 1\n'\
        '1 a a 1\n'\
        '1 b b 1\n'

# Up to 2 insertions and deletions (IP transducer)
id2ts = '@Transducer 0 1 2 * 0\n'\
        '0 a a 0\n'\
        '0 b b 0\n'\
        '0 @CEpsilon a 1\n'\
        '0 @CEpsilon b 1\n'\
        '0 a @CEpsilon 1\n'\
        '0 b @CEpsilon 1\n'\
        '1 a a 1\n'\
        '1 b b 1\n'\
        '1 @CEpsilon a 2\n'\
        '1 @CEpsilon b 2\n'\
        '1 a @CEpsilon 2\n'\
        '1 b @CEpsilon 2\n'\
        '2 a a 2\n'\
        '2 b b 2\n'


# noinspection PyTypeChecker
class MyTestCase(unittest.TestCase):
    @staticmethod
    def _concat(xxx_todo_changeme):
        (a, b) = xxx_todo_changeme
        return a + b

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.nfas = fio.readFromFile("test/NFA-abx.fa")
        self.transducer1 = fio.readOneFromFile("test/TR-for-in+out-Intersect-with-NFA-abx.fa")

    def test_io(self):
        """Test readFromFile """
        fas = fio.readFromFile("test/TR-io.fa")
        self.assertEqual(len(fas), 5, "Number of TRs read is wrong")

    def test_dup(self):
        """Tests dup() for transducers"""
        t = SFT()
        i = t.addState()
        t.addInitial(i)
        t.addFinal(i)
        s = t.dup()
        self.assertTrue(len(s) == len(t))

    def test_inverse(self):
        """Test inverse method"""
        detIOt = fio.readOneFromFile("test/TR-detIO.fa")
        a = detIOt.inverse().inverse()
        self.assertTrue(a.toInNFA().toDFA() == detIOt.toInNFA().toDFA())
        self.assertTrue(a.toOutNFA().toDFA() == detIOt.toOutNFA().toDFA())

    def test_emptyP(self):
        """Test emptyP"""
        empty = fio.readFromFile("test/TR-emptyness.fa")
        self.assertTrue(empty[0].emptyP())
        self.assertFalse(empty[1].emptyP())

    def test_trim(self):
        """ Test trimming transducers. Credits to David Purser (D.J.Purser@warwick.ac.uk) """
        tran = SFT()
        tran.addState('r')  # 0
        tran.addState('s')  # 1
        tran.addState('t')  # 2
        tran.addState('u')  # 3
        tran.addState('v')  # 4
        tran.addState('w')  # 5
        tran.addState('x')  # 6
        tran.addState('y')  # 7
        tran.addState('z')  # 8
        tran.addInitial(0)
        tran.addTransition(0, 'a', 'b', 1)
        tran.addTransition(1, 'a', 'b', 4)
        tran.addTransition(1, 'c', 'd', 8)
        tran.setFinal([4, 8])
        tran.trim()
        self.assertTrue(tran.finalP(tran.stateIndex("v")))
        self.assertTrue(tran.finalP(tran.stateIndex("z")))
        self.assertEqual(len(tran.Final), 2, "Number of Finals after trimming wrong")

    def test_nonEmptyW(self):
        """Test non empty witness production"""
        empty = fio.readFromFile("test/TR-emptyness.fa")
        r = re.compile('^(?P<s>.).b(?P=s).b$')
        self.assertEqual(empty[0].nonEmptyW(), (None, None))
        self.assertTrue(r.match(self._concat(empty[1].nonEmptyW())))

    def test_inIntersection(self):
        """Test Input Intersection"""
        for nfa in self.nfas:
            self.assertTrue(self.transducer1.inIntersection(nfa).emptyP())
            self.assertFalse(self.transducer1.inverse().inIntersection(nfa).emptyP())

    def test_outIntersection(self):
        """Test Out Intersection"""
        for nfa in self.nfas:
            self.assertEqual(self.transducer1.inverse().outIntersection(nfa).emptyP(),
                             self.transducer1.inverse().outIntersectionDerived(nfa).emptyP())
            self.assertEqual(self.transducer1.outIntersection(nfa).emptyP(),
                             self.transducer1.outIntersectionDerived(nfa).emptyP())

    def test_evalWordP(self):
        """ Test evalWordP """
        t = fio.readOneFromFile("test/TR-upto1err.fa")
        self.assertTrue(t.evalWordP(("00000", "000000")))
        self.assertTrue(t.evalWordP(("00000", "0000")))
        self.assertTrue(t.evalWordP(("00000", "00010")))
        self.assertTrue(t.evalWordP(("00000", "01000")))
        self.assertTrue(t.evalWordP(("00000", "00100")))
        self.assertTrue(t.evalWordP(("00000", "10000")))
        self.assertTrue(t.evalWordP(("00000", "00001")))
        self.assertTrue(t.evalWordP(("00000", "00000")))

    def test_runOnWord(self):
        """Test run on a given word"""
        transducersROW = fio.readFromFile("test/TR-runOnWord.fa")
        self.assertTrue(transducersROW[0].runOnWord('aa') == str2regexp('aa(a+b)*'))
        self.assertTrue(transducersROW[0].runOnWord(Epsilon) == str2regexp('(a+b)*'))
        self.assertTrue(transducersROW[0].inverse().runOnWord('aa') == str2regexp('@CEpsilon+a+aa'))
        self.assertTrue(transducersROW[0].inverse().runOnWord(Epsilon) == str2regexp('@CEpsilon'))
        self.assertTrue(transducersROW[1].runOnWord('aa') == str2regexp('aa(a+b)(a+b)*'))
        self.assertTrue(transducersROW[1].runOnWord(Epsilon) == str2regexp('(a+b)(a+b)*'))
        self.assertTrue(transducersROW[1].inverse().runOnWord('aa') == str2regexp('@CEpsilon+a'))
        self.assertTrue(transducersROW[1].inverse().runOnWord(Epsilon) == str2regexp('@empty_set'))

    def test_runOnNFA(self):
        """Test run on NFA"""
        nfa = transducersRON[0]
        self.assertTrue(transducersRON[1].runOnNFA(nfa) == str2regexp("aa*"))
        self.assertTrue(transducersRON[2].runOnNFA(nfa).emptyP())
        self.assertTrue(transducersRON[3].runOnNFA(nfa) == str2regexp("ab(@CEpsilon+b+bb)(ab(@CEpsilon+b+bb))*"))

    def test_composition(self):
        """Test composition of SFTransducers"""
        transducersComp = fio.readFromFile("test/TR-composition.fa")
        self.assertTrue(transducersComp[3].composition(transducersComp[3]).runOnWord('aa') == str2regexp(
            'aacc'))
        self.assertTrue(transducersComp[0].composition(transducersComp[0]).runOnWord('aa') == str2regexp(
            '@CEpsilon+a(a+b)+(a+b)a+a+(a+b)aa+a(a+b)a+aa(a+b)+(a+b)aa(a+b)+a(a+b)(a+b)a+(a+b)(a+b)aa+a(a+b)a(a+b)+' +
            '(a+b)a(a+b)a+aa(a+b)(a+b)+aa+a'))
        self.assertTrue(transducersComp[2].composition(transducersComp[3]).runOnWord('aa') == str2regexp(
            'aac+bac+abc'))

    def test_nonFunctionalW(self):
        """Test non functionality witness production"""
        transducersFunc = fio.readFromFile("test/TR-functionality.fa")
        self.assertTrue(transducersFunc[0].nonFunctionalW() == (None, None, None))
        self.assertTrue(transducersFunc[1].nonFunctionalW() == (None, None, None))
        self.assertFalse(transducersFunc[2].nonFunctionalW() == (None, None, None))
        self.assertFalse(transducersFunc[2].inverse().nonFunctionalW() == (None, None, None))
        self.assertFalse(transducersFunc[3].nonFunctionalW() == (None, None, None))

    def test_union_star_concat(self):
        """Test union concatenation and CStar"""
        transducerUCS = fio.readFromFile("test/TR-union-concat-star.fa")
        self.assertTrue(transducerUCS[0].union(transducerUCS[1]).runOnWord("aaa") == str2regexp("@epsilon+a+aa+aaac"))
        self.assertTrue(transducerUCS[1].union(transducerUCS[0]).runOnWord("aaa") == str2regexp("@epsilon+a+aa+aaac"))
        self.assertTrue(transducerUCS[0].concat(transducerUCS[1]).runOnWord("aaa") == str2regexp("c+ac+aac"))
        self.assertTrue(transducerUCS[1].concat(transducerUCS[0]).runOnWord("aaa") == str2regexp("c+ac+aac+ca+caa+aca"))
        self.assertTrue(transducerUCS[1].star().runOnWord('aa') == str2regexp("c*ac*acc*"))
        self.assertTrue(transducerUCS[0].star().runOnWord('aa') == str2regexp("a+@epsilon"))

    def test_gft_to_sft(self):
        """ Test conversion of GFT to SFT"""
        transducerGFT = fio.readFromFile("test/TR-general2sft.fa")
        auxL = [(4, 6, 1, 9, 11, 1), (2, 6, 1, 2, 6, 1), (4, 8, 1, 17, 21, 1)]
        for i in range(3):
            self.assertTrue(len(transducerGFT[i]) == auxL[i][0])
            self.assertTrue(transducerGFT[i].countTransitions() == auxL[i][1])
            self.assertTrue(len(transducerGFT[i].Initial) == auxL[i][2])
            s = transducerGFT[i].toSFT()
            self.assertTrue(len(s) == auxL[i][3])
            self.assertTrue(s.countTransitions() == auxL[i][4])
            self.assertTrue(len(s.Initial) == auxL[i][5])

    def test_IATP_Satisfaction(self):
        """ Satisfaction Test """
        p = buildIATPropF("test/P-infix.fa")
        a = fio.readOneFromFile("test/DFA-ac+bba.fa")
        self.assertTrue(p.satisfiesP(a))
        a = fio.readOneFromFile("test/DFA-ab#.fa")
        r = re.compile('^(?P<s>.*)#.*(?P=s).*$')
        i, j = p.notSatisfiesW(a)
        if len(i) < len(j):
            x = i + "#" + j
        else:
            x = j + "#" + i
        self.assertTrue(r.match(x))

    def test_IATP_Maximality(self):
        """Maximality test """
        p = buildIATPropF("test/P-infix.fa")
        a = fio.readOneFromFile("test/DFA-ab#a.fa")
        self.assertFalse(p.maximalP(a))
        w = p.notMaximalW(a)
        self.assertFalse(a.evalWordP(w))
        self.assertTrue(p.satisfiesP(fl.FL([w]).trieFA().toNFA() | a))
        l = fl.FL(['aa', 'ab', 'ba', 'bb']).trieFA().toNFA()
        self.assertTrue(p.maximalP(l))

    def test_IPTP_Satisfaction(self):
        """ Satisfaction Test """
        p = buildIPTPropF("test/P-ip-infix.fa")
        a = fio.readOneFromFile("test/DFA-ac+bba.fa")
        self.assertTrue(p.satisfiesP(a))
        a = fio.readOneFromFile("test/DFA-ab#.fa")
        r = re.compile('^(?P<s>.*)#.*(?P=s).*$')
        i, j = p.notSatisfiesW(a)
        if len(i) < len(j):
            x = i + "#" + j
        else:
            x = j + "#" + i
        self.assertTrue(r.match(x))

    def test_IPTP_Maximality(self):
        """Maximality test """
        p = buildIPTPropF("test/P-ip-infix.fa")
        a = fio.readOneFromFile("test/DFA-ab#a.fa")
        self.assertFalse(p.maximalP(a))
        w = p.notMaximalW(a)
        self.assertFalse(a.evalWordP(w))
        self.assertTrue(p.satisfiesP(fl.FL([w]).trieFA().toNFA() | a))
        l = fl.FL(['aa', 'ab', 'ba', 'bb']).trieFA().toNFA()
        l1 = fl.FL(['ab', 'ba', 'bb']).trieFA().toNFA()
        self.assertTrue(p.maximalP(l))
        l2 = str2regexp('(a+b)(a+b)').toNFA()
        self.assertTrue(p.maximalP(l, l2))
        self.assertEqual(p.notMaximalW(l1, l2), 'aa')

    def test_CodeProp(self):
        """ UDCodeProp tests"""
        l = str2regexp('aab*+baa').toNFA()
        b = UDCodeProp({'a', 'b'})
        foo = b.notSatisfiesW(l)
        self.assertNotEqual(foo[0], foo[1])
        self.assertEqual("".join(x for x in foo[0]), "".join(x for x in foo[1]))
        l = str2regexp('aab*').toNFA()
        self.assertTrue(b.satisfiesP(l))

    def test_TrajProp(self):
        """ Test Trajectory Code Property"""
        p = buildTrajPropS("1*0*1*", {'a', 'b', 'c'})
        a = fio.readOneFromFile("test/DFA-ac+bba.fa")
        self.assertTrue(p.satisfiesP(a))
        a = fio.readOneFromFile("test/DFA-ab#.fa")
        r = re.compile('^(?P<s>.*)#.*(?P=s).*$')
        i, j = p.notSatisfiesW(a)
        if len(i) < len(j):
            x = i + "#" + j
        else:
            x = j + "#" + i
        self.assertTrue(r.match(x))
        a = fio.readOneFromFile("test/DFA-ab#a.fa")
        self.assertFalse(p.maximalP(a))
        w = p.notMaximalW(a, str2regexp('(a+b)*').toNFA())
        self.assertFalse(a.evalWordP(w))
        self.assertTrue(p.satisfiesP(fl.FL([w]).trieFA().toNFA() | a))
        l = fl.FL(['aa', 'ab', 'ba', 'bb']).trieFA().toNFA()
        self.assertTrue(p.maximalP(l, str2regexp('(a+b)*').toNFA()))

    def test_ErrorDetectProp(self):
        """ Test Error Detecting Code Property """
        p = buildErrorDetectPropF("test/P-ip-infix.fa")
        a = fio.readOneFromFile("test/DFA-ac+bba.fa")
        self.assertTrue(p.satisfiesP(a))
        a = fio.readOneFromFile("test/DFA-ab#.fa")
        r = re.compile('^(?P<s>.*)#.*(?P=s).*$')
        i, j = p.notSatisfiesW(a)
        if len(i) < len(j):
            x = i + "#" + j
        else:
            x = j + "#" + i
        self.assertTrue(r.match(x))
        a = fio.readOneFromFile("test/DFA-ab#a.fa")
        self.assertFalse(p.maximalP(a))
        w = p.notMaximalW(a)
        self.assertFalse(a.evalWordP(w))
        self.assertTrue(p.satisfiesP(fl.FL([w]).trieFA().toNFA() | a))
        l = fl.FL(['aa', 'ab', 'ba', 'bb']).trieFA().toNFA()
        l1 = fl.FL(['ab', 'ba', 'bb']).trieFA().toNFA()
        self.assertTrue(p.maximalP(l))
        l2 = str2regexp('(a+b)(a+b)').toNFA()
        self.assertTrue(p.maximalP(l, l2))
        self.assertEqual(p.notMaximalW(l1, l2), 'aa')
        p = buildErrorDetectPropF("test/TR-sub1.ab.fa")
        a = fio.readOneFromFile("test/DFA-EvenBMult03A-FAdo.fa")
        self.assertTrue(p.satisfiesP(a))
        a = str2regexp("aa+ab+bbbbb").toNFA()
        self.assertEqual(sorted(list(p.notSatisfiesW(a))), ['aa', 'ab'])

    def testErrorCorrectProp(self):
        p = buildErrorCorrectPropF("test/TR-sub1.ab.fa")
        a = str2regexp("aaa+bbb").toNFA()
        u = str2regexp("(a+b)(a+b)(a+b)").toNFA()
        self.assertTrue(p.maximalP(a, u))
        self.assertTrue(p.satisfiesP(a))
        u = str2regexp("(a+b)(a+b)(a+b)(a+b)").toNFA()
        self.assertTrue(len(p.notMaximalW(a, u)) >= 4)

    def testPrefixProperty(self):
        """ Test Prefix Code Property """
        p = buildPrefixProperty({'a', 'b'})
        a = fl.FL(['b', 'ab', 'aa']).trieFA().toDFA()
        self.assertTrue(p.satisfiesP(a))
        self.assertTrue(p.maximalP(a))
        a = fl.FL(['aa', 'ab']).trieFA().toDFA()
        u = fl.FL(['aa', 'ab', 'bb']).trieFA().toDFA()
        self.assertEqual(p.notMaximalW(a, u), 'bb')
        a = fl.FL(['b', 'ba', 'aa']).toDFA()
        self.assertFalse(p.satisfiesP(a))
        self.assertEqual(sorted(list(p.notSatisfiesW(a.toNFA()))), ['b', 'ba'])
        a = str2regexp("b+ab").toNFA()
        self.assertEqual(p.notMaximalW(a), 'aa')
        self.assertTrue(p.satisfiesP(a))

    def testEditDistance(self):
        """ Test editDistanceW"""
        self.assertEqual(editDistanceW(str2regexp('abbabc+bbaba').toNFA())[0], 2)
        self.assertEqual(editDistanceW(str2regexp('(abbabc)*+(bbaba)*').toNFA())[0], 2)

    def testExponentialDensity(self):
        """ Test exponentialDensityP """
        self.assertTrue(exponentialDensityP(str2regexp('(ab+abb)*+(aa)*').toNFA()))
        self.assertFalse(exponentialDensityP(str2regexp('(ab+abab)*+(aa)*').toNFA()))

    def testCombinedProperty(self):
        """ Test combined properties """
        a = str2regexp('a(bb)*a').toNFA()
        p1 = buildPrefixProperty(a.Sigma)
        p2 = buildSuffixProperty(a.Sigma)
        p12 = p1 & p2
        self.assertTrue(p12.satisfiesP(a))
        b = str2regexp('ab(bb)*bab+baaa+aa').toNFA()
        self.assertEqual(sorted(list(p12.notSatisfiesW(b))), ['aa', 'baaa'])
        p3 = buildIPTPropF('test/P-ip-infix.fa')
        p4 = buildIPTPropF('test/TR-sub1.ab.fa')
        p34 = p3 & p4
        self.assertTrue(p34.satisfiesP(a))
        self.assertEqual(sorted(list(p34.notSatisfiesW(b))), ['aa', 'baaa'])
        c = str2regexp('a(bb)*a+ababba').toNFA()
        s1, s2 = p34.notSatisfiesW(c)
        self.assertTrue(s1.find(s2) or s2.find(s1) or (len(s1) == len(s2) and hammingdist(s1, s2) == 1))
        self.assertEqual(sorted(list(p34.notSatisfiesW(c))), ['ababba', 'abbbba'])
        p3a = buildIATPropF('test/P-infix.fa')
        p3a4 = p3a & p4
        self.assertTrue(p3a4.satisfiesP(a))
        self.assertEqual(sorted(list(p3a4.notSatisfiesW(b))), ['aa', 'baaa'])
        p43a = p4 & p3a
        self.assertTrue(p43a.satisfiesP(a))
        self.assertEqual(sorted(list(p43a.notSatisfiesW(b))), ['aa', 'baaa'])

    def testInfixSAT_InDiffPropertyFormats(self):
        """ Test the same property using different descriptions of the property"""
        a = str2regexp('ab(bb)*a+bbbbb+abbabb').toNFA()  # not infix code: bbbbb in ab(bb)*a
        p1 = buildInfixProperty(a.Sigma)  # infix as fixed
        p2 = buildTrajPropS('1*0*1*', a.Sigma)  # infix as trajectory expr
        p3 = buildIATPropF('test/P-infix.fa')  # infix as inp. altering SFT
        p4 = buildIPTPropF('test/P-ip-infix.fa')  # infix as inp. preserving SFT
        (s1, s2) = p1.notSatisfiesW(a)
        self.assertTrue(s1.find(s2) >= 0 or s2.find(s1) >= 0)
        (s1, s2) = p3.notSatisfiesW(a)
        self.assertTrue(s1.find(s2) >= 0 or s2.find(s1) >= 0)
        (s1, s2) = p4.notSatisfiesW(a)
        self.assertTrue(s1.find(s2) >= 0 or s2.find(s1) >= 0)
        (s1, s2) = p2.notSatisfiesW(a)
        self.assertTrue(s1.find(s2) >= 0 or s2.find(s1) >= 0)

    def testOutixSAT_InDiffPropertyFormats(self):
        """ Test the same property using different descriptions of the property"""
        b = str2regexp('aabb+baa+bbb').toNFA()  # is outfix code: not both xy and xuy in b
        p1 = buildOutfixProperty(b.Sigma)
        p2 = buildTrajPropS('1*0*1*', b.Sigma)
        p3 = buildIATPropF('test/P-outfix.fa')
        p4 = buildIPTPropF('test/P-ip-outfix.fa')
        self.assertEqual(p1.notSatisfiesW(b), (None, None))
        self.assertEqual(p2.notSatisfiesW(b), (None, None))
        self.assertEqual(p3.notSatisfiesW(b), (None, None))
        self.assertEqual(p4.notSatisfiesW(b), (None, None))

    def testTransposeErrDetSAT_InDiffPropertyFormats(self):
        """ Test the same property using different descriptions of the property"""
        b = str2regexp('aabb+baa+bbb').toNFA()
        p1 = buildIPTPropF('test/P-transpose-1.ipt.fa')
        p2 = buildIPTPropF('test/P-transpose-1-using-subs.ipt.fa')
        p3 = buildIATPropF('test/P-transpose-1.iat.fa')
        p4 = buildErrorDetectPropF('test/P-transpose-1.ipt.fa')
        self.assertEqual(p1.notSatisfiesW(b), (None, None))
        self.assertEqual(p2.notSatisfiesW(b), (None, None))
        self.assertEqual(p3.notSatisfiesW(b), (None, None))
        self.assertEqual(p4.notSatisfiesW(b), (None, None))
        c = str2regexp('abaa*+baa+b(bb)*').toNFA()
        self.assertEqual(sorted(list(p1.notSatisfiesW(c))), ['aba', 'baa'])
        self.assertEqual(sorted(list(p2.notSatisfiesW(c))), ['aba', 'baa'])
        self.assertEqual(sorted(list(p3.notSatisfiesW(c))), ['aba', 'baa'])
        self.assertEqual(sorted(list(p4.notSatisfiesW(c))), ['aba', 'baa'])

    def testSuffix_MAX_InDiffPropertyFormats(self):
        """ Test the same property using different descriptions of the property"""
        a = str2regexp('a+ab+bb').toNFA()  # maximal suffix code
        p1 = buildSuffixProperty(a.Sigma)  # suffix as fixed
        p2 = buildTrajPropS('1*0*', a.Sigma)  # suffix as trajectory expr
        p3 = buildIATPropF('test/P-suffix.fa')  # suffix as inp. altering SFT
        p4 = buildIPTPropF('test/P-suffix-ipt.fa')  # suffix as inp. preserving SFT
        self.assertEqual(p1.notMaximalW(a), None)
        self.assertEqual(p3.notMaximalW(a), None)
        self.assertEqual(p4.notMaximalW(a), None)
        # self.assertEqual(p2.notMaximalW(a), None)   ## FAILS
        ##
        b = str2regexp('a+ab').toNFA()  # non maximal suffix code
        s = p1.notMaximalW(b)
        c = str2regexp('a+ab' + str(s)).toNFA()
        self.assertTrue(p1.satisfiesP(c))
        s = p3.notMaximalW(b)
        foo = 'a+ab' + str(s)
        c = str2regexp(foo).toNFA()
        self.assertTrue(p1.satisfiesP(c))
        s = p4.notMaximalW(b)
        c = str2regexp('a+ab' + str(s)).toNFA()
        self.assertTrue(p1.satisfiesP(c))
        s = p2.notMaximalW(b)  # raises exception PropertyNotSatisfied
        c = str2regexp('a+ab' + str(s)).toNFA()
        self.assertTrue(p1.satisfiesP(c))

    def test_long2base(self):
        def list2long(lt, q):
            lh = len(lt) - 1
            summ = 0
            while lh >= 0:
                summ += lt[lh] * (q ** lh)
                lh -= 1
            return summ

        self.assertEqual(50, list2long(long2base(50, 3), 3))
        self.assertEqual(77777777777777777777, list2long(long2base(77777777777777777777, 58), 58))

    def test_list2string(self):
        self.assertEqual('bcabbcaa', list2string([1, 2, 0, 1, 1, 2, 0, 0], {0: 'a', 1: 'b', 2: 'c'}))

    def test_notUniversalStatW(self):
        r = 'a((bb)*+(ba)*)'
        a = ~(str2regexp(r).toNFA().toDFA())
        for l in range(1, 26, 2):
            t = notUniversalStatW(a, l)
            if t[0] is not None:
                self.assertFalse(a.evalWordP(t[0]))

                # def test_notUniversalStatFileW(self):
                # Same as above, but records tests in a file that is created in the subdir madeTests
                # of the current directory
                # Requires to import skUtils.py
                # import skUtils
                # r = 'a((bb)*+(ba)*)'
                # a = ~(str2regexp(r).toNFA().toDFA())
                # # return a new open file f whose name is s and starts with tests
                # (f, s) = skUtils.makeNewFile('./madeTests', 'tests')
                # if f is None:
                # for l in range(1, 26, 2):
                #         t = notUniversalStatW(a, l, 20000)
                #         if t[0] is not None:
                #             self.assertFalse(a.evalWordP(t[0]))
                # else:
                #     f.write('\nLanguage = '+r+'\n')
                #     for l in range(1, 26, 2):
                #         t = notUniversalStatW(a, l, 20000)
                #         f.write('\n- l = '+str(l)+' --> '+str(t))
                #         if t[0] is not None:
                #             self.assertFalse(a.evalWordP(t[0]))
                #     f.close()
                #     print '\n\n!!! Note: new file created in the directory madeTests !!!\n'

    def test_constructCode(self):
        s = '@Transducer 1\n0 a a 0\n0 b b 0\n0 a @CEpsilon 1\n0 b @CEpsilon 1\n1 a @CEpsilon 1\n1 b @CEpsilon 1\n'
        p1 = buildIATPropS(s)
        n, l = 5, 5
        lt = constructCode(n, l, p1)
        a = fl.FL(lt).trieFA().toNFA()
        self.assertTrue(p1.satisfiesP(a))
        s = '@Transducer 1\n0 a a 0\n0 b b 0\n0 a b 1\n0 b a 1\n1 a a 1\n1 b b 1\n'
        p2 = buildIATPropS(s)
        n, l = 20, 10
        lt = constructCode(n, l, p2)
        a = fl.FL(lt).trieFA().toNFA()
        self.assertTrue(p2.satisfiesP(a))
        s = '@Transducer 1 2\n0 a a 0\n0 b b 0\n0 a b 1\n0 b a 1\n1 a a 1\n1 b b 1\n1 a b 2\n1 b a 2\n2 a a 2\n2 b b 2\n'
        p3 = buildIATPropS(s)
        n, l = 20, 10
        lt = constructCode(n, l, p3)
        a = fl.FL(lt).trieFA().toNFA()
        self.assertTrue(p3.satisfiesP(a))
        s = '@Transducer 0 1 2\n0 a a 0\n0 b b 0\n0 a b 1\n0 b a 1\n1 a a 1\n1 b b 1\n1 a b 2\n1 b a 2\n2 a a 2\n2 b b 2\n'
        p4 = buildIPTPropS(s)
        n, l = 16, 7
        lt = constructCode(n, l, p4)
        a = fl.FL(lt).trieFA().toNFA()
        self.assertTrue(p4.satisfiesP(a))
        s = '@Transducer 0 1 2\n0 a a 0\n0 b b 0\n0 a b 1\n0 b a 1\n0 a @CEpsilon 1\n0 b @CEpsilon 1\n' \
            + '0 @CEpsilon a 1\n0 @CEpsilon b 1\n1 a a 1\n1 b b 1\n1 a b 2\n1 b a 2\n1 a @CEpsilon 2\n' \
            + '1 b @CEpsilon 2\n1 @CEpsilon a 2\n1 @CEpsilon b 2\n2 a a 2\n2 b b 2\n'
        p5 = buildIPTPropS(s)
        n, l = 10, 7
        lt = constructCode(n, l, p5)
        a = fl.FL(lt).trieFA().toNFA()
        self.assertTrue(p5.satisfiesP(a))

    # def test_constructCodeFileW(self):
    #     # Same as above, but records the constructed code in a file created in the subdir madeCodes
    #     # of the current directory
    #     # Requires to import skUtils.py
    #         import skUtils
    #         # return a new open file f whose name is s and starts with code
    #         (f, s) = skUtils.makeNewFile('./madeCodes', 'code')
    #         if f is not None:
    #             s = '@Transducer 0 1 2\n0 a a 0\n0 b b 0\n0 a b 1\n0 b a 1\n'\
    #                 + '1 a a 1\n1 b b 1\n1 a b 2\n1 b a 2\n2 a a 2\n2 b b 2\n'
    #             p1 = buildIPTPropS(s)
    #             n, l = 16, 7
    #             # NOTE: The best code constructed had indeed 16 words out of the 16 requested.
    #             # It was the reversal of the Hamming code of length 7. It took about 220sec
    #             # ---see file madeCodes/code-2014-06-20-at-11-47-21.0.txt. Later constructions
    #             # took shorter time and made 16 element codes
    #             time1 = skUtils.timeNow()
    #             while True:
    #                 lt = constructCode(n, l, p1, False, None)
    #                 if len(lt) > 15: break
    #             time2 = skUtils.timeNow()
    #             f.write('IP transducer:\n'+s+'\n')
    #             f.write('Requested ' + str(n) + ' words of length ' + str(l) + '.\n')
    #             f.write('The following '+str(len(lt))+' words were constructed\n')
    #             f.write('(from '+time1+' to '+time2+'):\n-\n')
    #             for st in lt: f.write(st + '\n')
    #             f.close()

    def testOurPythonClasses(self):

        def _f1(p):
            self.assertTrue(isinstance(p, SuffixProp))
            self.assertTrue(isinstance(p, TrajProp))
            self.assertTrue(isinstance(p, IATProp))
            self.assertTrue(isinstance(p, IPTProp))
            self.assertTrue(isinstance(p, ErrDetectProp))
            self.assertTrue(isinstance(p, CodeProperty))

        p1 = buildSuffixProperty({'a', 'b'})
        _f1(p1)
        p2 = buildInfixProperty({'a', 'b'})
        _f1(p2)
        p3 = buildHypercodeProperty({'a', 'b'})
        _f1(p3)
        p2 = buildPrefixProperty({'a', 'b'})
        self.assertTrue(isinstance(p2, IPTProp))
        self.assertTrue(isinstance(p1 & p2, IATProp))
        ps1d = buildErrorDetectPropS(s1ts)
        self.assertTrue(isinstance(ps1d, ErrDetectProp))
        self.assertTrue(isinstance(ps1d, IPTProp))
        self.assertFalse(isinstance(ps1d, IATProp))
        self.assertFalse(isinstance(ps1d, TrajProp))
        self.assertTrue(isinstance(ps1d, CodeProperty))
        pud = buildUDCodeProperty({'a', 'b'})
        self.assertFalse(isinstance(pud, IPTProp))
        self.assertFalse(isinstance(pud, IATProp))
        self.assertFalse(isinstance(pud, TrajProp))
        self.assertTrue(isinstance(pud, CodeProperty))

    def testFixedPropHierarchy1(self):
        ppx = buildPrefixProperty({'a', 'b'})
        psx = buildSuffixProperty({'a', 'b'})
        pix = buildInfixProperty({'a', 'b'})
        pox = buildOutfixProperty({'a', 'b'})
        phc = buildHypercodeProperty({'a', 'b'})
        ppx1 = buildPrefixProperty({'a', 'b'})
        pud = buildUDCodeProperty({'a', 'b'})
        self.assertEqual(isSubclass(psx, ppx), 0)
        # The next test is not really appropriate, as UD_codes are not IPTProp
        self.assertEqual(isSubclass(pud, ppx), 2)
        self.assertEqual(isSubclass(psx, pix), 2)
        self.assertEqual(isSubclass(pox, ppx), 1)
        self.assertEqual(isSubclass(phc, pix), 1)
        self.assertEqual(isSubclass(pix, pox), 0)
        self.assertEqual(isSubclass(ppx1, ppx), 3)
        p0 = ppx & ppx1
        self.assertEqual(isSubclass(p0, ppx), 3)
        pbx = ppx & psx
        self.assertEqual(isSubclass(pbx, ppx), 1)
        p1 = pix & psx
        p2 = pix & pix
        self.assertEqual(isSubclass(p1, pix), 3)
        self.assertEqual(isSubclass(p2, pix), 3)
        self.assertEqual(isSubclass(p2, p1), 3)
        p3 = pix & pix & ppx
        self.assertEqual(isSubclass(p2, p3), 3)
        p4 = p3 & ppx
        self.assertEqual(isSubclass(p2, p4), 3)
        pbx1 = ppx & psx
        self.assertEqual(isSubclass(pbx1, pbx), 3)
        self.assertEqual(isSubclass(pix, pbx), 1)

    def testErrDetectPropHierarchy1(self):
        pixj = buildTrajPropS('1*0*1*', {'a', 'b'})
        ppx = buildPrefixProperty({'a', 'b'})
        pox = buildOutfixProperty({'a', 'b'})
        ps1d = buildErrorDetectPropS(s1ts)
        ps2d = buildErrorDetectPropS(s2ts)
        pix_s2d = pixj & ps2d
        ps2d_ix = ps2d & pixj
        ppx_s2d = ppx & ps2d
        pox_s2d = pox & ps2d
        pid2d = buildErrorDetectPropS(id2ts)
        self.assertEqual(isSubclass(pix_s2d, pixj), 1)
        self.assertEqual(isSubclass(ps2d_ix, pixj), 1)
        self.assertEqual(isSubclass(pox_s2d, ppx_s2d), 1)
        self.assertEqual(isSubclass(ps2d_ix, pixj), 1)
        self.assertEqual(isSubclass(pox_s2d & ppx, pox_s2d & pid2d), 2)
        self.assertEqual(isSubclass(pox_s2d & pid2d & ps1d, ppx_s2d & ppx), 1)
        self.assertEqual(isSubclass(pix_s2d, ps2d_ix), 3)
        self.assertEqual(isSubclass(pix_s2d, pix_s2d), 3)


if __name__ == '__main__':
    unittest.main()
