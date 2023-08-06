# system modules
import functools
import re
import json
import sys
import argparse
import operator

# internal modules

# external modules
import inflect


def latex_escape(string):
    """
    Prepend characters that have a special meaning in LaTeX with a backslash.
    """
    return functools.reduce(
        lambda s, m: re.sub(m[0], m[1], s),
        (
            (r"[\\]", r"\\textbackslash "),
            (r"[~]", r"\\textasciitilde "),
            (r"[\^]", r"\\textasciicircum "),
            (r"([&%$#_{}])", r"\\\1"),
        ),
        str(string),
    )


def numbers2words(s):
    p = inflect.engine()
    if isinstance(s, int):
        return p.ordinal(
            re.sub(r"\W+", r" ", p.number_to_words(s, andword="", comma=""))
        )
    numbers = re.findall(r"\d+", str(s))
    outs = s
    for number in numbers:
        words = re.sub(
            r"\W+", r" ", p.number_to_words(number, andword="", comma="")
        )
        outs = outs.replace(number, " {} ".format(words), 1)
    return outs


def elements2texmaxcroname(elements):
    p = inflect.engine()
    return re.sub(
        r"\s+",
        r"",
        " ".join(
            map(
                operator.methodcaller("title"),
                map(
                    lambda w: re.sub(r"\W+", r" ", w),
                    map(numbers2words, elements),
                ),
            ),
        ),
    )


def dead_ends(d, path=tuple()):
    """
    Generator recursing into a dictionary and yielding tuples of paths and the
    value at dead ends.
    """
    if type(d) in (str, int, bool, float, type(None)):
        # print(f"Reached a dead end: {d}")
        yield path, d
        return
    elif hasattr(d, "items"):
        # print(f"recursing into dict {d}")
        for k, v in d.items():
            for x in dead_ends(v, path + (k,)):
                yield x
    else:
        try:
            it = iter(d)
            # print(f"recursing into list {d}")
            for i, e in enumerate(d):
                for x in dead_ends(e, path + (i + 1,)):
                    yield x
        except TypeError:
            # print(f"Don't know what to do with {d}. Assuming it's a dead end.")
            yield sequence, d


def cli():
    parser = argparse.ArgumentParser(description="Convert JSON to TEX")
    parser.add_argument(
        "-i",
        "--input",
        help="input JSON file",
        nargs="+",
        type=argparse.FileType("r"),
        default=[sys.stdin],
    )
    parser.add_argument(
        "-o",
        "--output",
        help="output TEX file",
        type=argparse.FileType("w"),
        default=sys.stdout,
    )
    args = parser.parse_args()

    # Merge all inputs
    for f in args.input:
        d = json.load(f)
        try:
            JSON
        except NameError:
            JSON = d
            continue
        if isinstance(JSON, list):
            if isinstance(d, list):
                JSON.extend(d)
            else:
                JSON.append(d)
        elif isinstance(JSON, dict):
            if isinstance(d, dict):
                JSON.update(d)
            else:
                JSON = [JSON, d]

    # Traverse the merged inputs and output TeX definitions
    for name_parts, raw_value in dead_ends(JSON):
        name = elements2texmaxcroname(name_parts)
        value = latex_escape(raw_value)
        args.output.write(f"\\newcommand{{\\{name}}}{{{value}}}\n")
