# -*- coding: utf-8 -*-
"""
    CleverCSS
    ~~~~~~~~~

    The Pythonic way of CSS files.

    To convert this into a normal css file just call the `convert`
    function in the clevercss module. It's that easy :-)

    Example::

        base_padding = 2px
        background_color = #eee
        text_color = #111
        link_color = #ff0000

        body:
            font-family: serif, sans-serif, 'Verdana', 'Times New Roman'
            color: $text_color
            padding->
                top: $base_padding + 2
                right: $base_padding + 3
                left: $base_padding + 3
                bottom: $base_padding + 2
            background-color: $background_color

        div.foo:
            width: "Hello World".length() * 20px
            foo: (foo, bar, baz, 42).join('/')

        a:
            color: $link_color
            &:hover:
                color: $link_color.darken(30%)
            &:active:
                color: $link_color.brighten(10%)

        div.navigation:
            height: 1.2em
            padding: 0.2em
            ul:
                margin: 0
                padding: 0
                list-style: none
                li:
                    float: left
                    height: 1.2em
                    a:
                        display: block
                        height: 1em
                        padding: 0.1em
            foo: (1 2 3).string()

        __END__
        this is ignored, but __END__ as such is completely optional.

    To get the converted example module as css just run this file as script
    with the "--eigen-test" parameter.

    Literals
    --------

    CleverCSS supports most of the standard CSS literals.  Some syntax
    elements are not supported by now, some will probably never.

    Strings:
        everything (except of dangling method calls and whitespace) that
        cannot be parsed with a different rule is considered being a
        string.  If you want to have whitespace in your strings or use
        something as string that would otherwise have a different semantic
        you can use double or single quotes.

        these are all valid strings::

            =
            foo-bar-baz
            "blub"
            'foo bar baz'
            Verdana

    Numbers
        Numbers are just that.  Numbers with unit postfix are values.

    Values
        Values are numbers with an associated unit.  Most obvious difference
        between those two are the different semantics in arithmetic
        operations.  Some units can be converted, some are just not compatible
        (for example you won't be able to convert 1em in percent because
         there is no fixed conversion possible)
        Additionally to the CSS supported colors this module supports the
        netscape color codes.

    Colors
        Colors are so far only supported in hexadecimal notation.  You can
        also use the `rgb()` literal to some amount.  But that means you
        cannot use "orange" as color.

    URLs:
        URLs work like strings, the only difference is that the syntax looks
        like ``url(...)``.

    Variables:
        variables are quite simple.  Once they are defined in the root section
        you can use them in every expression::

            foo = 42px

            div:
                width: $foo * 100;

    Lists:
        Sometimes you want to assign more than one element to a CSS rule.  For
        example if you work with font families.  In that situation just use
        the comma operator to define a list::

            font-family: Verdana, Arial, sans-serif

        Additionally lists have methods, you can for example do this (although
        probably completely useless in real world cases)::

            width: (1, 2, 3, 4).length() * 20


    Implicit Concatenation
    ----------------------

    CleverCSS ignores whitespace.  But whitespace keeps the tokens apart.  If
    the parser now stumbles upon something it doesn't know how to handle, it
    assumes that there was a whitespace.  In some situations CSS even requires
    that behavior::

        padding: 2px 3px

    But because CleverCSS has expressions this could lead to this situation::

        padding: $x + 1 $x + 2

    This if course works too because ``$x + 1`` is one expression and
    ``$x + 2`` another one.  This however can lead to code that is harder to
    read.  In that situation it's recommended to parentize the expressions::

        padding: ($x + 1) ($x + 2)

    or remove the whitespace between the operators::

        padding: $x+1 $x+2


    Operators
    ---------

    ``+``       add two numbers, a number and a value or two compatible
                values (for example ``1cm + 12mm``).  This also works as
                concatenate operator for strings.  Using this operator
                on color objects allows some basic color composition.
    ``-``       subtract one number from another, a number from a value
                or a value from a compatible one.  Like the plus operator
                this also works on colors.
    ``*``       Multiply numbers, numbers with a value.  Multiplying strings
                repeats it. (eg: ``= * 5`` gives '=====')
    ``/``       divide one number or value by a number.
    ``%``       do a modulo division on a number or value by a number.

    Keep in mind that whitespace matters. For example ``20% 10`` is something
    completely different than ``20 % 10``. The first one is an implicit
    concatenation expression with the values 20% and 10, the second one a
    modulo epression.  The same applies to ``no-wrap`` versus ``no - wrap``
    and others.

    Additionally there are two operators used to keep list items apart. The
    comma (``,``) and semicolon (``;``) operator both keep list items apart.

    If you want to group expressions you can use parentheses.

    Methods
    -------

    Objects have some methods you can call:

    - `Number.abs()`            get the absolute value of the number
    - `Number.round(places)`    round to (default = 0) places
    - `Value.abs()`             get the absolute value for this value
    - `Value.round(places)`     round the value to (default = 0) places
    - `Color.brighten(amount)`  brighten the color by amount percent of
                                the current lightness, or by 0 - 100.
                                brighening by 100 will result in white.
    - `Color.darken(amount)`    darken the color by amount percent of the
                                current lightness, or by 0 - 100.
                                darkening by 100 will result in black.
    - `String.length()`         the length of the string.
    - `String.upper()`          uppercase version of the string.
    - `String.lower()`          lowercase version of the string.
    - `String.strip()`          version with leading an trailing whitespace
                                removed.
    - `String.split(delim)`     return a list of substrings, splitted by
                                whitespace or delim.
    - `String.eval()`           eval a css rule inside of a string. For
                                example a string "42" would return the
                                number 42 when parsed. But this can also
                                contain complex expressions such as
                                "(1 + 2) * 3px".
    - `String.string()`         just return the string itself.
    - `List.length()`           number of elements in a list.
    - `List.join(delim)`        join a list by space char or delim.

    Additionally all objects and expressions have a `.string()` method that
    converts the object into a string, and a `.type()` method that returns
    the type of the object as string.

    If you have implicit concatenated expressions you can convert them into
    a list using the `list` method::

        (1 2 3 4 5).list()

    does the same as::

        1, 2, 3, 4, 5

    :copyright: Copyright 2007 by Armin Ronacher, Georg Brandl.
    :license: BSD License
"""
import re
import colorsys
import operator


