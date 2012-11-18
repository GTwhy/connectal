#!/usr/bin/python2
#
# grammar.py, part of Yapps 2 - yet another python parser system
# Copyright 1999-2003 by Amit J. Patel <amitp@cs.stanford.edu>
#
# This version of the Yapps 2 grammar can be distributed under the
# terms of the MIT open source license, either found in the LICENSE
# file included with the Yapps distribution
# <http://theory.stanford.edu/~amitp/yapps/> or at
# <http://www.opensource.org/licenses/mit-license.php>
#

"""Parser for Yapps grammars.

This file defines the grammar of Yapps grammars.  Naturally, it is
implemented in Yapps.  The grammar.py module needed by Yapps is built
by running Yapps on yapps_grammar.g.  (Holy circularity, Batman!)

"""

import sys, re
import parsetree

######################################################################
def cleanup_choice(rule, lst):
    if len(lst) == 0: return Sequence(rule, [])
    if len(lst) == 1: return lst[0]
    return parsetree.Choice(rule, *tuple(lst))

def cleanup_sequence(rule, lst):
    if len(lst) == 1: return lst[0]
    return parsetree.Sequence(rule, *tuple(lst))

def resolve_name(rule, tokens, id, args):
    if id in [x[0] for x in tokens]:
        # It's a token
        if args:
            print 'Warning: ignoring parameters on TOKEN %s<<%s>>' % (id, args)
        return parsetree.Terminal(rule, id)
    else:
        # It's a name, so assume it's a nonterminal
        return parsetree.NonTerminal(rule, id, args)


# Begin -- grammar generated by Yapps
import sys, re
import yappsrt

class ParserDescriptionScanner(yappsrt.Scanner):
    patterns = [
        ('"rule"', re.compile('rule')),
        ('"ignore"', re.compile('ignore')),
        ('"token"', re.compile('token')),
        ('"option"', re.compile('option')),
        ('":"', re.compile(':')),
        ('"parser"', re.compile('parser')),
        ('[ \t\r\n]+', re.compile('[ \t\r\n]+')),
        ('#.*?\r?\n', re.compile('#.*?\r?\n')),
        ('EOF', re.compile('$')),
        ('ATTR', re.compile('<<.+?>>')),
        ('STMT', re.compile('{{.+?}}')),
        ('ID', re.compile('[a-zA-Z_][a-zA-Z_0-9]*')),
        ('STR', re.compile('[rR]?\'([^\\n\'\\\\]|\\\\.)*\'|[rR]?"([^\\n"\\\\]|\\\\.)*"')),
        ('LP', re.compile('\\(')),
        ('RP', re.compile('\\)')),
        ('LB', re.compile('\\[')),
        ('RB', re.compile('\\]')),
        ('OR', re.compile('[|]')),
        ('STAR', re.compile('[*]')),
        ('PLUS', re.compile('[+]')),
        ('QUEST', re.compile('[?]')),
        ('COLON', re.compile(':')),
    ]
    def __init__(self, str):
        yappsrt.Scanner.__init__(self,None,['[ \t\r\n]+', '#.*?\r?\n'],str)

