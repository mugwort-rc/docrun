# DocRun

DocString ArgumentParser

## Usage

```example.py
import sys

import docrun


def example(name, value=42):
    """
    example function

    :param name: name string
    :param value: something value
    """
    print("Hello {}!".format(name))
    return value


def main():
    return docrun.run(example)


if __name__ == "__main__":
    sys.exit(main())
```

```shell
$ python3 example.py
usage: example.py [-h] [--value VALUE] name
example.py: error: the following arguments are required: name
$ python3 example.py test
Hello test!
```