VERSION = '0.1'

__all__ = ['convert']


# regular expresssions for the normal parser
_var_def_re = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)')
_def_re = re.compile(r'^([a-zA-Z-]+)\s*:\s*(.+)')
_line_comment_re = re.compile(r'(?<!:)//.*?$')

# list of operators
_operators = ['+', '-', '*', '/', '%', '(', ')', ';', ',']

# units and conversions
_units = ['em', 'ex', 'px', 'cm', 'mm', 'in', 'pt', 'pc', 'deg', 'rad'
          'grad', 'ms', 's', 'Hz', 'kHz', '%']
_conv = {
    'length': {
        'mm':       1.0,
        'cm':       10.0,
        'in':       25.4,
        'pt':       25.4 / 72,
        'pc':       25.4 / 6
    },
    'time': {
        'ms':       1.0,
        's':        1000.0
    },
    'freq': {
        'Hz':       1.0,
        'kHz':      1000.0
    }
}
_conv_mapping = {}
for t, m in _conv.iteritems():
    for k in m:
        _conv_mapping[k] = t
del t, m, k

# color literals
_colors = {
    'aliceblue': '#f0f8ff',
    'antiquewhite': '#faebd7',
    'aqua': '#00ffff',
    'aquamarine': '#7fffd4',
    'azure': '#f0ffff',
    'beige': '#f5f5dc',
    'bisque': '#ffe4c4',
    'black': '#000000',
    'blanchedalmond': '#ffebcd',
    'blue': '#0000ff',
    'blueviolet': '#8a2be2',
    'brown': '#a52a2a',
    'burlywood': '#deb887',
    'cadetblue': '#5f9ea0',
    'chartreuse': '#7fff00',
    'chocolate': '#d2691e',
    'coral': '#ff7f50',
    'cornflowerblue': '#6495ed',
    'cornsilk': '#fff8dc',
    'crimson': '#dc143c',
    'cyan': '#00ffff',
    'darkblue': '#00008b',
    'darkcyan': '#008b8b',
    'darkgoldenrod': '#b8860b',
    'darkgray': '#a9a9a9',
    'darkgreen': '#006400',
    'darkkhaki': '#bdb76b',
    'darkmagenta': '#8b008b',
    'darkolivegreen': '#556b2f',
    'darkorange': '#ff8c00',
    'darkorchid': '#9932cc',
    'darkred': '#8b0000',
    'darksalmon': '#e9967a',
    'darkseagreen': '#8fbc8f',
    'darkslateblue': '#483d8b',
    'darkslategray': '#2f4f4f',
    'darkturquoise': '#00ced1',
    'darkviolet': '#9400d3',
    'deeppink': '#ff1493',
    'deepskyblue': '#00bfff',
    'dimgray': '#696969',
    'dodgerblue': '#1e90ff',
    'firebrick': '#b22222',
    'floralwhite': '#fffaf0',
    'forestgreen': '#228b22',
    'fuchsia': '#ff00ff',
    'gainsboro': '#dcdcdc',
    'ghostwhite': '#f8f8ff',
    'gold': '#ffd700',
    'goldenrod': '#daa520',
    'gray': '#808080',
    'green': '#008000',
    'greenyellow': '#adff2f',
    'honeydew': '#f0fff0',
    'hotpink': '#ff69b4',
    'indianred': '#cd5c5c',
    'indigo': '#4b0082',
    'ivory': '#fffff0',
    'khaki': '#f0e68c',
    'lavender': '#e6e6fa',
    'lavenderblush': '#fff0f5',
    'lawngreen': '#7cfc00',
    'lemonchiffon': '#fffacd',
    'lightblue': '#add8e6',
    'lightcoral': '#f08080',
    'lightcyan': '#e0ffff',
    'lightgoldenrodyellow': '#fafad2',
    'lightgreen': '#90ee90',
    'lightgrey': '#d3d3d3',
    'lightpink': '#ffb6c1',
    'lightsalmon': '#ffa07a',
    'lightseagreen': '#20b2aa',
    'lightskyblue': '#87cefa',
    'lightslategray': '#778899',
    'lightsteelblue': '#b0c4de',
    'lightyellow': '#ffffe0',
    'lime': '#00ff00',
    'limegreen': '#32cd32',
    'linen': '#faf0e6',
    'magenta': '#ff00ff',
    'maroon': '#800000',
    'mediumaquamarine': '#66cdaa',
    'mediumblue': '#0000cd',
    'mediumorchid': '#ba55d3',
    'mediumpurple': '#9370db',
    'mediumseagreen': '#3cb371',
    'mediumslateblue': '#7b68ee',
    'mediumspringgreen': '#00fa9a',
    'mediumturquoise': '#48d1cc',
    'mediumvioletred': '#c71585',
    'midnightblue': '#191970',
    'mintcream': '#f5fffa',
    'mistyrose': '#ffe4e1',
    'moccasin': '#ffe4b5',
    'navajowhite': '#ffdead',
    'navy': '#000080',
    'oldlace': '#fdf5e6',
    'olive': '#808000',
    'olivedrab': '#6b8e23',
    'orange': '#ffa500',
    'orangered': '#ff4500',
    'orchid': '#da70d6',
    'palegoldenrod': '#eee8aa',
    'palegreen': '#98fb98',
    'paleturquoise': '#afeeee',
    'palevioletred': '#db7093',
    'papayawhip': '#ffefd5',
    'peachpuff': '#ffdab9',
    'peru': '#cd853f',
    'pink': '#ffc0cb',
    'plum': '#dda0dd',
    'powderblue': '#b0e0e6',
    'purple': '#800080',
    'red': '#ff0000',
    'rosybrown': '#bc8f8f',
    'royalblue': '#4169e1',
    'saddlebrown': '#8b4513',
    'salmon': '#fa8072',
    'sandybrown': '#f4a460',
    'seagreen': '#2e8b57',
    'seashell': '#fff5ee',
    'sienna': '#a0522d',
    'silver': '#c0c0c0',
    'skyblue': '#87ceeb',
    'slateblue': '#6a5acd',
    'slategray': '#708090',
    'snow': '#fffafa',
    'springgreen': '#00ff7f',
    'steelblue': '#4682b4',
    'tan': '#d2b48c',
    'teal': '#008080',
    'thistle': '#d8bfd8',
    'tomato': '#ff6347',
    'turquoise': '#40e0d0',
    'violet': '#ee82ee',
    'wheat': '#f5deb3',
    'white': '#ffffff',
    'whitesmoke': '#f5f5f5',
    'yellow': '#ffff00',
    'yellowgreen': '#9acd32'
}
_reverse_colors = dict((v, k) for k, v in _colors.iteritems())