class ParserDescription(yappsrt.Parser):
    Context = yappsrt.Context
    def LINENO(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'LINENO', [])
        return 1 + self._scanner.get_input_scanned().count('\n')

    def Parser(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'Parser', [])
        self._scan('"parser"')
        ID = self._scan('ID')
        self._scan('":"')
        Options = self.Options(_context)
        Tokens = self.Tokens(_context)
        Rules = self.Rules(Tokens, _context)
        EOF = self._scan('EOF')
        return parsetree.Generator(ID,Options,Tokens,Rules)

    def Options(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'Options', [])
        opt = {}
        while self._peek() == '"option"':
            self._scan('"option"')
            self._scan('":"')
            Str = self.Str(_context)
            opt[Str] = 1
        if self._peek() not in ['"option"', '"token"', '"ignore"', 'EOF', '"rule"']:
            raise yappsrt.SyntaxError(charpos=self._scanner.get_prev_char_pos(), context=_context, msg='Need one of ' + ', '.join(['"option"', '"token"', '"ignore"', 'EOF', '"rule"']))
        return opt

    def Tokens(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'Tokens', [])
        tok = []
        while self._peek() in ['"token"', '"ignore"']:
            _token = self._peek()
            if _token == '"token"':
                self._scan('"token"')
                ID = self._scan('ID')
                self._scan('":"')
                Str = self.Str(_context)
                tok.append( (ID,Str) )
            elif _token == '"ignore"':
                self._scan('"ignore"')
                self._scan('":"')
                Str = self.Str(_context)
                tok.append( ('#ignore',Str) )
            else:
                raise yappsrt.SyntaxError(_token[0], 'Could not match Tokens')
        if self._peek() not in ['"token"', '"ignore"', 'EOF', '"rule"']:
            raise yappsrt.SyntaxError(charpos=self._scanner.get_prev_char_pos(), context=_context, msg='Need one of ' + ', '.join(['"token"', '"ignore"', 'EOF', '"rule"']))
        return tok

    def Rules(self, tokens, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'Rules', [tokens])
        rul = []
        while self._peek() == '"rule"':
            LINENO = self.LINENO(_context)
            self._scan('"rule"')
            ID = self._scan('ID')
            OptParam = self.OptParam(_context)
            self._scan('":"')
            ClauseA = self.ClauseA(ID, tokens, _context)
            rul.append( (ID, OptParam, ClauseA) )
        if self._peek() not in ['"rule"', 'EOF']:
            raise yappsrt.SyntaxError(charpos=self._scanner.get_prev_char_pos(), context=_context, msg='Need one of ' + ', '.join(['"rule"', 'EOF']))
        return rul

    def ClauseA(self, rule, tokens, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'ClauseA', [rule, tokens])
        ClauseB = self.ClauseB(rule, tokens, _context)
        v = [ClauseB]
        while self._peek() == 'OR':
            OR = self._scan('OR')
            ClauseB = self.ClauseB(rule, tokens, _context)
            v.append(ClauseB)
        if self._peek() not in ['OR', 'RP', 'RB', '"rule"', 'EOF']:
            raise yappsrt.SyntaxError(charpos=self._scanner.get_prev_char_pos(), context=_context, msg='Need one of ' + ', '.join(['OR', 'RP', 'RB', '"rule"', 'EOF']))
        return cleanup_choice(rule, v)

    def ClauseB(self, rule, tokens, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'ClauseB', [rule, tokens])
        v = []
        while self._peek() in ['STR', 'ID', 'LP', 'LB', 'STMT']:
            ClauseC = self.ClauseC(rule, tokens, _context)
            v.append(ClauseC)
        if self._peek() not in ['STR', 'ID', 'LP', 'LB', 'STMT', 'OR', 'RP', 'RB', '"rule"', 'EOF']:
            raise yappsrt.SyntaxError(charpos=self._scanner.get_prev_char_pos(), context=_context, msg='Need one of ' + ', '.join(['STR', 'ID', 'LP', 'LB', 'STMT', 'OR', 'RP', 'RB', '"rule"', 'EOF']))
        return cleanup_sequence(rule, v)

    def ClauseC(self, rule, tokens, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'ClauseC', [rule, tokens])
        ClauseD = self.ClauseD(rule, tokens, _context)
        _token = self._peek()
        if _token == 'PLUS':
            PLUS = self._scan('PLUS')
            return parsetree.Plus(rule, ClauseD)
        elif _token == 'STAR':
            STAR = self._scan('STAR')
            return parsetree.Star(rule, ClauseD)
        elif _token == 'QUEST':
            QUEST = self._scan('QUEST')
            return parsetree.Option(rule, ClauseD)
        elif _token not in ['"ignore"', '"token"', '"option"', '":"', '"parser"', 'ATTR', 'COLON']:
            return ClauseD
        else:
            raise yappsrt.SyntaxError(_token[0], 'Could not match ClauseC')

    def ClauseD(self, rule, tokens, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'ClauseD', [rule, tokens])
        _token = self._peek()
        if _token == 'STR':
            STR = self._scan('STR')
            t = (STR, eval(STR,{},{}))
            if t not in tokens: tokens.insert( 0, t )
            print "attempted to add token in middle of grammar!!!!", t
            sys.exit(-1)
            return parsetree.Terminal(rule, STR)
        elif _token == 'ID':
            ID = self._scan('ID')
            OptParam = self.OptParam(_context)
            return resolve_name(rule, tokens, ID, OptParam)
        elif _token == 'LP':
            LP = self._scan('LP')
            ClauseA = self.ClauseA(rule, tokens, _context)
            RP = self._scan('RP')
            return ClauseA
        elif _token == 'LB':
            LB = self._scan('LB')
            ClauseA = self.ClauseA(rule, tokens, _context)
            RB = self._scan('RB')
            return parsetree.Option(rule, ClauseA)
        elif _token == 'STMT':
            STMT = self._scan('STMT')
            return parsetree.Eval(rule, STMT[2:-2])
        else:
            raise yappsrt.SyntaxError(_token[0], 'Could not match ClauseD')

    def OptParam(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'OptParam', [])
        _token = self._peek()
        if _token == 'ATTR':
            ATTR = self._scan('ATTR')
            return ATTR[2:-2]
        elif _token not in ['"ignore"', '"token"', '"option"', '"parser"', 'COLON']:
            return ''
        else:
            raise yappsrt.SyntaxError(_token[0], 'Could not match OptParam')

    def Str(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'Str', [])
        STR = self._scan('STR')
        return eval(STR,{},{})


def parse(rule, text):
    P = ParserDescription(ParserDescriptionScanner(text))
    return yappsrt.wrap_error_reporter(P, rule)

# End -- grammar generated by Yapps


