Convenience functions for ANSI terminal colour sequences [color].

*Latest release 20220227*:
* New TerminalColors class parsing /etc/terminal-colors.d and honouring $*_COLORS.
* New colour_escape(code) to make the escape sequence for a colour code.
* New COLOUR_CODES mapping of known colour names.

Mapping and function for adding ANSI terminal colour escape sequences
to strings for colour highlighting of output.

## Function `colour_escape(code)`

Return the ANSI escape sequence to activate the colour `code`.
`code` may be an `int` or a `str` which indexes `COLOUR_CODES`.

## Function `colourise(s, colour=None, uncolour=None)`

Return a string enclosed in colour-on and colour-off ANSI sequences.

* `colour`: names the desired ANSI colour.
* `uncolour`: may be used to specify the colour-off colour;
  the default is 'normal' (from `NORMAL_COLOUR`).

## Function `colourise_patterns(s, patterns, default_colour=None)`

Colourise a string `s` according to `patterns`.

Parameters:
* `s`: the string.
* `patterns`: a sequence of patterns.
* `default_colour`: if a string pattern has no colon, or starts
  with a colon, use this colour;
  default "cyan" (from `DEFAULT_HIGHLIGHT`).

Each pattern may be:
* a string of the form "[colour]:regexp"
* a string containing no colon, taken to be a regexp
* a tuple of the form `(colour,regexp)`
* a regexp object

Returns the string with ANSI colour escapes embedded.

## Function `env_no_color(environ=None)`

Test the `$NO_COLOR` environment variable per the specification at
https://no-color.org/

## Function `make_pattern(pattern, default_colour=None)`

Convert a `pattern` specification into a `(colour,regexp)` tuple.

Parameters:
* `pattern`: the pattern to parse
* `default_colour`: the highlight colour,
  default "cyan" (from `DEFAULT_HIGHLIGHT`).

Each `pattern` may be:
* a string of the form "[colour]:regexp"
* a string containing no colon, taken to be a regexp
* a tuple of the form `(colour,regexp)`
* a regexp object

## Function `make_patterns(patterns, default_colour=None)`

Convert an iterable of pattern specifications into a list of
`(colour,regexp)` tuples.

Parameters:
* `patterns`: an iterable of patterns to parse
* `default_colour`: the highlight colour,
  default "cyan" (from `DEFAULT_HIGHLIGHT`).

Each pattern may be:
* a string of the form "[colour]:regexp"
* a string containing no colon, taken to be a regexp
* a tuple of the form (colour, regexp)
* a regexp object

## Class `TerminalColors`

A parser for `/etc/terminal-colors.d'` files.

*Method `TerminalColors.__init__(self, util_name=None, term_name=None, type_name=None, colors_dirpath=None, envvar=None)`*:
Initialise the `TerminalColors` instance.

Parameters:
* `util_name`: optional utility name, default from `sys.argv[0]`
* `term_name`: optional terminal name, default from the `$TERM` envvar
* `type_name`: optional type name, default `'enable'`
* `colors_dirpath`: optional specification files directory path,
  default from `TerminalColors.TERMINAL_COLORS_D`
* `envvar`: environment variable to override matches;
  the default `util_name+'_COLORS'`,
  thus `$LS_COLORS` if `util_name=='ls'`.
  That may be the value `False` if no environment variable should be an override.

*Method `TerminalColors.convert_sequence(sequence)`*:
Convert a colour specification to an escape sequence.

*Method `TerminalColors.find_specfile(self)`*:
Locate the most specific specification file matching our criteria.
Return `None` if no file matches.

*Property `TerminalColors.mapping`*:
The mapping of `name` to escape sequence.

*Method `TerminalColors.scan(self, path=None)`*:
Scan the colour specification in `path`
and yield `(name,escape_sequence)` tuples.

# Release Log



*Release 20220227*:
* New TerminalColors class parsing /etc/terminal-colors.d and honouring $*_COLORS.
* New colour_escape(code) to make the escape sequence for a colour code.
* New COLOUR_CODES mapping of known colour names.

*Release 20200729*:
* New env_no_color() test function honouring the $NO_COLOUR envvar per https://no-color.org/
* colourise: get the "normal" default from the global NORMAL_COLOUR.

*Release 20180726*:
greater markdowning of docstrings

*Release 20180725.2*:
some markdown, still release testing

*Release 20180725.1*:
Trivial changes, testing release process.

*Release 20180725*:
rename second colourise function to colourise_patterns, was shadowing things

*Release 20180422*:
* New function colourise to colour strings with regexp matches.
* New helper functions make_pattern and make_patterns to construct (colour, regexp)s from specifications.
* New public names NORMAL_COLOUR and DEFAULT_HIGHLIGHT.

*Release 20170902*:
Release metadata changes.

*Release 20160828*:
Add PyPI category, other minor tweaks.

*Release 20150112*:
PyPI release.

*Release 20150107*:
first standalone pypi release