# partial regular expressions for the expr parser
_r_number = '\d+(?:\.\d+)?'
_r_string = r"(?:'(?:[^'\\]*(?:\\.[^'\\]*)*)'|" \
            r'\"(?:[^"\\]*(?:\\.[^"\\]*)*)")'
_r_call = r'([a-zA-Z_][a-zA-Z0-9_]*)\('

# regular expressions for the expr parser
_operator_re = re.compile('|'.join(re.escape(x) for x in _operators))
_whitespace_re = re.compile(r'\s+')
_number_re = re.compile(_r_number + '(?![a-zA-Z0-9_])')
_value_re = re.compile(r'(%s)(%s)(?![a-zA-Z0-9_])' % (_r_number, '|'.join(_units)))
_color_re = re.compile(r'#' + ('[a-fA-f0-9]{1,2}' * 3))
_string_re = re.compile('%s|([^\s*/();,.+$]+|\.(?!%s))+' % (_r_string, _r_call))
_url_re = re.compile(r'url\(\s*(%s|.*?)\s*\)' % _r_string)
_var_re = re.compile(r'(?<!\\)\$(?:([a-zA-Z_][a-zA-Z0-9_]*)|'
                     r'\{([a-zA-Z_][a-zA-Z0-9_]*)\})')
_call_re = re.compile(r'\.' + _r_call)


def number_repr(value):
    """
    CleverCSS uses floats internally.  To keep the string representation
    of the numbers small cut off the places if this is possible without
    loosing much information.
    """
    value = unicode(value)
    parts = value.rsplit('.')
    if len(parts) == 2 and parts[-1] == '0':
        return parts[0]
    return value


def rgb_to_hls(red, green, blue):
    """
    Convert RGB to HSL.  The RGB values we use are in the range 0-255, but
    HSL is in the range 0-1!
    """
    return colorsys.rgb_to_hls(red / 255.0, green / 255.0, blue / 255.0)


def hls_to_rgb(hue, saturation, lightness):
    """Convert HSL back to RGB."""
    t = colorsys.hls_to_rgb(hue, saturation, lightness)
    return tuple(int(round(x * 255)) for x in t)


class ParserError(Exception):
    """
    Raised on syntax errors.
    """

    def __init__(self, lineno, message):
        self.lineno = lineno
        Exception.__init__(self, message)

    def __str__(self):
        return '%s (line %s)' % (
            self.message,
            self.lineno
        )


class EvalException(Exception):
    """
    Raised during evaluation.
    """

    def __init__(self, lineno, message):
        self.lineno = lineno
        Exception.__init__(self, message)

    def __str__(self):
        return '%s (line %s)' % (
            self.message,
            self.lineno
        )


class LineIterator(object):
    """
    This class acts as an iterator for sourcecode. It yields the lines
    without comments or empty lines and keeps track of the real line
    number.

    Example::

        >>> li = LineIterator(u'foo\nbar\n\n/* foo */bar')
        >>> li.next()
        1, u'foo'
        >>> li.next()
        2, 'bar'
        >>> li.next()
        4, 'bar'
        >>> li.next()
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        StopIteration
    """

    def __init__(self, source, emit_endmarker=False):
        """
        If `emit_endmarkers` is set to `True` the line iterator will send
        the string ``'__END__'`` before closing down.
        """
        lines = source.splitlines()
        self.lineno = 0
        self.lines = len(lines)
        self.emit_endmarker = emit_endmarker
        self._lineiter = iter(lines)

    def __iter__(self):
        return self

    def _read_line(self):
        """Read the next non empty line.  This strips line comments."""
        line = ''
        while not line.strip():
            line += _line_comment_re.sub('', self._lineiter.next()).rstrip()
            self.lineno += 1
        return line

    def _next(self):
        """
        Get the next line without mutliline comments.
        """
        # XXX: this fails for a line like this: "/* foo */bar/*"
        line = self._read_line()
        comment_start = line.find('/*')
        if comment_start < 0:
            return self.lineno, line

        stripped_line = line[:comment_start]
        comment_end = line.find('*/', comment_start)
        if comment_end >= 0:
            return self.lineno, stripped_line + line[comment_end + 2:]

        start_lineno = self.lineno
        try:
            while True:
                line = self._read_line()
                comment_end = line.find('*/')
                if comment_end >= 0:
                    stripped_line += line[comment_end + 2:]
                    break
        except StopIteration:
            raise ParserError(self.lineno, 'missing end of multiline comment')
        return start_lineno, stripped_line

    def next(self):
        """
        Get the next line without multiline comments and emit the
        endmarker if we reached the end of the sourcecode and endmarkers
        were requested.
        """
        try:
            return self._next()
        except StopIteration:
            if self.emit_endmarker:
                self.emit_endmarker = False
                return self.lineno, '__END__'
            raise


