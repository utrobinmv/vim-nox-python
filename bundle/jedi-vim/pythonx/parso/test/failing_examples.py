# -*- coding: utf-8 -*-
import sys
from textwrap import dedent


def indent(code):
    lines = code.splitlines(True)
    return ''.join([' ' * 2 + line for line in lines])


def build_nested(code, depth, base='def f():\n'):
    if depth == 0:
        return code

    new_code = base + indent(code)
    return build_nested(new_code, depth - 1, base=base)


FAILING_EXAMPLES = [
    '1 +',
    '?',
    'continue',
    'break',
    'return',
    'yield',

    # SyntaxError from Python/ast.c
    'f(x for x in bar, 1)',
    'from foo import a,',
    'from __future__ import whatever',
    'from __future__ import braces',
    'from .__future__ import whatever',
    'def f(x=3, y): pass',
    'lambda x=3, y: x',
    '__debug__ = 1',
    'with x() as __debug__: pass',
    # Mostly 3.6 relevant
    '[]: int',
    '[a, b]: int',
    '(): int',
    '(()): int',
    '((())): int',
    '{}: int',
    'True: int',
    '(a, b): int',
    '*star,: int',
    'a, b: int = 3',
    'foo(+a=3)',
    'f(lambda: 1=1)',
    'f(x=1, x=2)',
    'f(**x, y)',
    'f(x=2, y)',
    'f(**x, *y)',
    'f(**x, y=3, z)',
    'a, b += 3',
    '(a, b) += 3',
    '[a, b] += 3',
    # All assignment tests
    'lambda a: 1 = 1',
    '[x for x in y] = 1',
    '{x for x in y} = 1',
    '{x:x for x in y} = 1',
    '(x for x in y) = 1',
    'None = 1',
    '... = 1',
    'a == b = 1',
    '{a, b} = 1',
    '{a: b} = 1',
    '1 = 1',
    '"" = 1',
    'b"" = 1',
    'b"" = 1',
    '"" "" = 1',
    '1 | 1 = 3',
    '1**1 = 3',
    '~ 1 = 3',
    'not 1 = 3',
    '1 and 1 = 3',
    'def foo(): (yield 1) = 3',
    'def foo(): x = yield 1 = 3',
    'async def foo(): await x = 3',
    '(a if a else a) = a',
    'a, 1 = x',
    'foo() = 1',
    # Cases without the equals but other assignments.
    'with x as foo(): pass',
    'del bar, 1',
    'for x, 1 in []: pass',
    'for (not 1) in []: pass',
    '[x for 1 in y]',
    '[x for a, 3 in y]',
    '(x for 1 in y)',
    '{x for 1 in y}',
    '{x:x for 1 in y}',
    # Unicode/Bytes issues.
    r'u"\x"',
    r'u"\"',
    r'u"\u"',
    r'u"""\U"""',
    r'u"\Uffffffff"',
    r"u'''\N{}'''",
    r"u'\N{foo}'",
    r'b"\x"',
    r'b"\"',
    '*a, *b = 3, 3',
    'async def foo(): yield from []',
    'yield from []',
    '*a = 3',
    'del *a, b',
    'def x(*): pass',
    '(%s *d) = x' % ('a,' * 256),
    '{**{} for a in [1]}',

    # Parser/tokenize.c
    r'"""',
    r'"',
    r"'''",
    r"'",
    r"\blub",
    # IndentationError: too many levels of indentation
    build_nested('pass', 100),

    # SyntaxErrors from Python/symtable.c
    'def f(x, x): pass',
    'nonlocal a',

    # IndentationError
    ' foo',
    'def x():\n    1\n 2',
    'def x():\n 1\n  2',
    'if 1:\nfoo',
    'if 1: blubb\nif 1:\npass\nTrue and False',

    # f-strings
    'f"{}"',
    r'f"{\}"',
    'f"{\'\\\'}"',
    'f"{#}"',
    "f'{1!b}'",
    "f'{1:{5:{3}}}'",
    "f'{'",
    "f'{'",
    "f'}'",
    "f'{\"}'",
    "f'{\"}'",
    # Now nested parsing
    "f'{continue}'",
    "f'{1;1}'",
    "f'{a;}'",
    "f'{b\"\" \"\"}'",
]

