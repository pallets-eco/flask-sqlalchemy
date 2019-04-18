import sys

PY2 = sys.version_info[0] == 2


if PY2:
    xrange = xrange  # noqa: F821

    string_types = (unicode, bytes)  # noqa: F821

    def to_str(x, charset='utf8', errors='strict'):
        if x is None or isinstance(x, str):
            return x

        if isinstance(x, unicode):  # noqa: F821
            return x.encode(charset, errors)

        return str(x)

else:
    xrange = range

    string_types = (str,)

    def to_str(x, charset='utf8', errors='strict'):
        if x is None or isinstance(x, str):
            return x

        if isinstance(x, bytes):
            return x.decode(charset, errors)

        return str(x)