class Engine(object):
    """
    The central object that brings parser and evaluation together.  Usually
    nobody uses this because the `convert` function wraps it.
    """

    def __init__(self, source):
        self._parser = p = Parser()
        self.rules, self._vars = p.parse(source)

    def evaluate(self, context=None):
        """Evaluate code."""
        expr = None
        context = {}
        for key, value in context.iteritems():
            expr = self._parser.parse_expr(1, value)
            context[key] = expr
        context.update(self._vars)

        for selectors, defs in self.rules:
            yield selectors, [(key, expr.to_string(context))
                              for key, expr in defs]

    def to_css(self, context=None):
        """Evaluate the code and generate a CSS file."""
        blocks = []
        for selectors, defs in self.evaluate(context):
            block = []
            block.append(u',\n'.join(selectors) + ' {')
            for key, value in defs:
                block.append(u'  %s: %s;' % (key, value))
            block.append('}')
            blocks.append(u'\n'.join(block))
        return u'\n\n'.join(blocks)


class TokenStream(object):
    """
    This is used by the expression parser to manage the tokens.
    """

    def __init__(self, lineno, gen):
        self.lineno = lineno
        self.gen = gen
        self.next()

    def next(self):
        try:
            self.current = self.gen.next()
        except StopIteration:
            self.current = None, 'eof'

    def expect(self, value, token):
        if self.current != (value, token):
            raise ParserError(self.lineno, "expected '%s', got '%s'." %
                              (value, self.current[0]))
        self.next()


class Expr(object):
    """
    Baseclass for all expressions.
    """

    #: name for exceptions
    name = 'expression'

    #: empty iterable of dict with methods
    methods = ()

    def __init__(self, lineno=None):
        self.lineno = lineno

    def evaluate(self, context):
        return self

    def add(self, other, context):
        return String(self.to_string(context) + other.to_string(context))

    def sub(self, other, context):
        raise EvalException(self.lineno, 'cannot substract %s from %s' %
                            (self.name, other.name))

    def mul(self, other, context):
        raise EvalException(self.lineno, 'cannot multiply %s with %s' %
                            (self.name, other.name))

    def div(self, other, context):
        raise EvalException(self.lineno, 'cannot divide %s by %s' %
                            (self.name, other.name))

    def mod(self, other, context):
        raise EvalException(self.lineno, 'cannot use the modulo operator for '
                            '%s and %s. Misplaced unit symbol?' %
                            (self.name, other.name))

    def neg(self, context):
        raise EvalException(self.lineno, 'cannot negate %s by %s' % self.name)

    def to_string(self, context):
        return self.evaluate(context).to_string(context)

    def call(self, name, args, context):
        if name == 'string':
            if isinstance(self, String):
                return self
            return String(self.to_string(context))
        elif name == 'type':
            return String(self.name)
        if name not in self.methods:
            raise EvalException(self.lineno, '%s objects don\'t have a method'
                                ' called "%s". If you want to use this'
                                ' construct as string, quote it.' %
                                (self.name, name))
        return self.methods[name](self, context, *args)

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            ', '.join('%s=%r' % item for item in
                      self.__dict__.iteritems())
        )


class ImplicitConcat(Expr):
    """
    Holds multiple expressions that are delimited by whitespace.
    """
    name = 'concatenated'
    methods = {
        'list':     lambda x, c: List(x.nodes)
    }

    def __init__(self, nodes, lineno=None):
        Expr.__init__(self, lineno)
        self.nodes = nodes

    def to_string(self, context):
        return u' '.join(x.to_string(context) for x in self.nodes)


class Bin(Expr):

    def __init__(self, left, right, lineno=None):
        Expr.__init__(self, lineno)
        self.left = left
        self.right = right


class Add(Bin):

    def evaluate(self, context):
        return self.left.evaluate(context).add(
               self.right.evaluate(context), context)


class Sub(Bin):

    def evaluate(self, context):
        return self.left.evaluate(context).sub(
               self.right.evaluate(context), context)


class Mul(Bin):

    def evaluate(self, context):
        return self.left.evaluate(context).mul(
               self.right.evaluate(context), context)


class Div(Bin):

    def evaluate(self, context):
        return self.left.evaluate(context).div(
               self.right.evaluate(context), context)


class Mod(Bin):

    def evaluate(self, context):
        return self.left.evaluate(context).mod(
               self.right.evaluate(context), context)


class Neg(Expr):

    def __init__(self, node, lineno=None):
        Expr.__init__(self, lineno)
        self.node = node

    def evaluate(self, context):
        return self.node.evaluate(context).neg(context)


class Call(Expr):

    def __init__(self, node, method, args, lineno=None):
        Expr.__init__(self, lineno)
        self.node = node
        self.method = method
        self.args = args

    def evaluate(self, context):
        return self.node.evaluate(context) \
                        .call(self.method, [x.evaluate(context)
                                            for x in self.args],
                              context)


class Literal(Expr):

    def __init__(self, value, lineno=None):
        Expr.__init__(self, lineno)
        self.value = value

    def to_string(self, context):
        rv = unicode(self.value)
        if len(rv.split(None, 1)) > 1:
            return u"'%s'" % rv.replace('\\', '\\\\') \
                               .replace('\n', '\\\n') \
                               .replace('\t', '\\\t') \
                               .replace('\'', '\\\'')
        return rv


