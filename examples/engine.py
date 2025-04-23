"""
Balance Engine - Inventory Management LP Example

This example demonstrates a simple Linear Programming model for inventory
optimization that minimizes shortage and overstock costs.
"""

import pulp


def lp_model(products, periods, initial_inventory, effective_demand, yielded_supply, 
             safety_stock_target, shortage_cost, excess_cost):
    """
    Linear Programming model for inventory optimization
    
    Args:
        products: List of product identifiers
        periods: List of time periods
        initial_inventory: Dict with initial inventory per product
        effective_demand: Dict with demand per (product, period)
        yielded_supply: Dict with supply per (product, period)
        safety_stock_target: Dict with safety stock targets per product
        shortage_cost: Cost per unit of shortage
        excess_cost: Cost per unit of excess inventory above SST
    
    Returns:
        Dict containing optimization results
    """
    # Create the LP problem
    model = pulp.LpProblem("Inventory_Management", pulp.LpMinimize)
    
    # Decision variables
    # x[i,t] = final inventory of product i in period t
    inventory = pulp.LpVariable.dicts(
        "Inventory",
        [(i, t) for i in products for t in periods],
        lowBound=0,
        cat="Continuous"
    )
    
    # s[i,t] = shortage of product i in period t
    shortage = pulp.LpVariable.dicts(
        "Shortage",
        [(i, t) for i in products for t in periods],
        lowBound=0,
        cat="Continuous"
    )
    
    # e[i,t] = excess inventory above SST for product i in period t
    excess = pulp.LpVariable.dicts(
        "Excess",
        [(i, t) for i in products for t in periods],
        lowBound=0,
        cat="Continuous"
    )
    
    # Objective function: minimize shortage and excess costs
    model += pulp.lpSum([
        shortage_cost * shortage[i, t] + excess_cost * excess[i, t]
        for i in products
        for t in periods
    ]), "Total_Cost"
    
    # Constraints
    for i in products:
        for t_idx, t in enumerate(periods):
            # Inventory balance equation
            if t_idx == 0:  # First period
                model += (
                    inventory[i, t] == initial_inventory[i] + 
                    yielded_supply[i, t] - effective_demand[i, t] + shortage[i, t],
                    f"Balance_{i}_{t}"
                )
            else:  # Subsequent periods
                prev_t = periods[t_idx - 1]
                model += (
                    inventory[i, t] == inventory[i, prev_t] + 
                    yielded_supply[i, t] - effective_demand[i, t] + shortage[i, t],
                    f"Balance_{i}_{t}"
                )
            
            # Excess inventory calculation
            model += (
                excess[i, t] >= inventory[i, t] - safety_stock_target[i],
                f"Excess_Calc_{i}_{t}"
            )
            
            # Shortage calculation
            if t_idx == 0:
                model += (
                    shortage[i, t] >= effective_demand[i, t] - 
                    (initial_inventory[i] + yielded_supply[i, t]),
                    f"Shortage_Calc_{i}_{t}"
                )
            else:
                prev_t = periods[t_idx - 1]
                model += (
                    shortage[i, t] >= effective_demand[i, t] - 
                    (inventory[i, prev_t] + yielded_supply[i, t]),
                    f"Shortage_Calc_{i}_{t}"
                )
    
    # Solve the model
    model.solve()
    
    # Prepare results
    results = {
        'status': pulp.LpStatus[model.status],
        'total_cost': pulp.value(model.objective),
        'inventory': {(i, t): inventory[i, t].value() for i in products for t in periods},
        'shortage': {(i, t): shortage[i, t].value() for i in products for t in periods},
        'excess': {(i, t): excess[i, t].value() for i in products for t in periods}
    }
    
    return results


def main():
    """Main function for inventory optimization example"""
    
    print("Balance Engine - Inventory Management Optimization")
    
    # Define problem parameters
    products = ["Product_A", "Product_B"]
    periods = ["Jan", "Feb", "Mar"]
    
    # Initial inventory for each product
    initial_inventory = {
        "Product_A": 100,
        "Product_B": 150
    }
    
    # Demand forecast for each product in each period
    effective_demand = {
        ("Product_A", "Jan"): 250,
        ("Product_A", "Feb"): 300,
        ("Product_A", "Mar"): 400,
        ("Product_B", "Jan"): 200,
        ("Product_B", "Feb"): 180,
        ("Product_B", "Mar"): 220
    }
    
    # Production capacity (yielded supply) for each product in each period
    yielded_supply = {
        ("Product_A", "Jan"): 280,
        ("Product_A", "Feb"): 350,
        ("Product_A", "Mar"): 300,
        ("Product_B", "Jan"): 180,
        ("Product_B", "Feb"): 200,
        ("Product_B", "Mar"): 250
    }
    
    # Safety stock targets for each product
    safety_stock_target = {
        "Product_A": 80,
        "Product_B": 60
    }

    # Cost parameters
    shortage_cost = 5.0  # Cost per unit of shortage
    excess_cost = 1.5    # Cost per unit of excess inventory above SST
    
    # Solve the LP model
    results = lp_model(
        products=products,
        periods=periods,
        initial_inventory=initial_inventory,
        effective_demand=effective_demand,
        yielded_supply=yielded_supply,
        safety_stock_target=safety_stock_target,
        shortage_cost=shortage_cost,
        excess_cost=excess_cost
    )
    
    # Print results
    print(f"\nOptimization Status: {results['status']}")
    print(f"Total Cost: ${results['total_cost']:.2f}")
    
    # Display results in tabular format
    print("\n" + "="*60)
    print("Results Summary")
    print("="*60)
    
    for i in products:
        print(f"\n{i}:")
        print(f"{'Period':<8} {'Inventory':<12} {'Shortage':<12} {'Excess':<12}")
        print("-"*45)
        for t in periods:
            inv_val = results['inventory'].get((i, t), 0) or 0
            short_val = results['shortage'].get((i, t), 0) or 0
            exc_val = results['excess'].get((i, t), 0) or 0
            print(f"{t:<8} {inv_val:<12.1f} {short_val:<12.1f} {exc_val:<12.1f}")
    
    # Cost breakdown
    print("\n" + "="*40)
    print("Cost Breakdown")
    print("="*40)
    
    total_shortage_cost = sum(
        shortage_cost * (results['shortage'].get((i, t), 0) or 0)
        for i in products for t in periods
    )
    total_excess_cost = sum(
        excess_cost * (results['excess'].get((i, t), 0) or 0)
        for i in products for t in periods
    )
    
    print(f"Total shortage cost: ${total_shortage_cost:.2f}")
    print(f"Total excess cost: ${total_excess_cost:.2f}")
    print(f"Total cost: ${total_shortage_cost + total_excess_cost:.2f}")


if __name__ == "__main__":
    # import engine

    # engine.some_init()
    main()
