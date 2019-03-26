
from pkg_resources import parse_version
import sqlalchemy


def sqlalchemy_version(op, val):
    sa_ver = parse_version(sqlalchemy.__version__)
    target_ver = parse_version(val)

    assert op in ('<', '>', '<=', '>=', '=='), 'op {} not supported'.format(op)

    if op == '<':
        return sa_ver < target_ver
    if op == '>':
        return sa_ver > target_ver
    if op == '<=':
        return sa_ver <= target_ver
    if op == '>=':
        return sa_ver >= target_ver
    return sa_ver == target_ver