class Number(Literal):
    name = 'number'

    methods = {
        'abs':      lambda x, c: Number(abs(x.value)),
        'round':    lambda x, c, p=0: Number(round(x.value, p))
    }

    def __init__(self, value, lineno=None):
        Literal.__init__(self, float(value), lineno)

    def add(self, other, context):
        if isinstance(other, Number):
            return Number(self.value + other.value, lineno=self.lineno)
        elif isinstance(other, Value):
            return Value(self.value + other.value, other.unit,
                         lineno=self.lineno)
        return Literal.add(self, other, context)

    def sub(self, other, context):
        if isinstance(other, Number):
            return Number(self.value - other.value, lineno=self.lineno)
        elif isinstance(other, Value):
            return Value(self.value - other.value, other.unit,
                         lineno=self.lineno)
        return Literal.sub(self, other, context)

    def mul(self, other, context):
        if isinstance(other, Number):
            return Number(self.value * other.value, lineno=self.lineno)
        elif isinstance(other, Value):
            return Value(self.value * other.value, other.unit,
                         lineno=self.lineno)
        return Literal.mul(self, other, context)

    def div(self, other, context):
        try:
            if isinstance(other, Number):
                return Number(self.value / other.value, lineno=self.lineno)
            elif isinstance(other, Value):
                return Value(self.value / other.value, other.unit,
                             lineno=self.lineno)
            return Literal.div(self, other, context)
        except ZeroDivisionError:
            raise EvalException(self.lineno, 'cannot divide by zero')

    def mod(self, other, context):
        try:
            if isinstance(other, Number):
                return Number(self.value % other.value, lineno=self.lineno)
            elif isinstance(other, Value):
                return Value(self.value % other.value, other.unit,
                             lineno=self.lineno)
            return Literal.mod(self, other, context)
        except ZeroDivisionError:
            raise EvalException(self.lineno, 'cannot divide by zero')

    def neg(self, context):
        return Number(-self.value)

    def to_string(self, context):
        return number_repr(self.value)


class Value(Literal):
    name = 'value'

    methods = {
        'abs':      lambda x, c: Value(abs(x.value), x.unit),
        'round':    lambda x, c, p=0: Value(round(x.value, p), x.unit)
    }

    def __init__(self, value, unit, lineno=None):
        Literal.__init__(self, float(value), lineno)
        self.unit = unit

    def add(self, other, context):
        return self._conv_calc(other, context, operator.add, Literal.add,
                               'cannot add %s and %s')

    def sub(self, other, context):
        return self._conv_calc(other, context, operator.sub, Literal.sub,
                               'cannot subtract %s from %s')

    def mul(self, other, context):
        if isinstance(other, Number):
            return Value(self.value * other.value, self.unit,
                         lineno=self.lineno)
        return Literal.mul(self, other, context)

    def div(self, other, context):
        if isinstance(other, Number):
            try:
                return Value(self.value / other.value, self.unit,
                             lineno=self.lineno)
            except ZeroDivisionError:
                raise EvalException(self.lineno, 'cannot divide by zero',
                                    lineno=self.lineno)
        return Literal.div(self, other, context)

    def mod(self, other, context):
        if isinstance(other, Number):
            try:
                return Value(self.value % other.value, self.unit,
                             lineno=self.lineno)
            except ZeroDivisionError:
                raise EvalException(self.lineno, 'cannot divide by zero')
        return Literal.mod(self, other, context)

    def _conv_calc(self, other, context, calc, fallback, msg):
        if isinstance(other, Number):
            return Value(calc(self.value, other.value), self.unit)
        elif isinstance(other, Value):
            if self.unit == other.unit:
                return Value(calc(self.value,other.value), other.unit,
                             lineno=self.lineno)
            self_unit_type = _conv_mapping.get(self.unit)
            other_unit_type = _conv_mapping.get(other.unit)
            if not self_unit_type or not other_unit_type or \
               self_unit_type != other_unit_type:
                raise EvalException(self.lineno, msg % (self.unit, other.unit)
                                    + ' because the two units are '
                                    'not compatible.')
            self_unit = _conv[self_unit_type][self.unit]
            other_unit = _conv[other_unit_type][other.unit]
            if self_unit > other_unit:
                return Value(calc(self.value / other_unit * self_unit,
                                  other.value), other.unit,
                             lineno=self.lineno)
            return Value(calc(other.value / self_unit * other_unit,
                              self.value), self.unit, lineno=self.lineno)
        return fallback(self, other, context)

    def neg(self, context):
        return Value(-self.value, self.unit, lineno=self.lineno)

    def to_string(self, context):
        return number_repr(self.value) + self.unit


def brighten_color(color, context, amount=None):
    if amount is None:
        amount = Value(10.0, '%')
    hue, lightness, saturation = rgb_to_hls(*color.value)
    if isinstance(amount, Value):
        if amount.unit == '%':
            if not amount.value:
                return color
            lightness *= 1.0 + amount.value / 100.0
        else:
            raise EvalException(self.lineno, 'invalid unit %s for color '
                                'calculations.' % amount.unit)
    elif isinstance(amount, Number):
        lightness += (amount.value / 100.0)
    if lightness > 1:
        lightness = 1.0
    return Color(hls_to_rgb(hue, lightness, saturation))


def darken_color(color, context, amount=None):
    if amount is None:
        amount = Value(10.0, '%')
    hue, lightness, saturation = rgb_to_hls(*color.value)
    if isinstance(amount, Value):
        if amount.unit == '%':
            if not amount.value:
                return color
            lightness *= amount.value / 100.0
        else:
            raise EvalException(self.lineno, 'invalid unit %s for color '
                                'calculations.' % amount.unit)
    elif isinstance(amount, Number):
        lightness -= (amount.value / 100.0)
    if lightness < 0:
        lightness = 0.0
    return Color(hls_to_rgb(hue, lightness, saturation))


