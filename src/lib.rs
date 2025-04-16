// #![allow(unused)]

use dev_utils::{app_dt, dlog};
// pub mod engine;

use pyo3::prelude::*;
use std::time::Instant;


/// A simple linear programming solver for production planning optimization
///
/// This module provides tools to balance production with demand while optimizing resource usage.
#[pymodule]
#[pyo3(name = "engine")]  // This changes the Python module name to "engine"
fn balance_engine(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Add new functions
    m.add_function(wrap_pyfunction!(init, m)?)?;
    m.add_function(wrap_pyfunction!(time_exec, m)?)?;
    Ok(())
}

/// Display package information and initialize the balance engine
#[pyfunction]
pub fn init() -> PyResult<()> {
    app_dt!(file!(),
        "package" => ["authors", "license", "description"]
    );
    println!("Balance Engine initialized - Production Planning Optimizer v0.1.0");
    Ok(())
}

/// Execute a Python function and measure its execution time
/// 
/// This wrapper allows measuring execution time of any Python function,
/// displaying the results using the dev_utils logging system.
#[pyfunction]
fn time_exec(py: Python<'_>, func: Py<PyAny>) -> PyResult<()> {
    // Start measuring time
    let start = Instant::now();
    
    // Call the Python function - fixed to use the correct PyO3 method
    func.call0(py)?;
    
    // Calculate elapsed time
    let elapsed = start.elapsed();
    
    // Log the execution time
    dlog::trace!("Function timing:");
    dlog::trace!("- Total execution time: {:?}", elapsed);
    dlog::trace!("- Milliseconds: {:.2}", elapsed.as_millis());
    
    // Also print to standard output for immediate feedback
    println!("Function execution time: {:?}", elapsed);
    
    Ok(())
}
