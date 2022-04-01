"""Rewrite paths using JSON-refs."""

def replace_refs(schema, path):
    """Replace JSON-refs in the schema."""
    ref_index = 0
    prefix = None
    for index, part in enumerate(path):
        if hasattr(schema, "__reference__"):
            ref_index = index
            prefix = schema.__reference__["$ref"].split("/")[1:]

        schema = schema[part]

    if prefix is not None:
        return (*prefix, *path[ref_index:])
    return path