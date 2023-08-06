def concat(items, union=None, cast=None):
    if union is None:
        union = concat.default_union
    if cast is None:
        cast = concat.default_cast
    iterator = iter(items)
    try:
        first = next(iterator)
    except StopIteration:
        return ''
    try:
        second = next(iterator)
    except StopIteration:
        return cast(first)
    *head, last = first, second, *iterator
    return ', '.join(map(cast, head)) + f' {union} {cast(last)}'


concat.default_union = 'or'
concat.default_cast = repr