# openapi-coverage
Calculate schema coverage

## Usage

```python
import openapi_coverage

openapi_coverage.cover_schema(schema, data)

openapi_coverage.cover_schema(schema, first) | openapi_coverage.cover_schema(schema, second)
```

Calculate coverage of schema based on HAR recording:

```console
$ python -m openapi_coverage openapi.yaml cassettes/*/*.har
```
## Ideas

- [ ] prepare fixtures and petstore coverage example
- [ ] instrument `httplib` to automatically calculate coverage for HTTP traffic
- [ ] generate coverage reports (lcov, ...)