class Color(Literal):
    name = 'color'

    methods = {
        'brighten': brighten_color,
        'darken':   darken_color,
        'hex':      lambda x, c: Color(x.value, x.lineno)
    }

    def __init__(self, value, lineno=None):
        self.from_name = False
        if isinstance(value, basestring):
            if not value.startswith('#'):
                value = _colors.get(value)
                if not value:
                    raise ParserError(lineno, 'unknown color name')
                self.from_name = True
            try:
                if len(value) == 4:
                    value = [int(x * 2, 16) for x in value[1:]]
                elif len(value) == 7:
                    value = [int(value[i:i + 2], 16) for i in xrange(1, 7, 2)]
                else:
                    raise ValueError()
            except ValueError, e:
                raise ParserError(lineno, 'invalid color value')
        Literal.__init__(self, tuple(value), lineno)

    def add(self, other, context):
        if isinstance(other, (Color, Number)):
            return self._calc(other, operator.add)
        return Literal.add(self, other, context)

    def sub(self, other, context):
        if isinstance(other, (Color, Number)):
            return self._calc(other, operator.sub)
        return Literal.sub(self, other, context)

    def mul(self, other, context):
        if isinstance(other, (Color, Number)):
            return self._calc(other, operator.mul)
        return Literal.mul(self, other, context)

    def div(self, other, context):
        if isinstance(other, (Color, Number)):
            return self._calc(other, operator.sub)
        return Literal.div(self, other, context)

    def to_string(self, context):
        code = '#%02x%02x%02x' % self.value
        return self.from_name and _reverse_colors.get(code) or code

    def _calc(self, other, method):
        is_number = isinstance(other, Number)
        channels = []
        for idx, val in enumerate(self.value):
            if is_number:
                other_val = int(other.value)
            else:
                other_val = other.value[idx]
            new_val = method(val, other_val)
            if new_val > 255:
                new_val = 255
            elif new_val < 0:
                new_val = 0
            channels.append(new_val)
        return Color(tuple(channels), lineno=self.lineno)


class RGB(Expr):
    """
    an expression that hopefully returns a Color object.
    """

    def __init__(self, rgb, lineno=None):
        Expr.__init__(self, lineno)
        self.rgb = rgb

    def evaluate(self, context):
        args = []
        for arg in self.rgb:
            arg = arg.evaluate(context)
            if isinstance(arg, Number):
                value = int(arg.value)
            elif isinstance(arg, Value) and arg.unit == '%':
                value = int(arg.value / 100.0 * 255)
            else:
                raise EvalException(self.lineno, 'colors defined using the '
                                    'rgb() literal only accept numbers and '
                                    'percentages.')
            if value < 0 or value > 255:
                raise EvalError(self.lineno, 'rgb components must be in '
                                'the range 0 to 255.')
            args.append(value)
        return Color(args, lineno=self.lineno)


class String(Literal):
    name = 'string'

    methods = {
        'length':   lambda x, c: Number(len(x.value)),
        'upper':    lambda x, c: String(x.value.upper()),
        'lower':    lambda x, c: String(x.value.lower()),
        'strip':    lambda x, c: String(x.value.strip()),
        'split':    lambda x, c, d=None: String(x.value.split(d)),
        'eval':     lambda x, c: Parser().parse_expr(x.lineno, x.value)
                                         .evaluate(c)
    }

    def mul(self, other, context):
        if isinstance(other, Number):
            return String(self.value * int(other.value), lineno=self.lineno)
        return Literal.mul(self, other, context, lineno=self.lineno)


class URL(Literal):
    name = 'URL'
    methods = {
        'length':   lambda x, c: Number(len(self.value))
    }

    def add(self, other, context):
        return URL(self.value + other.to_string(context),
                   lineno=self.lineno)

    def mul(self, other, context):
        if isinstance(other, Number):
            return URL(self.value * int(other.value), lineno=self.lineno)
        return Literal.mul(self, other, context)

    def to_string(self, context):
        return 'url(%s)' % Literal.to_string(self, context)


class Var(Expr):

    def __init__(self, name, lineno=None):
        self.name = name
        self.lineno = lineno

    def evaluate(self, context):
        if self.name not in context:
            raise EvalException(self.lineno, 'variable %s is not defined' %
                                (self.name,))
        val = context[self.name]
        context[self.name] = FailingVar(self, self.lineno)
        try:
            return val.evaluate(context)
        finally:
            context[self.name] = val


class FailingVar(Expr):

    def __init__(self, var, lineno=None):
        Expr.__init__(self, lineno or var.lineno)
        self.var = var

    def evaluate(self, context):
        raise EvalException(self.lineno, 'Circular variable dependencies '
                            'detected when resolving %s.' % (self.var.name,))


class List(Expr):
    name = 'list'

    methods = {
        'length':   lambda x, c: Number(len(x.items)),
        'join':     lambda x, c, d=String(' '): String(d.value.join(
                                 a.to_string(c) for a in x.items))
    }

    def __init__(self, items, lineno=None):
        Expr.__init__(self, lineno)
        self.items = items

    def add(self, other):
        if isinstance(other, List):
            return List(self.items + other.items, lineno=self.lineno)
        return List(self.items + [other], lineno=self.lineno)

    def to_string(self, context):
        return u', '.join(x.to_string(context) for x in self.items)


