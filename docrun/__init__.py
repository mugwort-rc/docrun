import argparse
import enum
import io
import re


class State(enum.Enum):
    Begin = enum.auto()
    Field = enum.auto()
    FieldText = enum.auto()
    Interpret = enum.auto()


RE_FIELD = re.compile(r"^\s*:param\s+([^:]+)\s*:\s*(.+)\s*$")


class PEP287Parser:
    def __init__(self):
        self.args = []
        self.description = None
        self.state = State.Begin
        self.temp = []
        self.last_indent = None

    def parse_field(cls, line):
        m = RE_FIELD.match(line)
        assert m is not None
        key, value = m.groups()
        hint = None
        if " " in key:
            temp = key.split(" ")
            key = temp[0]
            hint = " ".join(temp[1:])
        return key, hint, value

    def flush(self):
        if self.state == State.Begin:
            if self.temp and self.description is None:
                self.description = " ".join(x.lstrip() for x in self.temp)
        elif self.state == State.Field:
            assert len(self.temp) == 1
            self.args.append(self.parse_field(self.temp[0]))
        elif self.state == State.FieldText:
            self.args.append(self.parse_field(x.lstrip() for x in self.temp))
        elif self.state == State.Interpret:
            # doctest
            pass
        else:
            raise NotImplementedError("Not implemented yet: {!r}".format(self.state))
        self.state = State.Begin
        self.temp = []
        self.last_indent = None

    def parse(self, doc):
        for line in io.StringIO(doc):
            if not line.strip():
                # empty
                self.flush()
                self.state = State.Begin
                continue
            lstriped = line.lstrip()
            indent = len(line) - len(lstriped)
            if self.last_indent is not None:
                # detect de-indent
                if indent < self.last_indent:
                    self.flush()
                elif indent == self.last_indent:
                    if self.state in [State.Field]:
                        self.flush()
            if self.state == State.Begin:
                if RE_FIELD.match(line):
                    self.temp.append(line.rstrip("\n"))
                    self.state = State.Field
                elif line.startswith(">>>"):
                    self.state = State.TestInput
                else:
                    self.temp.append(line.strip())
                self.last_indent = indent
            elif self.state == State.Field:
                assert self.last_indent is not None
                if indent <= self.last_indent:
                    self.flush()
                    self.temp.append(line)
                else:
                    self.temp.append(line.rstrip("\n"))
                    self.state = State.FieldText
            elif self.state == State.FieldText:
                assert self.last_indent is not None
                assert indent >= self.last_indent
                self.temp.append(line)
            elif self.state == State.TestInput:
                assert not lstriped.startswith(">>>")
                self.state = State.Begin

        self.flush()
        return self.description, self.args


def parse_pep287(doc):
    """
    :param doc: PEP 287 docstring
    """
    parser = PEP287Parser()
    return parser.parse(doc)


def parse_doc(func):
    """
    :param func: Python Function object
    """
    description, args = parse_pep287(func.__doc__)
    size = len(args)
    defaults = func.__defaults__
    arg_count = size - len(defaults)
    opt_count = size - arg_count

    parser = argparse.ArgumentParser(description=description)
    # required args
    for i in range(arg_count):
        name, hint, help = args[i]
        parser.add_argument(name, help=help)
    # optional args
    for k, i in enumerate(range(arg_count, size)):
        name, hint, help = args[i]
        parser.add_argument("--{}".format(name.replace("_", "-")), help=help, default=defaults[k])
    return parser


def run(func):
    """
    :param func: Python Function object
    """
    parser = parse_doc(func)
    args = parser.parse_args()
    return func(**dict(args._get_kwargs()))

