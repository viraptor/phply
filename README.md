# phply

phply is a parser for the PHP programming language written using PLY, a
Lex/YACC-style parser generator toolkit for Python.

## Why?

Good question. Because I'm crazy. Because it seemed possible.

Things I'm interested in doing with it:

* Converting PHP code to Python
* Running PHP templates in a Python environment
* Learning more about parsing "industrial" languages, warts and all

## What does it stand for?

* phply -> PHP PLY
* phply -> PHP Hypertext Preprocessor Python Lex YACC
* phply -> PHP Hypertext Preprocessor Hypertext Preprocessor Python Lex Yet Another Compiler Compiler
* (... to be completed ...)

## How do you pronounce it?

If you're conservative, it's pronounced "pee aich ply". If you're liberal,
it's "fiply". And if you're anarchist, pronounce it however you want. Who am I
to tell you what to do?

## What's working?

* Lexer matching the standard PHP lexer token-for-token
* Parser and abstract syntax tree for most of the PHP grammar
* Script to convert PHP source to JSON-based ASTs
* Script to convert PHP source to Jinja2 source (experimental)

## What's not?

Some things can't be parsed yet. They are getting fewer by the day, but there
is still a fair amount of work to do:

* Labels and goto
* Some other stuff, probably

## Who's working on it?

See the [AUTHORS](https://github.com/viraptor/phply/blob/master/AUTHORS) file.

## Troubleshooting

### Couldn't create 'phply.parsetab'

Phply relies on `ply` to generate and cache some tables required for the parser.
These have been generated with the latest available version of ply for the phply
release. If you installed phply under a different user and a new `ply` was
released, the parsetab file cannot be automatically updated. Your options are
to:

* raise an issue for phply
* rebuild the package yourself

## How do I use it?

* Lexer test: python phply/phplex.py
* Parser test: python phply/phpparse.py
* JSON dump: cd tools; python php2json.py < input.php > output.json
* Jinja2 conversion: cd tools; python php2jinja.py < input.php > output.html
* Fork me on GitHub and start hacking :)
