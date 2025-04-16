#![allow(unused)]

use dev_utils::{
    app_dt,
    dlog::{self, Level, set_max_level},
};
use good_lp::{Expression, Solution, SolverModel, Variable, constraint, default_solver, variables};
use std::{thread, time::Duration};

/// Solves a production planning optimization problem.
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
        .with(constraint!(
            hours_per_a * product_a + hours_per_b * product_b <= available_hours
        ))
        .with(constraint!(
            material_per_a * product_a + material_per_b * product_b <= available_materials
        ))
        .solve()?;

    // Extract solution values
    let product_a_quantity = solution.value(product_a);
    let product_b_quantity = solution.value(product_b);
    let total_profit = solution.eval(&objective);

    Ok((total_profit, vec![product_a_quantity, product_b_quantity]))
}

fn main() {
    // Display package information with styling
    app_dt!(file!(), "package" => ["license", "keywords", "description", "authors"]);
    set_max_level(Level::Trace);

    // Print ASCII art header
    dlog::info!(
        "
╭───────────────────────────────────────────╮
│                                           │
│       🏭 BALANCE ENGINE OPTIMIZER 🏭       │
│                                           │
╰───────────────────────────────────────────╯"
    );

    // Define available resources with styled section header
    dlog::debug!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    dlog::debug!("📊 RESOURCE CONFIGURATION");
    dlog::debug!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

    let available_hours = 40.0;
    let available_materials = 90.0;

    dlog::info!("Production Hours Available: {} hours", available_hours);
    dlog::info!("Raw Materials Available: {} units", available_materials);

    // Product data display
    dlog::debug!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    dlog::debug!("🏭 PRODUCT SPECIFICATIONS");
    dlog::debug!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

    dlog::info!("Product A: 2 hours/unit, 3 materials/unit, $40 profit/unit");
    dlog::info!("Product B: 1 hour/unit, 4 materials/unit, $30 profit/unit");

    // Solve the production planning problem
    dlog::debug!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    dlog::debug!("🧮 OPTIMIZATION PROCESS");
    dlog::debug!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

    dlog::info!("Running linear optimization solver...");
    thread::sleep(Duration::from_millis(500)); // Simulate processing time

    match solve_production_plan(available_hours, available_materials) {
        Ok((profit, quantities)) => {
            // Results display with visual separation
            dlog::debug!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
            dlog::debug!("✅ OPTIMIZATION RESULTS");
            dlog::debug!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

            // Production plan
            dlog::info!("│ OPTIMAL PRODUCTION PLAN │");
            dlog::info!("├─────────────────────────┤");
            dlog::info!("│ Product A: {:6.2} units │", quantities[0]);
            dlog::info!("│ Product B: {:6.2} units │", quantities[0]);
            dlog::info!("└─────────────────────────┘");

            // Financial results
            dlog::debug!("💰 FINANCIAL PROJECTION");
            dlog::info!("Total Profit: ${:.2}", profit);

            // Resource utilization analysis
            let hours_used = 2.0 * quantities[0] + 1.0 * quantities[1];
            let materials_used = 3.0 * quantities[0] + 4.0 * quantities[1];

            dlog::debug!("📊 RESOURCE UTILIZATION");
            dlog::trace!(
                "Hours: {:.1}/{:.1} hours ({:.1}%)",
                hours_used,
                available_hours,
                (hours_used / available_hours * 100.0)
            );
            dlog::trace!(
                "Materials: {:.1}/{:.1} units ({:.1}%)",
                materials_used,
                available_materials,
                (materials_used / available_materials * 100.0)
            );

            // Show capacity bottleneck
            if hours_used / available_hours > materials_used / available_materials {
                dlog::warn!("⚠️ BOTTLENECK: Production hours are the limiting resource");
            } else {
                dlog::warn!("⚠️ BOTTLENECK: Materials are the limiting resource");
            }

            dlog::debug!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
            dlog::info!("Optimization complete!");
        }
        Err(e) => {
            dlog::error!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
            dlog::error!("❌ OPTIMIZATION FAILED");
            dlog::error!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
            dlog::error!("Error: {}", e);
            dlog::error!("Please check your constraints and try again.");
        }
    }
}