GLOBAL_NONLOCAL_ERROR = [
    dedent('''
        def glob():
            x = 3
            x.z
            global x'''),
    dedent('''
        def glob():
            x = 3
            global x'''),
    dedent('''
        def glob():
            x
            global x'''),
    dedent('''
        def glob():
            x = 3
            x.z
            nonlocal x'''),
    dedent('''
        def glob():
            x = 3
            nonlocal x'''),
    dedent('''
        def glob():
            x
            nonlocal x'''),
    # Annotation issues
    dedent('''
        def glob():
            x[0]: foo
            global x'''),
    dedent('''
        def glob():
            x.a: foo
            global x'''),
    dedent('''
        def glob():
            x: foo
            global x'''),
    dedent('''
        def glob():
            x: foo = 5
            global x'''),
    dedent('''
        def glob():
            x: foo = 5
            x
            global x'''),
    dedent('''
        def glob():
            global x
            x: foo = 3
        '''),
    # global/nonlocal + param
    dedent('''
        def glob(x):
            global x
        '''),
    dedent('''
        def glob(x):
            nonlocal x
        '''),
    dedent('''
        def x():
            a =3
            def z():
                nonlocal a
                a = 3
                nonlocal a
        '''),
    dedent('''
        def x():
            a = 4
            def y():
                global a
                nonlocal a
        '''),
    # Missing binding of nonlocal
    dedent('''
        def x():
            nonlocal a
        '''),
    dedent('''
        def x():
            def y():
                nonlocal a
        '''),
    dedent('''
        def x():
            a = 4
            def y():
                global a
                print(a)
                def z():
                    nonlocal a
        '''),
]

if sys.version_info >= (3, 6):
    FAILING_EXAMPLES += GLOBAL_NONLOCAL_ERROR
if sys.version_info >= (3, 5):
    FAILING_EXAMPLES += [
        # Raises different errors so just ignore them for now.
        '[*[] for a in [1]]',
        # Raises multiple errors in previous versions.
        'async def bla():\n def x():  await bla()',
    ]
if sys.version_info >= (3, 4):
    # Before that del None works like del list, it gives a NameError.
    FAILING_EXAMPLES.append('del None')
if sys.version_info >= (3,):
    FAILING_EXAMPLES += [
        # Unfortunately assigning to False and True do not raise an error in
        # 2.x.
        '(True,) = x',
        '([False], a) = x',
        # A symtable error that raises only a SyntaxWarning in Python 2.
        'def x(): from math import *',
        # unicode chars in bytes are allowed in python 2
        'b"??"',
        # combining strings and unicode is allowed in Python 2.
        '"s" b""',
        '"s" b"" ""',
        'b"" "" b"" ""',
    ]
if sys.version_info >= (3, 6):
    FAILING_EXAMPLES += [
        # Same as above, but for f-strings.
        'f"s" b""',
        'b"s" f""',

        # f-string expression part cannot include a backslash
        r'''f"{'\n'}"''',
    ]
FAILING_EXAMPLES.append('[a, 1] += 3')

if sys.version_info[:2] == (3, 5):
    # yields are not allowed in 3.5 async functions. Therefore test them
    # separately, here.
    FAILING_EXAMPLES += [
        'async def foo():\n yield x',
        'async def foo():\n yield x',
    ]
else:
    FAILING_EXAMPLES += [
        'async def foo():\n yield x\n return 1',
        'async def foo():\n yield x\n return 1',
    ]


if sys.version_info[:2] <= (3, 4):
    # Python > 3.4 this is valid code.
    FAILING_EXAMPLES += [
        'a = *[1], 2',
        '(*[1], 2)',
    ]

if sys.version_info[:2] < (3, 8):
    FAILING_EXAMPLES += [
        # Python/compile.c
        dedent('''\
            for a in [1]:
                try:
                    pass
                finally:
                    continue
            '''),  # 'continue' not supported inside 'finally' clause"
    ]

if sys.version_info[:2] >= (3, 8):
    # assignment expressions from issue#89
    FAILING_EXAMPLES += [
        # Case 2
        '(lambda: x := 1)',
        '((lambda: x) := 1)',
        # Case 3
        '(a[i] := x)',
        '((a[i]) := x)',
        '(a(i) := x)',
        # Case 4
        '(a.b := c)',
        '[(i.i:= 0) for ((i), j) in range(5)]',
        # Case 5
        '[i:= 0 for i, j in range(5)]',
        '[(i:= 0) for ((i), j) in range(5)]',
        '[(i:= 0) for ((i), j), in range(5)]',
        '[(i:= 0) for ((i), j.i), in range(5)]',
        '[[(i:= i) for j in range(5)] for i in range(5)]',
        '[i for i, j in range(5) if True or (i:= 1)]',
        '[False and (i:= 0) for i, j in range(5)]',
        # Case 6
        '[i+1 for i in (i:= range(5))]',
        '[i+1 for i in (j:= range(5))]',
        '[i+1 for i in (lambda: (j:= range(5)))()]',
        # Case 7
        'class Example:\n [(j := i) for i in range(5)]',
        # Not in that issue
        '(await a := x)',
        '((await a) := x)',
        # new discoveries
        '((a, b) := (1, 2))',
        '([a, b] := [1, 2])',
        '({a, b} := {1, 2})',
        '({a: b} := {1: 2})',
        '(a + b := 1)',
        '(True := 1)',
        '(False := 1)',
        '(None := 1)',
        '(__debug__ := 1)',
    ]