class Parser(object):
    """
    Class with a bunch of methods that implement a tokenizer and parser.  In
    fact this class has two parsers.  One that splits up the code line by
    line and keeps track of indentions, and a second one for expressions in
    the value parts.
    """

    def preparse(self, source):
        """
        Do the line wise parsing and resolve indents.
        """
        rule = (None, [], [])
        vars = {}
        indention_stack = [0]
        state_stack = ['root']
        group_block_stack = []
        rule_stack = [rule]
        root_rules = rule[1]
        new_state = None
        lineiter = LineIterator(source, emit_endmarker=True)

        def fail(msg):
            raise ParserError(lineno, msg)

        def parse_definition():
            m = _def_re.search(line)
            if m is None:
                fail('invalid syntax for style definition')
            return lineiter.lineno, m.group(1), m.group(2)

        for lineno, line in lineiter:
            raw_line = line.rstrip().expandtabs()
            line = raw_line.lstrip()
            indention = len(raw_line) - len(line)

            # indenting
            if indention > indention_stack[-1]:
                if not new_state:
                    fail('unexpected indent')
                state_stack.append(new_state)
                indention_stack.append(indention)
                new_state = None

            # dedenting
            elif indention < indention_stack[-1]:
                for level in indention_stack:
                    if level == indention:
                        while indention_stack[-1] != level:
                            if state_stack[-1] == 'rule':
                                rule = rule_stack.pop()
                            elif state_stack[-1] == 'group_block':
                                name, part_defs = group_block_stack.pop()
                                for lineno, key, val in part_defs:
                                    rule[2].append((lineno, name + '-' +
                                                    key, val))
                            indention_stack.pop()
                            state_stack.pop()
                        break
                else:
                    fail('invalid dedent')

            # new state but no indention. bummer
            elif new_state:
                fail('expected definitions, found nothing')

            # end of data
            if line == '__END__':
                break

            # root and rules
            elif state_stack[-1] in ('rule', 'root'):
                # new rule blocks
                if line.endswith(':'):
                    s_rule = line[:-1].rstrip()
                    if not s_rule:
                        fail('empty rule')
                    new_state = 'rule'
                    new_rule = (s_rule, [], [])
                    rule[1].append(new_rule)
                    rule_stack.append(rule)
                    rule = new_rule

                # if we in a root block we don't consume group blocks
                # or style definitions but variable defs
                elif state_stack[-1] == 'root':
                    if '=' in line:
                        m = _var_def_re.search(line)
                        if m is None:
                            fail('invalid syntax')
                        key = m.group(1)
                        if key in vars:
                            fail('variable "%s" defined twice' % key)
                        vars[key] = (lineiter.lineno, m.group(2))
                    else:
                        fail('Style definitions or group blocks are only '
                             'allowed inside a rule or group block.')

                # definition group blocks
                elif line.endswith('->'):
                    group_prefix = line[:-2].rstrip()
                    if not group_prefix:
                        fail('no group prefix defined')
                    new_state = 'group_block'
                    group_block_stack.append((group_prefix, []))

                # otherwise parse a style definition.
                else:
                    rule[2].append(parse_definition())

            # group blocks
            elif state_stack[-1] == 'group_block':
                group_block_stack[-1][1].append(parse_definition())

            # something unparseable happened
            else:
                fail('unexpected character %s' % line[0])

        return root_rules, vars

    def parse(self, source):
        """
        Create a flat structure and parse inline expressions.
        """
        def handle_rule(rule, children, defs):
            def recurse():
                if defs:
                    result.append((get_selectors(), [
                        (k, self.parse_expr(lineno, v)) for
                        lineno, k, v in defs
                    ]))
                for child in children:
                    handle_rule(*child)

            local_rules = []
            reference_rules = []
            for r in rule.split(','):
                r = r.strip()
                if '&' in r:
                    reference_rules.append(r)
                else:
                    local_rules.append(r)

            if local_rules:
                stack.append(local_rules)
                recurse()
                stack.pop()

            if reference_rules:
                if stack:
                    parent_rules = stack.pop()
                    push_back = True
                else:
                    parent_rules = ['*']
                    push_back = False
                virtual_rules = []
                for parent_rule in parent_rules:
                    for tmpl in reference_rules:
                        virtual_rules.append(tmpl.replace('&', parent_rule))
                stack.append(virtual_rules)
                recurse()
                stack.pop()
                if push_back:
                    stack.append(parent_rules)

        def get_selectors():
            branches = [()]
            for level in stack:
                new_branches = []
                for rule in level:
                    for item in branches:
                        new_branches.append(item + (rule,))
                branches = new_branches
            return [' '.join(branch) for branch in branches]

        root_rules, vars = self.preparse(source)
        result = []
        stack = []
        for rule in root_rules:
            handle_rule(*rule)

        real_vars = {}
        for name, args in vars.iteritems():
            real_vars[name] = self.parse_expr(*args)

        return result, real_vars

    def parse_expr(self, lineno, s):
        def parse():
            pos = 0
            end = len(s)

            def process(token, group=0):
                return lambda m: (m.group(group), token)

            def process_string(m):
                value = m.group(0)
                try:
                    if value[:1] == value[-1:] and value[0] in '"\'':
                        value = value[1:-1].encode('utf-8') \
                                           .decode('string-escape') \
                                           .encode('utf-8')
                    elif value == 'rgb':
                        return None, 'rgb'
                    elif value in _colors:
                        return value, 'color'
                except UnicodeError:
                    raise ParserError(lineno, 'invalid string escape')
                return value, 'string'

            rules = ((_operator_re, process('op')),
                     (_call_re, process('call', 1)),
                     (_value_re, lambda m: (m.groups(), 'value')),
                     (_color_re, process('color')),
                     (_number_re, process('number')),
                     (_url_re, process('url', 1)),
                     (_string_re, process_string),
                     (_var_re, lambda m: (m.group(1) or m.group(2), 'var')),
                     (_whitespace_re, None))

            while pos < end:
                for rule, processor in rules:
                    m = rule.match(s, pos)
                    if m is not None:
                        if processor is not None:
                            yield processor(m)
                        pos = m.end()
                        break
                else:
                    raise ParserError(lineno, 'Syntax error')

        s = s.rstrip(';')
        return self.expr(TokenStream(lineno, parse()))

    def expr(self, stream, ignore_comma=False):
        args = [self.concat(stream)]
        list_delim = [(';', 'op')]
        if not ignore_comma:
            list_delim.append((',', 'op'))
        while stream.current in list_delim:
            stream.next()
            args.append(self.concat(stream))
        if len(args) == 1:
            return args[0]
        return List(args, lineno=stream.lineno)

    def concat(self, stream):
        args = [self.add(stream)]
        while stream.current[1] != 'eof' and \
              stream.current not in ((',', 'op'), (';', 'op'),
                                     (')', 'op')):
            args.append(self.add(stream))
        if len(args) == 1:
            node = args[0]
        else:
            node = ImplicitConcat(args, lineno=stream.lineno)
        return node

    def add(self, stream):
        left = self.sub(stream)
        while stream.current == ('+', 'op'):
            stream.next()
            left = Add(left, self.sub(stream), lineno=stream.lineno)
        return left

    def sub(self, stream):
        left = self.mul(stream)
        while stream.current == ('-', 'op'):
            stream.next()
            left = Sub(left, self.mul(stream), lineno=stream.lineno)
        return left

    def mul(self, stream):
        left = self.div(stream)
        while stream.current == ('*', 'op'):
            stream.next()
            left = Mul(left, self.div(stream), lineno=stream.lineno)
        return left

    def div(self, stream):
        left = self.mod(stream)
        while stream.current == ('/', 'op'):
            stream.next()
            left = Div(left, self.mod(stream), lineno=stream.lineno)
        return left

    def mod(self, stream):
        left = self.neg(stream)
        while stream.current == ('%', 'op'):
            stream.next()
            left = Mod(left, self.neg(stream), lineno=stream.lineno)
        return left

    def neg(self, stream):
        if stream.current == ('-', 'op'):
            stream.next()
            return Neg(self.primary(stream), lineno=stream.lineno)
        return self.primary(stream)

    def primary(self, stream):
        value, token = stream.current
        if token == 'number':
            stream.next()
            node = Number(value, lineno=stream.lineno)
        elif token == 'value':
            stream.next()
            node = Value(lineno=stream.lineno, *value)
        elif token == 'color':
            stream.next()
            node = Color(value, lineno=stream.lineno)
        elif token == 'rgb':
            stream.next()
            if stream.current == ('(', 'op'):
                stream.next()
                args = []
                while len(args) < 3:
                    if args:
                        stream.expect(',', 'op')
                    args.append(self.expr(stream, True))
                stream.expect(')', 'op')
                return RGB(tuple(args), lineno=stream.lineno)
            else:
                node = String('rgb')
        elif token == 'string':
            stream.next()
            node = String(value, lineno=stream.lineno)
        elif token == 'url':
            stream.next()
            node = URL(value, lineno=stream.lineno)
        elif token == 'var':
            stream.next()
            node = Var(value, lineno=stream.lineno)
        elif token == 'op' and value == '(':
            stream.next()
            if stream.current == (')', 'op'):
                raise ParserError(stream.lineno, 'empty parentheses are '
                                  'not valid. If you want to use them as '
                                  'string you have to quote them.')
            node = self.expr(stream)
            stream.expect(')', 'op')
        else:
            if token == 'call':
                raise ParserError(stream.lineno, 'You cannot call standalone '
                                  'methods. If you wanted to use it as a '
                                  'string you have to quote it.')
            stream.next()
            node = String(value, lineno=stream.lineno)
        while stream.current[1] == 'call':
            node = self.call(stream, node)
        return node

    def call(self, stream, node):
        method, token = stream.current
        assert token == 'call'
        stream.next()
        args = []
        while stream.current != (')', 'op'):
            if args:
                stream.expect(',', 'op')
            args.append(self.expr(stream))
        stream.expect(')', 'op')
        return Call(node, method, args, lineno=stream.lineno)


