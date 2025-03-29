#![allow(unused)]

use dev_utils::app_dt;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::cmp::Ordering;
use std::collections::HashMap;

/// A simple linear programming solver for production planning optimization
///
/// This module provides tools to balance production with demand while optimizing resource usage.
#[pymodule]
fn balance_engine(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(solve_linear_program, m)?)?;
    m.add_function(wrap_pyfunction!(optimize_production_plan, m)?)?;
    m.add_function(wrap_pyfunction!(py_init, m)?)?;
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    Ok(())
}

/// Sum two numbers and return the result as a string
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

/// Initialize the balance engine
#[pyfunction]
fn py_init() -> PyResult<()> {
    app_dt!(file!(),
        "package" => ["authors", "license", "description"]
    );
    println!("Balance Engine initialized - Production Planning Optimizer v0.1.0");
    Ok(())
}

/// Solves a linear programming problem with given demand and supply vectors
///
/// Args:
///     demand: A vector of demand values by period
///     supply: A vector of supply capacity values by period
///     capacity: Optional overall capacity constraint
///
/// Returns:
///     A vector of optimized production values
#[pyfunction]
#[pyo3(signature = (demand, supply, capacity=None))]
fn solve_linear_program(
    demand: Vec<f64>,
    supply: Vec<f64>,
    capacity: Option<f64>,
) -> PyResult<Vec<f64>> {
    // Ensure vectors are of equal length
    if demand.len() != supply.len() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Demand and supply vectors must have the same length",
        ));
    }

    // Calculate total demand and available supply
    let total_demand: f64 = demand.iter().sum();
    let total_supply: f64 = supply.iter().sum();

    // If capacity is provided, constrain the total supply
    let effective_supply = if let Some(cap) = capacity {
        total_supply.min(cap)
    } else {
        total_supply
    };

    // Determine if we need to allocate scarce resources or we have excess capacity
    let allocation_factor = if total_demand > effective_supply {
        // Scarce resources - allocate proportionally to demand
        effective_supply / total_demand
    } else {
        // Excess capacity - produce to meet demand
        1.0
    };

    // Calculate the optimized production plan
    let result: Vec<f64> = demand.iter().map(|&d| d * allocation_factor).collect();

    Ok(result)
}

/// Optimizes a production plan for multiple products with resource constraints
///
/// Args:
///     products: A list of product names
///     demand_dict: A dict mapping products to their demand
///     production_rates_dict: A dict mapping products to units produced per hour
///     available_hours: Total available production hours
///     current_inventory_dict: A dict mapping products to current inventory levels
///     min_inventory_dict: A dict mapping products to minimum required inventory
///
/// Returns:
///     A dict with optimized production quantities and resulting inventory
#[pyfunction]
#[pyo3(signature = (products, demand_dict, production_rates_dict, available_hours, current_inventory_dict, min_inventory_dict))]
fn optimize_production_plan(
    py: Python<'_>,
    products: Vec<String>,
    demand_dict: HashMap<String, f64>,
    production_rates_dict: HashMap<String, f64>,
    available_hours: f64,
    current_inventory_dict: HashMap<String, f64>,
    min_inventory_dict: HashMap<String, f64>,
) -> PyResult<PyObject> {
    // Extract values for each product
    let mut product_data: Vec<ProductData> = Vec::new();

    for product in &products {
        // Get demand for this product
        let demand_value = match demand_dict.get(product) {
            Some(&val) => val,
            None => {
                return Err(pyo3::exceptions::PyKeyError::new_err(format!(
                    "Product '{}' not found in demand_dict",
                    product
                )))
            }
        };

        // Get production rate
        let production_rate = match production_rates_dict.get(product) {
            Some(&val) => val,
            None => {
                return Err(pyo3::exceptions::PyKeyError::new_err(format!(
                    "Product '{}' not found in production_rates_dict",
                    product
                )))
            }
        };

        // Get current inventory
        let inventory = match current_inventory_dict.get(product) {
            Some(&val) => val,
            None => {
                return Err(pyo3::exceptions::PyKeyError::new_err(format!(
                    "Product '{}' not found in current_inventory_dict",
                    product
                )))
            }
        };

        // Get minimum inventory requirement
        let min_inv = match min_inventory_dict.get(product) {
            Some(&val) => val,
            None => {
                return Err(pyo3::exceptions::PyKeyError::new_err(format!(
                    "Product '{}' not found in min_inventory_dict",
                    product
                )))
            }
        };

        // Calculate effective demand (actual demand + inventory shortage)
        let effective_demand = demand_value + (min_inv - inventory).max(0.0);

        // Calculate priority (higher for products with inventory below minimum)
        let priority = if inventory < min_inv {
            (min_inv - inventory) / min_inv.max(1.0)
        } else {
            0.0
        };

        product_data.push(ProductData {
            name: product.clone(),
            demand: demand_value,
            effective_demand,
            production_rate,
            inventory,
            min_inventory: min_inv,
            priority,
            hours_needed: effective_demand / production_rate,
        });
    }

    // Sort by priority (higher priority first)
    product_data.sort_by(|a, b| {
        b.priority
            .partial_cmp(&a.priority)
            .unwrap_or(Ordering::Equal)
    });

    // Allocate hours based on priority and need
    let mut remaining_hours = available_hours;
    let mut production_plan = Vec::new();

    for product in &product_data {
        let hours_allocated = product.hours_needed.min(remaining_hours);
        let quantity_produced = hours_allocated * product.production_rate;

        production_plan.push((
            product.name.clone(),
            quantity_produced,
            product.inventory + quantity_produced - product.demand,
        ));

        remaining_hours -= hours_allocated;
        if remaining_hours <= 0.0 {
            break;
        }
    }

    // Print debug info
    println!(
        "DEBUG: Production plan created with {} products",
        production_plan.len()
    );
    for (product, qty, inv) in &production_plan {
        println!(
            "DEBUG: Product: {}, Production: {}, Final Inventory: {}",
            product, qty, inv
        );
    }

    // Create return dictionary
    let result_dict = PyDict::new(py);

    // Production quantities
    let production_dict = PyDict::new(py);
    for (product, quantity, _) in &production_plan {
        production_dict.set_item(product, *quantity)?;
    }
    result_dict.set_item("production", production_dict)?;

    // Final inventory
    let inventory_dict = PyDict::new(py);
    for (product, _, final_inventory) in &production_plan {
        inventory_dict.set_item(product, *final_inventory)?;
    }
    result_dict.set_item("projected_inventory", inventory_dict)?;

    // Hours used
    result_dict.set_item("hours_used", available_hours - remaining_hours)?;

    // Convert to Python object
    Ok(result_dict.to_object(py))
}

/// Internal structure to hold product data for optimization
struct ProductData {
    name: String,
    demand: f64,
    effective_demand: f64,
    production_rate: f64,
    inventory: f64,
    min_inventory: f64,
    priority: f64,
    hours_needed: f64,
}
