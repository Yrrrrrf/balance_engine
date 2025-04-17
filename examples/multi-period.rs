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
    
    println!("Balance Engine - Multi-Period Production Planning Demo");
    
    // Define the problem data
    let products = vec!["A", "B"];
    let periods = vec!["January", "February", "March"];
    
    // Initial conditions
    let mut initial_inventory = HashMap::new();
    initial_inventory.insert("A", 100.0);
    initial_inventory.insert("B", 120.0);
    
    let mut safety_stock = HashMap::new();
    safety_stock.insert("A", 130.0);
    safety_stock.insert("B", 110.0);
    
    let mut production_cost = HashMap::new();
    production_cost.insert("A", 20.0);
    production_cost.insert("B", 25.0);
    
    let holding_cost_rate = 0.02;  // 2% of production cost
    
    // Calculate holding cost per unit per period
    let mut holding_cost = HashMap::new();
    for &p in &products {
        holding_cost.insert(p, production_cost[&p] * holding_cost_rate);
    }
    
    // Demand forecasts
    let mut demand = HashMap::new();
    demand.insert(("A", "January"), 700.0);
    demand.insert(("A", "February"), 900.0);
    demand.insert(("A", "March"), 1000.0);
    demand.insert(("B", "January"), 800.0);
    demand.insert(("B", "February"), 600.0);
    demand.insert(("B", "March"), 900.0);
    
    // Resource capacities
    let mut machine_capacity = HashMap::new();
    machine_capacity.insert("January", 3000.0);
    machine_capacity.insert("February", 2800.0);
    machine_capacity.insert("March", 3600.0);
    
    let mut labor_capacity = HashMap::new();
    labor_capacity.insert("January", 2500.0);
    labor_capacity.insert("February", 2300.0);
    labor_capacity.insert("March", 2400.0);
    
    // Resource requirements per unit
    let mut machine_hours = HashMap::new();
    machine_hours.insert("A", 1.5);
    machine_hours.insert("B", 1.6);
    
    let mut labor_hours = HashMap::new();
    labor_hours.insert("A", 1.1);
    labor_hours.insert("B", 1.2);
    
    // Create variables for the problem
    let mut vars = variables!();
    
    // x[p,t] = production of product p in period t
    let mut x = HashMap::new();
    for &p in &products {
        for &t in &periods {
            x.insert((p, t), vars.add(variable().min(0.0).integer().name(format!("x_{}_{}", p, t))));
        }
    }
    
    // inv[p,t] = inventory of product p at the end of period t
    let mut inv = HashMap::new();
    for &p in &products {
        for &t in &periods {
            inv.insert((p, t), vars.add(variable().min(0.0).integer().name(format!("inv_{}_{}", p, t))));
        }
    }
    
    // Objective function: minimize total cost (production + inventory holding)
    let mut objective = Expression::from(0.0);
    
    // Production costs
    for &p in &products {
        for &t in &periods {
            objective += production_cost[&p] * *x.get(&(p, t)).unwrap();
        }
    }
    
    // Holding costs
    for &p in &products {
        for &t in &periods {
            objective += holding_cost[&p] * *inv.get(&(p, t)).unwrap();
        }
    }
    
    // Create model with minimization objective
    let mut model = vars.minimise(objective.clone()).using(default_solver);
    
    // Add constraints
    
    // 1. Inventory balance constraints
    for &p in &products {
        for (i, &t) in periods.iter().enumerate() {
            if i == 0 {  // first period
                model = model.with(constraint!(
                    *inv.get(&(p, t)).unwrap() == initial_inventory[&p] + *x.get(&(p, t)).unwrap() - demand[&(p, t)]
                ));
            } else {
                let prev_t = periods[i - 1];
                model = model.with(constraint!(
                    *inv.get(&(p, t)).unwrap() == *inv.get(&(p, prev_t)).unwrap() + *x.get(&(p, t)).unwrap() - demand[&(p, t)]
                ));
            }
        }
    }
    
    // 2. Capacity constraints
    for &t in &periods {
        // Machine capacity
        let mut machine_usage = Expression::from(0.0);
        for &p in &products {
            machine_usage += machine_hours[&p] * *x.get(&(p, t)).unwrap();
        }
        model = model.with(constraint!(machine_usage <= machine_capacity[&t]));
        
        // Labor capacity
        let mut labor_usage = Expression::from(0.0);
        for &p in &products {
            labor_usage += labor_hours[&p] * *x.get(&(p, t)).unwrap();
        }
        model = model.with(constraint!(labor_usage <= labor_capacity[&t]));
    }
    
    // 3. Safety stock requirements (end of planning horizon)
    for &p in &products {
        let last_period = periods.last().unwrap();
        model = model.with(constraint!(*inv.get(&(p, last_period)).unwrap() >= safety_stock[&p]));
    }
    
    // Solve the model
    match model.solve() {
        Ok(solution) => {
            println!("\nOptimal Solution Found:");
            println!("Total Cost: €{:.2}", solution.eval(&objective));
            
            // Print production plan
            println!("\nProduction Plan:");
            println!("{:<10} {:<10} {:<10}", "Period", "Product A", "Product B");
            println!("{}", "-".repeat(30));
            for &t in &periods {
                println!("{:<10} {:<10} {:<10}", 
                         t, 
                         solution.value(*x.get(&("A", t)).unwrap()) as i32,
                         solution.value(*x.get(&("B", t)).unwrap()) as i32);
            }
            
            // Print ending inventory
            println!("\nEnding Inventory:");
            println!("{:<10} {:<10} {:<10}", "Period", "Product A", "Product B");
            println!("{}", "-".repeat(30));
            for &t in &periods {
                println!("{:<10} {:<10} {:<10}", 
                         t, 
                         solution.value(*inv.get(&("A", t)).unwrap()) as i32,
                         solution.value(*inv.get(&("B", t)).unwrap()) as i32);
            }
            
            // Calculate resource utilization
            println!("\nResource Utilization:");
            println!("{:<10} {:<30} {:<30}", 
                     "Period", 
                     "Machine Hours (Used/Available)", 
                     "Labor Hours (Used/Available)");
            println!("{}", "-".repeat(70));
            for &t in &periods {
                let mut machine_used = 0.0;
                let mut labor_used = 0.0;
                
                for &p in &products {
                    machine_used += machine_hours[&p] * solution.value(*x.get(&(p, t)).unwrap());
                    labor_used += labor_hours[&p] * solution.value(*x.get(&(p, t)).unwrap());
                }
                
                let machine_util = machine_used / machine_capacity[&t] * 100.0;
                let labor_util = labor_used / labor_capacity[&t] * 100.0;
                
                println!("{:<10} {:.1}/{} ({:.1}%) {:<5} {:.1}/{} ({:.1}%)",
                         t,
                         machine_used,
                         machine_capacity[&t],
                         machine_util,
                         "",
                         labor_used,
                         labor_capacity[&t],
                         labor_util);
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