def convert(source, context=None):
    """Convert a CleverCSS file into a normal stylesheet."""
    return Engine(source).to_css(context)


def main():
    """Entrypoint for the shell."""
    import sys

    # help!
    if '--help' in sys.argv:
        print 'usage: %s <file 1> ... <file n>' % sys.argv[0]
        print '  if called with some filenames it will read each file, cut of'
        print '  the extension and append a ".css" extension and save. If '
        print '  the target file has the same name as the source file it will'
        print '  abort, but if it overrides a file during this process it will'
        print '  continue. This is a desired functionality. To avoid that you'
        print '  must not give your source file a .css extension.'
        print
        print '  if you call it without arguments it will read from stdin and'
        print '  write the converted css to stdout.'
        print
        print '  called with the --eigen-test parameter it will evaluate the'
        print '  example from the module docstring.'
        print
        print '  to get a list of known color names call it with --list-colors'

    # version
    elif '--version' in sys.argv:
        print 'CleverCSS Version %s' % VERSION
        print 'Licensed under the BSD license.'
        print '(c) Copyright 2007 by Armin Ronacher and Georg Brandl.'

    # evaluate the example from the docstring.
    elif '--eigen-test' in sys.argv:
        print convert('\n'.join(l[8:].rstrip() for l in
                      re.compile(r'Example::\n(.*?)__END__(?ms)')
                        .search(__doc__).group(1).splitlines()))

    # color list
    elif '--list-colors' in sys.argv:
        print '%s known colors:' % len(_colors)
        for color in sorted(_colors.items()):
            print '  %-30s%s' % color

    # read from stdin and write to stdout
    elif len(sys.argv) == 1:
        try:
            print convert(sys.stdin.read())
        except (ParserError, EvalException), e:
            sys.stderr.write('Error: %s\n' % e)
            sys.exit(1)

    # convert some files
    else:
        for fn in sys.argv[1:]:
            target = fn.rsplit('.', 1)[0] + '.css'
            if fn == target:
                sys.stderr.write('Error: same name for source and target file'
                                 ' "%s".' % fn)
                sys.exit(2)
            src = file(fn)
            try:
                try:
                    converted = convert(src.read())
                except (ParserError, EvalException), e:
                    sys.stderr.write('Error in file %s: %s\n' % (fn, e))
                    sys.exit(1)
                dst = file(target, 'w')
                try:
                    dst.write(converted)
                finally:
                    dst.close()
            finally:
                src.close()


if __name__ == '__main__':
    main()
