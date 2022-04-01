"""Use path parts to get a right part of the schema."""

def lookup(schema, path):
    """Use path parts to get a right part of the schema."""
    if not path:
        return schema
    else:
        return lookup(schema[path[0]], path[1:])