"""
    pygments_clingo.clingo
    ~~~~~~~~~~~~~~~~~~~~~~

    Lexers for Logic Programs as supported by clingo.

    The lexer should cover most of the ASPCore language and thus also be usable
    with systems like dlv.

    :copyright: Copyright 2021-2022 by Roland Kaminski
    :license: MIT, see LICENSE for details.
"""

import re

from pygments.lexer import RegexLexer, bygroups, using
from pygments.lexers import PythonLexer, LuaLexer
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Number, Punctuation

__all__ = ['ClingoLexer']


def _script_lexer(name, lexer):
    return (rf'(?s)(\s*)(\()({name})(\))(\s*)(.*)(#end)(\s*)(\.)',
            bygroups(Text, # space
                     Punctuation, # (
                     Text, # python
                     Punctuation, # )
                     Text, # space
                     using(lexer),
                     Keyword, # end
                     Text, # space
                     Punctuation), # .)
            '#pop')


class ClingoLexer(RegexLexer):
    """
    Lexer for Clingo files.
    """
    name = 'Clingo'
    aliases = ['clingo']
    filenames = ['*.lp', '*.asp', '*.clingo', '*.gringo']
    mimetypes = ['text/plain']

    flags = re.UNICODE | re.MULTILINE

    tokens = {
        'root': [
            (r'%\*', Comment.Multiline, 'nested-comment'),
            (r'%.*', Comment.Single),
            (r'0x[0-9a-fA-F]+', Number.Hex),
            (r'\d+', Number.Integer),
            (r'"(\\n|\\"|\\\\|[^\\])*"', String.Double),
            (r':-', Punctuation),
            (r'[\[\](){}]', Punctuation),
            (r'((?<!:):-|(?<!:):~|\.(?!\.)|,(?!;)|;(?!;)|:(?!:))', Punctuation),
            (r'\&[_]*[a-z][a-zA-Z_]*', Keyword),
            (r'[/<=>+\-*\\?&@|:;~k.!]+', Operator),
            (r'(#count|#sum|#min|#max|#show|#const|#edge|#minimize|#maximize|'
             r'#defined|#heuristic|#project|#program|'
             r'#external|#theory|#end|not)\b', Keyword),
            (r'#script', Keyword, 'script'),
            (r'(#inf|#sup|#true|#false)\b', Keyword.Constant),
            (r"[_']*[A-Z][a-zA-Z'_]*", Name.Variable),
            (r'_', Name.Variable),
            (r"[_']*[a-z][a-zA-Z'_]*", Text),
            (r'\s', Text),
        ],
        'script': [
           _script_lexer('python', PythonLexer),
           _script_lexer('lua', LuaLexer),
           ('', Text, '#pop'), # fallback to normal parsing
        ],
        'nested-comment': [
            (r'\*%', Comment.Multiline, '#pop'),
            (r'%\*', Comment.Multiline, '#push'),
            (r'[^*%]+', Comment.Multiline),
            (r'[*%]', Comment.Multiline),
        ],
    }

    def get_tokens_unprocessed(self, text, stack=('root',)):
        '''
        This function adds special treatment for line label comments in Python
        scripts for usage with the minted package.

        In practice, it is very unlikely that there are comments starting with
        '#%\llabel{', so this code should not interfere with other use cases.
        '''
        for index, token, value in RegexLexer.get_tokens_unprocessed(self, text, stack):
            # Minted runs pygments two times. So we do the following:
            # - in the first pass we prepend a # to all line label comments, and
            # - in the second pass remove both #s.
            # We can only remove the leading #s in the second run because at
            # this point they still have to be tokenized as comments.
            if token is Comment.Single and value.startswith(r"#%\llabel{") and value.endswith("#"):
                yield index, token, f'#{value}'
            elif token is Comment.Single and value.startswith(r"##%\llabel{") and value.endswith("#"):
                yield index, token, value[2:]
            else:
                yield index, token, value

    def analyse_text(text):
        return ':-' in text
