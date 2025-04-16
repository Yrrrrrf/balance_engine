#![allow(unused)]

use dev_utils::{app_dt, dlog::{self, set_max_level}};
use good_lp::{
    constraint, default_solver, variables, Expression, Solution, SolverModel, Variable,
};
use std::{thread, time::Duration};

/// Solves a basic production planning problem using linear programming.
/// This is a simplified version of Balance Engine's core functionality.
fn solve_production_plan(
    available_hours: f64,
    available_materials: f64,
) -> Result<(f64, Vec<f64>), Box<dyn std::error::Error>> {
    // Initialize decision variables
    let mut vars = variables!();
    
    // Create variables for each product
    let product_a = vars.add_variable(); // Product A quantity
    let product_b = vars.add_variable(); // Product B quantity
    
    // Define resource requirements per unit
    let hours_per_a = 2.0;
    let hours_per_b = 1.0;
    let material_per_a = 3.0;
    let material_per_b = 4.0;
    
    // Define profit per unit
    let profit_a = 40.0;
    let profit_b = 30.0;
    
    // Create objective function (maximize profit)
    let objective = profit_a * product_a + profit_b * product_b;
    
    // Create and solve model with constraints
    let solution = vars
        .maximise(objective.clone())
        .using(default_solver)
        // Add constraint: limited production hours
        .with(constraint!(hours_per_a * product_a + hours_per_b * product_b <= available_hours))
        // Add constraint: limited materials
        .with(constraint!(material_per_a * product_a + material_per_b * product_b <= available_materials))
        // Add non-negativity constraints (implicit in good_lp, but shown for clarity)
        .with(constraint!(product_a >= 0))
        .with(constraint!(product_b >= 0))
        .solve()?;
    
    // Extract solution values
    let product_a_quantity = solution.value(product_a);
    let product_b_quantity = solution.value(product_b);
    let total_profit = solution.eval(&objective);
    
    // Return the optimal profit and production quantities
    Ok((total_profit, vec![product_a_quantity, product_b_quantity]))
}

fn main() {
    // Display package information
    app_dt!(file!(), "package" => ["license", "keywords", "description", "authors"]);
    set_max_level(dlog::Level::Trace);
    
    dlog::info!("Balance Engine - Production Planning Demo");
    
    // Define available resources
    let available_hours = 40.0;
    let available_materials = 90.0;
    
    // Solve the production planning problem
    match solve_production_plan(available_hours, available_materials) {
        Ok((profit, quantities)) => {
            dlog::debug!("Optimal solution found!");
            dlog::info!("Product A: {:.2} units", quantities[0]);
            dlog::info!("Product B: {:.2} units", quantities[1]);
            dlog::info!("Total profit: ${:.2}", profit);
            
            // Resource utilization analysis
            let hours_used = 2.0 * quantities[0] + 1.0 * quantities[1];
            let materials_used = 3.0 * quantities[0] + 4.0 * quantities[1];
            
            dlog::trace!("Resource utilization:");
            dlog::trace!("- Hours: {:.2}/{:.2} ({:.1}%)", 
                         hours_used, available_hours, 
                         (hours_used/available_hours * 100.0));
            dlog::trace!("- Materials: {:.2}/{:.2} ({:.1}%)", 
                        materials_used, available_materials,
                        (materials_used/available_materials * 100.0));
        },
        Err(e) => dlog::error!("Failed to solve production plan: {}", e),
    }
}