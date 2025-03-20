#![allow(unused)]

use dev_utils::app_dt;
use pyo3::prelude::*;

#[pyfunction]
#[pyo3(signature = (demand, supply, capacity=None))]
fn solve_linear_program(
    demand: Vec<f64>,
    supply: Vec<f64>,
    capacity: Option<f64>,
) -> PyResult<Vec<f64>> {
    let _demand = demand;
    let _supply = supply;

    let _capacity = capacity.unwrap_or(0.0);

    let result = vec![10.0, 20.0, 30.0];
    Ok(result)
}

#[pyfunction]
fn py_init() -> PyResult<()> {
    app_dt!(file!(),
        "package" => ["authors", "license", "description"]
    );
    Ok(())
}

#[pymodule]
fn balance_engine(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(solve_linear_program, m)?)?;
    m.add_function(wrap_pyfunction!(py_init, m)?)?;
    Ok(())
}
