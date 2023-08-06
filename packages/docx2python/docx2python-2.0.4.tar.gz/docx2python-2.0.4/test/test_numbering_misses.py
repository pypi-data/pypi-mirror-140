#!/usr/bin/env python3
# last modified: 220228 19:21:28
"""Match word with broken numbering behavior.

:author: Shay Hill
:created: 2022-02-28

# GitHub issue #31

User ay2456 found a document that worked in Word, Google Docs, etc. However,
docx2python did not number the paragraphs correctly.

I looked through the xml and the problem seems to be the way Word and others deal
with missing first outline items:

If I had to guess, I think the creator of this file created an outline:

[1] A. First top level
[1][1] 1. First second level
[1][2] 2. Second second level
[2] B. Second top level

... then chopped off the head:


[1][1] 1. First second level
[1][2] 2. Second second level
[2] B. Second top level

When docxpython <= 2.0.3 sees this, it numbers the levels

[0][1] 1. First second level
[0][2] 2. Second second level
[1] A. Second top level

So, the B would be an A.

Word, et al apparently encounter the sublevel at [0][1] and assume the higher level
MUST exist. So, when this list is encountered for the first time at [?][1], Word
assumes [1][1] and docx2python <= 2.0.3 assumes [0][1].

The file from user ay2456 depends on this behavior, and probably so do a lot of
others. This file replaces the "head" of broken lists with a different list with the
same format. The new A is A because it's first, and the old B is still B because Word
won't assumed a had already been encountered when it found `1. First second level`.

Fortunately, ay2456 provided several test cases for me, so I know exactly where to
look for this behavior.
"""

from docx2python import docx2python
from pathlib import Path
from .conftest import RESOURCES


docx_file_name = RESOURCES / "numbering_misses.docx"
reader = docx2python(docx_file_name, html=True)


def test_numbering_ay2456_1() -> None:
    """"""
    list_A = reader.body[0][2][0][1]
    list_B = reader.body[0][2][0][6]
    list_C = reader.body[0][2][0][53]
    list_D = reader.body[0][2][0][59]

    assert list_A.startswith("<h2>A)")
    assert list_B.startswith("<h2>\tB)")
    assert list_C.startswith("<h2>\tC)")
    assert list_D.startswith("<h2>\tD)")


def test_numbering_ay2456_2() -> None:
    """"""
    list_II = reader.body[0][2][0][200]
    list_III = reader.body[0][2][0][295]
    assert list_II.startswith("<h1>II)")
    assert list_III.startswith("<h1>III)")
