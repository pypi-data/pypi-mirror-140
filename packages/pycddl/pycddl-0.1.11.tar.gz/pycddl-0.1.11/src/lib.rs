use cddl::{cddl_from_str, lexer_from_str, validate_cbor_from_slice};
use pyo3::{
    create_exception,
    exceptions::{PyException, PyValueError},
    prelude::*,
};

#[pyclass]
struct Schema {
    // Keep around the underlying data.
    schema: String,
    // TODO Eventually, just store the validator so we don't have to re-parse
    // the CDDL on every validation. For now there are some API issues which may
    // or may not be easily fixable on this side
    // (https://github.com/anweiss/cddl/issues/104) so for now we're doing it in
    // the inefficient way.
    //validator: CDDL,
}

#[pymethods]
impl Schema {
    #[new]
    fn new(schema: String) -> PyResult<Self> {
        // Make sure the schema is OK.
        let mut lexer = lexer_from_str(&schema);
        let parser = cddl_from_str(&mut lexer, &schema, true);
        if let Err(err) = parser {
            return Err(PyValueError::new_err(err));
        }

        Ok(Schema { schema })
    }

    fn validate_cbor(&self, cbor: &[u8]) -> PyResult<()> {
        // Using a parser directly is a pain
        // (https://github.com/anweiss/cddl/issues/105), and we're not actually
        // storing the parser persistently, so just use the higher-level API.
        validate_cbor_from_slice(&self.schema, cbor, None)
            .map_err(|e| ValidationError::new_err(format!("{}", e)))?;
        Ok(())
    }
}

create_exception!(pycddl, ValidationError, PyException);

#[pymodule]
fn pycddl(py: Python, m: &PyModule) -> PyResult<()> {
    m.add("ValidationError", py.get_type::<ValidationError>())?;
    m.add_class::<Schema>()?;
    Ok(())
}
