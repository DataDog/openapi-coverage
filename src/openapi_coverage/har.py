"""Calculate coverage for HAR files."""

import json
from urllib.parse import urlparse

from .lookup import lookup
from .paths import build_url_map
from .schemas import cover_schema


def load_har(path):
    with open(path, "r") as f:
        return json.load(f)


def _build_header_map(headers):
    return {
        header["name"]: header["value"]
        for header in headers
    }


def cover_har(schema, har, url_map=None):
    """Calculate coverage for a HAR file."""
    url_map = url_map or build_url_map(schema)

    coverage = set()
    for entry in har["log"]["entries"]:
        url = entry["request"]["url"]
        method = entry["request"]["method"]

        parsed_url = urlparse(url)
        parts, path_parameters = url_map.bind(parsed_url.hostname).match(parsed_url.path, method=method)

        # TODO cover path, query, and headers

        operation = lookup(schema, parts)

        if "requestBody" in operation:
            prefix = ["requestBody", "content", entry["request"]["postData"]["mimeType"], "schema"]
            data_schema = lookup(operation, prefix)
            try:
                data = json.loads(entry["request"]["postData"]["text"])
                for covered in cover_schema(data_schema, data):
                    coverage.add((*parts, *prefix, *covered))
            except ValueError:
                pass

        if "responses" in operation:
            response = entry["response"]
            status_code = str(response["status"])
            content_type = response["content"]["mimeType"]
            prefix = ["responses", status_code, "content", content_type, "schema"]
            try:
                response_schema = lookup(operation, prefix)
            except KeyError:
                continue
            try:
                data = json.loads(response["content"]["text"])
                for covered in cover_schema(response_schema, data):
                    coverage.add((*parts, *prefix, *covered))
            except ValueError:
                pass

    return coverage