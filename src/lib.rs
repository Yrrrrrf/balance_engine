#![allow(unused)]

use dev_utils::{app_dt, dlog};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::cmp::Ordering;
use std::collections::HashMap;
use std::time::Instant;

/// A simple linear programming solver for production planning optimization
///
/// This module provides tools to balance production with demand while optimizing resource usage.
#[pymodule]
#[pyo3(name = "engine")] // Esto cambia el nombre del módulo Python a "engine"
fn balance_engine(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(init, m)?)?;
    m.add_function(wrap_pyfunction!(time_exec, m)?)?;
    Ok(())
}

// Mantén la función con el nombre que espera Python
#[pyfunction]
pub fn init() -> PyResult<()> {
    app_dt!(file!(),
        "package" => ["authors", "license", "description"]
    );
    // load the pkg version
    let version = env!("CARGO_PKG_VERSION");
    let mut info = HashMap::new();
    info.insert("version", version);
    println!("{:?}", info);
    println!("270");
    Ok(())
}

#[pyfunction]
fn time_exec(py: Python<'_>, func: Py<PyAny>) -> PyResult<()> {
    let start = Instant::now();
    func.call0(py)?;
    let elapsed = start.elapsed();

    dlog::trace!("- Total execution time: {:?}", elapsed);
    dlog::trace!("- Milliseconds: {:.2}", elapsed.as_millis());
    Ok(())
}
