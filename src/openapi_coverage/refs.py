"""Rewrite paths using JSON-refs."""

def get_ref(schema):
    """Get JSON-ref from the schema."""
    if hasattr(schema, "__reference__"):
        return schema.__reference__["$ref"]
    return None


def replace_refs(schema, path):
    """Replace JSON-refs in the schema."""
    ref_index = 0
    prefix = None
    for index, part in enumerate(path):
        ref = get_ref(schema)
        if ref is not None:
            ref_index = index
            prefix = ref.split("/")[1:]

        schema = schema[part]

    ref = get_ref(schema)
    if ref is not None:
        ref_index = len(path)
        prefix = ref.split("/")[1:]

    if prefix is not None:
        return (*prefix, *path[ref_index:])
    return path
