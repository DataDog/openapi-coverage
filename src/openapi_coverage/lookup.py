"""Use path parts to get a right part of the schema."""


def lookup(schema, path):
    """Use path parts to get a right part of the schema."""
    if not path:
        return schema
    else:
        try:
            return lookup(schema[path[0]], path[1:])
        except KeyError:
            raise RuntimeError(f"Unable to find {path[0]!r} in {schema.keys()}")


def lookup_endline(schema, path, fallback=0):
    """Retrieve the last line of a data structure in the given schema."""
    original_schema = schema
    path_length = len(path)
    if not path_length:
        return fallback
    elif path_length == 1:
        position = schema[f"__position__{path[0]}"]["line"]
    else:
        for item in path[:-2]:
            schema = schema[item]
        if isinstance(path[-1], int):
            position = schema[path[-2]][path[-1] + 1]["line"]
        else:
            position = schema[path[-2]][f"__position__{path[-1]}"]["line"]
        if not isinstance(schema[path[-2]], list):
            schema = schema[path[-2]]

    next_items = [value["line"] for key, value in schema.items()
                  if key.startswith("__position__") and value["line"] > position]
    if not next_items:
        return lookup_endline(original_schema, path[:-1], fallback)

    return min(next_items) - 1
