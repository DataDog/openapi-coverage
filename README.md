# openapi-coverage
Calculate schema coverage

## Usage

```python
import openapi_coverage

openapi_coverage.cover(schema, data)

openapi_coverage.cover(schema, first) | openapi_coverage.cover(schema, second)
```



## Ideas

- [ ] prepare fixtures and petstore coverage example
- [ ] instrument `httplib` to automatically calculate coverage for HTTP traffic
- [ ] generate coverage reports (lcov, ...)
