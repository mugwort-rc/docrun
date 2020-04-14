# DocRun

DocString ArgumentParser

## Usage

```
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

