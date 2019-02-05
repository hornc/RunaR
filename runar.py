#!/usr/bin/env python3
import argparse
import re

"""
RunaR interpreter....
very WIP, still figuring out the language spec.
Expect most things to change.
"""

FUTHARK = 'ᚠᚢᚦᚬᚱᚴᚼᚾᛁᛅᛋᛏᛒᛘᛚᛦ'
SEP     = '᛬'
HEX     = re.compile('[0-9a-f]')
EGILL   = """ᚱᚢᚾᛅᛦ

  Skalat maðr Rúnaʀ rísta,
  nema ráða vel kunni;
  þat verðr mǫrgum manni,
  es of myrkan staf villisk;
  sák á telgðu tálkni
  tíu launstafi ristna,
  þat hefr lauka lindi
  langs oftrega fengit.
    -- Egill Skallagrímsson.

"""


class Pointer():
    """
    Instruction pointer.
    Sola gjekk i ringen.
    """

    x = 0
    y = 0
    symbol = ''
    origin = None
    v = (1, 0)
    wrap = (0, 0) # wrap behaviour
    value = 0
    HEADINGS = {'ᛌ': (1, 0), 'ᛍ': (0, 1), 'ᛊ': (1, 0), 'ᛋ': (0, 1)}
    WRAPINGS = {'ᛌ': (0, 0), 'ᛍ': (0, 0), 'ᛊ': (0, 1), 'ᛋ': (1, 0)}

    def __init__(self, x, y, symbol):
        self.x = x
        self.y = y
        self.origin = (x, y)
        self.symbol = symbol
        self.v = self.HEADINGS[symbol]
        self.wrap = self.WRAPINGS[symbol]

    def advance(self):
        """ Move pointer by v"""
        self.x += self.v[0]
        self.y += self.v[1]
        return self.pos()

    def change_dir(self, degrees):
        if degrees == 90:
            self.v = self.v[::-1]
        if degrees == -90:
            self.v = self.v[::-1]
        if degrees == 180:
            self.v = (-self.v[0], -self.v[1])

        if degrees == 'RR':  # rotate right
            self.v = self.v[::-1]
            self.v = (-self.v[0], self.v[1])

    def pos(self):
        return (self.x, self.y)

    def output(self):
        if self.value is None:
            return print(SEP, end='')
        return print(FUTHARK[self.value], end='')


class Grid():
    """
    Nornar spinnande, lagnadar bindande.
    """

    STARTS = re.compile('[ᛌᛍᛊᛋ]')
    grid = []
    pointers = []
    stack = [0]
    def __init__(self, sourcefile):
        with open(sourcefile, 'r', encoding='utf_8') as f:
            # Need to convert runic pentimal unicode combining characters to single characters
            self.grid = [self.pentimal_convert(line.rstrip()) for line in f.readlines()]
            self.pointers = [Pointer(m.start(), i, m.group(0)) for i,line in enumerate(self.grid) for m in re.finditer(self.STARTS, line)]

    def pentimal_convert(self, s):
        """ Converts pentimal runic unicode with combining diacritics to single characters (hex) """
        VALUES = {'ᛁ': 0, '\u0335': 1, '\u0304': 1, '\u0333': 2, '\u033f': 2, '\u030a': 10, '\u0325': 10, '\u0339': 5, '\u0357': 5}
        def pent(c):
            if len(c) == 1:
                return c
            else:
                return hex(sum([VALUES[n] for n in c])-1)[-1]
        return ''.join([pent(c) for c in re.findall(u'.[\u0300-\u036F]*', s)])

    def main(self):
        """ main program loop """
        for p in  self.pointers:
            c = self.grid[p.y][p.x]
            if DEBUG:
                print('DEBUG command: ', c)
            if re.match(HEX, c): # number
                p.value = int(c, 16)
            if c == 'ᚹ': # clear
                p.value = None 
            if c == 'ᛧ': # end
                return True
            if c == 'ᚭ': # output
                p.output()
            if c == 'ᛙ':
                self.stack.append(p.value)
            if c == 'ᛁ': # ice wall
                p.change_dir(180)
            if c == 'ᛚ':
                p.change_dir(90)
            if c == 'ᛐ':
                p.change_dir(-90)

            if c == 'ᚿ': # rot right 90 degs
                p.change_dir('RR')
            if c == 'ᚱ':
                p.v = (1, 0)
            if c == 'ᚢ':
                p.v = (-1, 0)
            if c == 'ᚷ': # subtract
                p.value -= self.stack.pop()
            if c == 'ᛟ': # add
                p.value += self.stack.pop()
            if c == 'ᚴ': # divide
                p.value = (p.value + 1) // (self.stack.pop() + 1) - 1
            if c == 'ᚠ': # multiply
                p.value = (p.value + 1) * (self.stack.pop() + 1) - 1
            if c == 'ᚦ':
                if p.value:
                    p.change_dir(180)
            self.pointer_advance(p)

    def pointer_advance(self, pointer):
        pos = pointer.advance()
        if pos[1] >= len(self.grid):
            pointer.y = 0
            pointer.x += pointer.wrap[0]
        if pos[1] < 0:
            pointer.y = len(self.grid) - 1
            pointer.x -= pointer.wrap[0]
        if pos[0] >= len(self.grid[pointer.y]):
            pointer.x = 0
            pointer.y += pointer.wrap[1]
        if pos[0] < 0:
            pointer.x = len(self.grid[pointer.y]) - 1
            pointer.y -= pointer.wrap[1]

    def peek(self):
        return self.stack[-1]


if __name__ == '__main__':
    """
    Galdrar groande.
    """

    parser = argparse.ArgumentParser(description=EGILL + 'https://esolangs.org/wiki/ᚱᚢᚾᛅᛦ', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--debug', help='turn on debug output', action='store_true')
    parser.add_argument('file', help='source file to process')
    args = parser.parse_args()

    DEBUG = args.debug
    sourcefile = args.file
    g = Grid(sourcefile)
    print('GRID:', g.grid)
    print('POSITIONS: ', [s.pos() for s in g.pointers])

    while not g.main():
        if DEBUG:
            print('    POINTER VARS: :', end='')
            [p.output() for p in g.pointers]
        pass
