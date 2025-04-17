#![allow(unused)]

use std::{collections::HashMap, time::Instant};
use good_lp::{
    constraint, default_solver, variable, variables, Expression, Solution, SolverModel
};

fn main() {
    // Start timing
    let start_time = Instant::now();
    
    // Initialize engine (as per template)
    engine::init();
    
    println!("Balance Engine - Production Mix Optimization Demo");
    
    // Define the problem data
    let raw_materials = vec!["A", "B", "C"];
    let products = vec!["Super", "Unleaded", "Super_Unleaded"];
    
    // Raw material properties
    let mut octane_number = HashMap::new();
    octane_number.insert("A", 120.0);
    octane_number.insert("B", 90.0);
    octane_number.insert("C", 130.0);
    
    let mut material_cost = HashMap::new();
    material_cost.insert("A", 38.0);
    material_cost.insert("B", 42.0);
    material_cost.insert("C", 105.0);
    
    let mut max_available = HashMap::new();
    max_available.insert("A", 1000.0);
    max_available.insert("B", 1200.0);
    max_available.insert("C", 700.0);
    
    // Product properties
    let mut octane_requirement = HashMap::new();
    octane_requirement.insert("Super", 94.0);
    octane_requirement.insert("Unleaded", 92.0);
    octane_requirement.insert("Super_Unleaded", 96.0);
    
    let mut selling_price = HashMap::new();
    selling_price.insert("Super", 85.0);
    selling_price.insert("Unleaded", 80.0);
    selling_price.insert("Super_Unleaded", 88.0);
    
    let mut demand = HashMap::new();
    demand.insert("Super", 800.0);
    demand.insert("Unleaded", 1100.0);
    demand.insert("Super_Unleaded", 500.0);
    
    // Create variables for the problem
    let mut vars = variables!();
    
    // z[i,j] = amount of raw material i used in product j (tons)
    let mut z = HashMap::new();
    for &i in &raw_materials {
        for &j in &products {
            z.insert((i, j), vars.add(variable().min(0.0).name(format!("z_{}_{}", i, j))));
        }
    }
    
    // y[j] = total amount of product j produced (tons)
    let mut y = HashMap::new();
    for &j in &products {
        y.insert(j, vars.add(variable().min(0.0).max(*demand.get(j).unwrap()).name(format!("y_{}", j))));
    }
    
    // Objective function: maximize total profit
    let mut objective = Expression::from(0.0);
    
    // Revenue part
    for &j in &products {
        objective += *selling_price.get(j).unwrap() * *y.get(j).unwrap();
    }
    
    // Material costs part
    for &i in &raw_materials {
        for &j in &products {
            objective -= *material_cost.get(i).unwrap() * *z.get(&(i, j)).unwrap();
        }
    }
    
    // Create model with maximization objective
    let mut model = vars.maximise(objective.clone()).using(default_solver);
    
    // Add constraints
    
    // 1. Raw material availability constraints
    for &i in &raw_materials {
        let mut usage = Expression::from(0.0);
        for &j in &products {
            usage += z.get(&(i, j)).unwrap();
        }
        model = model.with(constraint!(usage <= *max_available.get(i).unwrap()));
    }
    
    // 2. Mass balance constraints (sum of raw materials = product quantity)
    for &j in &products {
        let mut sum_materials = Expression::from(0.0);
        for &i in &raw_materials {
            sum_materials += z.get(&(i, j)).unwrap();
        }
        model = model.with(constraint!(sum_materials == y.get(j).unwrap()));
    }
    
    // 3. Octane requirements
    for &j in &products {
        let mut weighted_octane = Expression::from(0.0);
        for &i in &raw_materials {
            weighted_octane += *octane_number.get(i).unwrap() * *z.get(&(i, j)).unwrap();
        }
        let octane_req = *octane_requirement.get(j).unwrap() * *y.get(j).unwrap();
        model = model.with(constraint!(weighted_octane >= octane_req));
    }
    
    // Solve the model
    match model.solve() {
        Ok(solution) => {
            println!("\nOptimal Solution Found:");
            println!("Total Profit: €{:.2}", solution.eval(&objective));
            
            // Print production plan
            println!("\nProduction Quantities:");
            for &j in &products {
                let amount = solution.value(*y.get(j).unwrap());
                println!("{}: {:.2} tons (Max demand: {} tons)", j, amount, demand.get(j).unwrap());
            }
            
            // Print raw material usage
            println!("\nRaw Material Usage:");
            for &i in &raw_materials {
                let mut total_used = 0.0;
                for &j in &products {
                    total_used += solution.value(*z.get(&(i, j)).unwrap());
                }
                let utilization = total_used / max_available.get(i).unwrap() * 100.0;
                println!("{}: {:.2} tons ({:.1}% of available {} tons)", 
                         i, total_used, utilization, max_available.get(i).unwrap());
            }
            
            // Print product composition for each product
            println!("\nProduct Composition:");
            for &j in &products {
                println!("\n{} Mix:", j);
                let total_product = solution.value(*y.get(j).unwrap());
                if total_product > 0.001 {  // Only print if product is produced
                    for &i in &raw_materials {
                        let tons_used = solution.value(*z.get(&(i, j)).unwrap());
                        let percentage = (tons_used / total_product) * 100.0;
                        println!("  {}: {:.1}% ({:.2} tons)", i, percentage, tons_used);
                    }
                } else {
                    println!("  Not produced");
                }
            }
            
            // Calculate weighted average octane for each product
            println!("\nOctane Verification:");
            for &j in &products {
                let total_product = solution.value(*y.get(j).unwrap());
                if total_product > 0.001 {  // Only print if product is produced
                    let mut weighted_octane_sum = 0.0;
                    for &i in &raw_materials {
                        weighted_octane_sum += octane_number.get(i).unwrap() * solution.value(*z.get(&(i, j)).unwrap());
                    }
                    let achieved_octane = weighted_octane_sum / total_product;
                    println!("{}: Requirement = {}, Achieved = {:.2}", 
                             j, octane_requirement.get(j).unwrap(), achieved_octane);
                }
            }
            
        },
        Err(e) => {
            println!("No optimal solution found. Error: {:?}", e);
        }
    }
    
    // Print elapsed time
    let elapsed = start_time.elapsed();
    println!("\nTime elapsed: {:?}", elapsed);
}
