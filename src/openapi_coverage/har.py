"""Calculate coverage for HAR files."""

import json
import warnings
from urllib.parse import urlparse, parse_qs

from werkzeug.exceptions import NotFound
from werkzeug.http import parse_options_header

from .lookup import lookup
from .paths import build_url_map
from .schemas import cover_schema


def load_har(path):
    with open(path, "r") as f:
        return json.load(f)


def _build_header_map(headers):
    return {header["name"]: header["value"] for header in headers}


def cover_har(schema, har, url_map=None):
    """Calculate coverage for a HAR file."""
    url_map = url_map or build_url_map(schema)

    coverage = set()
    for entry in har["log"]["entries"]:
        url = entry["request"]["url"]
        method = entry["request"]["method"]

        parsed_url = urlparse(url)
        try:
            parts, path_parameters = url_map.bind(parsed_url.hostname).match(
                parsed_url.path, method=method
            )
        except NotFound:
            warnings.warn(f"Unable to match {url}")
            continue

        query_parameters = parse_qs(parsed_url.query)
        request_headers = _build_header_map(entry["request"]["headers"])
        operation = lookup(schema, parts)

        for i, parameter in enumerate(operation.get("parameters", [])):
            schema_keys = list((*parts, "parameters", i))
            if parameter["in"] == "path":
                name = parameter["name"]
                if name in path_parameters:
                    value = path_parameters[name]
                    coverage |= cover_schema(
                        parameter["schema"], value, schema_keys=schema_keys
                    )
            elif parameter["in"] == "header":
                name = parameter["name"]
                value = request_headers.get(name)
                if value is not None:
                    coverage |= cover_schema(
                        parameter["schema"], value, schema_keys=schema_keys
                    )
            elif parameter["in"] == "query":
                name = parameter["name"]
                value = query_parameters.get(name)
                if value is not None:
                    coverage |= cover_schema(
                        parameter["schema"], value, schema_keys=schema_keys
                    )
            else:
                raise ValueError("Unknown parameter type: {}".format(parameter["in"]))

        if "requestBody" in operation:
            prefix = [
                "requestBody",
                "content",
                entry["request"]["postData"]["mimeType"],
                "schema",
            ]
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
            variants = [status_code, status_code[0] + "xx", "default"]
            response_schema = None

            for variant in variants:
                prefix = ["responses", variant]
                try:
                    response_schema = lookup(operation, prefix[:2])
                    break
                except KeyError:
                    continue

            if response_schema is None:
                raise ValueError(
                    "Unable to find schema for response {}".format(status_code)
                )

            if "content" in response_schema:
                response_schema = response_schema["content"]
                parsed_content_type = parse_options_header(content_type)
                matched_content_type = None
                for schema_content_type in response_schema:
                    parsed_schema_content_type = parse_options_header(
                        schema_content_type
                    )
                    if (
                        schema_content_type == "*/*"
                        or parsed_schema_content_type[0] == parsed_content_type[0]
                    ):
                        matched_content_type = schema_content_type
                        break

                if matched_content_type:
                    response_schema = response_schema[matched_content_type]["schema"]
                    prefix += ["content", matched_content_type, "schema"]

                    try:
                        data = json.loads(response["content"]["text"])
                        for covered in cover_schema(response_schema, data):
                            coverage.add((*parts, *prefix, *covered))
                    except ValueError:
                        pass
                else:
                    warnings.warn(
                        f"Unable to find schema for content type {content_type} - known types: {response_schema.keys()} in {method} {url}"
                    )

    return coverage
