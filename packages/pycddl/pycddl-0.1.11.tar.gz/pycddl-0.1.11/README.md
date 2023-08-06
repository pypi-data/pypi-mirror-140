# PyCDDL: A CDDL validation library for Python

[CDDL](https://www.rfc-editor.org/rfc/rfc8610.html) is a schema language for the CBOR serialization format.
`pycddl` allows you to validate CBOR documents match a particular CDDL schema, based on the Rust [`cddl`](https://github.com/anweiss/cddl) library.

For example, here we use the [`cbor2`](https://pypi.org/project/cbor2/) library to serialize a dictionary to CBOR, and then validate it:

```python
from pycddl import Schema
import cbor2

uint_schema = Schema("""
    object = {
        xint: uint
    }
"""
)
uint_schema.validate_cbor(cbor2.dumps({"xint", -2}))
```

If validation fails, a `pycddl.ValidationError` is raised.

