import sys

import docrun


def example1(name, value=42):
    """
    example function

    :param name: name string
    :param value: something value
    """
    print("Hello {}!".format(name))
    return value


def main():
    return docrun.run(example1)


if __name__ == "__main__":
    sys.exit(main())

