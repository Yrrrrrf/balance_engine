"""
Balance Engine - Multi-Period Production Planning Example

This script demonstrates how to solve a multi-period production planning problem
using linear programming optimization.
"""

import pulp
import matplotlib.pyplot as plt
import numpy as np
import engine


def main():
    """Main demonstration function"""
    engine.init()  # Initialize the engine module

    print("Balance Engine - Multi-Period Production Planning Demo")

    # Define the problem data
    products = ["A", "B"]
    periods = ["January", "February", "March"]

    # Initial conditions
    initial_inventory = {"A": 100, "B": 120}
    safety_stock = {"A": 130, "B": 110}
    production_cost = {"A": 20, "B": 25}  # in euros
    holding_cost_rate = 0.02  # 2% of production cost

    # Calculate holding cost per unit per period
    holding_cost = {p: production_cost[p] * holding_cost_rate for p in products}

    # Demand forecasts
    demand = {
        ("A", "January"): 700,
        ("A", "February"): 900,
        ("A", "March"): 1000,
        ("B", "January"): 800,
        ("B", "February"): 600,
        ("B", "March"): 900,
    }

    # Resource capacities
    machine_capacity = {"January": 3000, "February": 2800, "March": 3600}
    labor_capacity = {"January": 2500, "February": 2300, "March": 2400}

    # Resource requirements per unit
    machine_hours = {"A": 1.5, "B": 1.6}
    labor_hours = {"A": 1.1, "B": 1.2}

    # Create the optimization model
    model = pulp.LpProblem(
        name="Multi_Period_Production_Planning", sense=pulp.LpMinimize
    )

    # Decision variables
    # x[p,t] = production of product p in period t
    x = {
        (p, t): pulp.LpVariable(f"x_{p}_{t}", lowBound=0, cat=pulp.LpInteger)
        for p in products
        for t in periods
    }

    # inv[p,t] = inventory of product p at the end of period t
    inv = {
        (p, t): pulp.LpVariable(f"inv_{p}_{t}", lowBound=0, cat=pulp.LpInteger)
        for p in products
        for t in periods
    }

    # Objective function: minimize total cost (production + inventory holding)
    total_production_cost = pulp.lpSum(
        [production_cost[p] * x[p, t] for p in products for t in periods]
    )
    total_holding_cost = pulp.lpSum(
        [holding_cost[p] * inv[p, t] for p in products for t in periods]
    )

    model += total_production_cost + total_holding_cost, "Total Cost"

    # Constraints
    # 1. Inventory balance constraints
    for p in products:
        for i, t in enumerate(periods):
            if i == 0:  # first period
                model += (
                    inv[p, t] == initial_inventory[p] + x[p, t] - demand[p, t],
                    f"Inventory_Balance_{p}_{t}",
                )
            else:
                prev_t = periods[i - 1]
                model += (
                    inv[p, t] == inv[p, prev_t] + x[p, t] - demand[p, t],
                    f"Inventory_Balance_{p}_{t}",
                )

    # 2. Capacity constraints
    for t in periods:
        # Machine capacity
        model += (
            pulp.lpSum([machine_hours[p] * x[p, t] for p in products])
            <= machine_capacity[t],
            f"Machine_Capacity_{t}",
        )
        # Labor capacity
        model += (
            pulp.lpSum([labor_hours[p] * x[p, t] for p in products])
            <= labor_capacity[t],
            f"Labor_Capacity_{t}",
        )

    # 3. Safety stock requirements (end of planning horizon)
    for p in products:
        model += inv[p, periods[-1]] >= safety_stock[p], f"Safety_Stock_{p}"

    # Solve the model
    model.solve()

    print(f"Status: {pulp.LpStatus[model.status]}")

    if model.status == pulp.LpStatusOptimal:
        print("\nOptimal Solution Found:")
        print(f"Total Cost: €{pulp.value(model.objective):.2f}")

        # Print production plan
        print("\nProduction Plan:")
        print(f"{'Period':<10} {'Product A':<10} {'Product B':<10}")
        print("-" * 30)
        for t in periods:
            print(f"{t:<10} {int(x['A', t].value()):<10} {int(x['B', t].value()):<10}")

        # Print ending inventory
        print("\nEnding Inventory:")
        print(f"{'Period':<10} {'Product A':<10} {'Product B':<10}")
        print("-" * 30)
        for t in periods:
            print(
                f"{t:<10} {int(inv['A', t].value()):<10} {int(inv['B', t].value()):<10}"
            )

        # Calculate resource utilization
        print("\nResource Utilization:")
        print(
            f"{'Period':<10} {'Machine Hours (Used/Available)':<30} {'Labor Hours (Used/Available)':<30}"
        )
        print("-" * 70)
        for t in periods:
            machine_used = sum(machine_hours[p] * x[p, t].value() for p in products)
            machine_util = machine_used / machine_capacity[t] * 100
            labor_used = sum(labor_hours[p] * x[p, t].value() for p in products)
            labor_util = labor_used / labor_capacity[t] * 100
            print(
                f"{t:<10} {machine_used:.1f}/{machine_capacity[t]} ({machine_util:.1f}%) {' ' * 5} {labor_used:.1f}/{labor_capacity[t]} ({labor_util:.1f}%)"
            )

        # Visualize the results
        plot_results(periods, products, x, inv, demand)
    else:
        print("No optimal solution found.")


def plot_results(periods, products, x, inv, demand):
    """Create visualization of production and inventory over time"""
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))

    # Production plot
    ind = np.arange(len(periods))
    width = 0.35

    prod_a = [x["A", t].value() for t in periods]
    prod_b = [x["B", t].value() for t in periods]

    ax1.bar(ind - width / 2, prod_a, width, label="Product A")
    ax1.bar(ind + width / 2, prod_b, width, label="Product B")
    ax1.set_ylabel("Units")
    ax1.set_title("Production Quantities")
    ax1.set_xticks(ind)
    ax1.set_xticklabels(periods)
    ax1.legend()

    # Inventory plot
    inv_a = [inv["A", t].value() for t in periods]
    inv_b = [inv["B", t].value() for t in periods]

    ax2.plot(periods, inv_a, "o-", label="Product A")
    ax2.plot(periods, inv_b, "s-", label="Product B")
    ax2.set_ylabel("Units")
    ax2.set_title("Ending Inventory Levels")
    ax2.legend()
    ax2.grid(True)

    # Production vs Demand
    demand_a = [demand["A", t] for t in periods]
    demand_b = [demand["B", t] for t in periods]

    ax3.plot(periods, prod_a, "o-", label="Production A")
    ax3.plot(periods, demand_a, "o--", label="Demand A")
    ax3.plot(periods, prod_b, "s-", label="Production B")
    ax3.plot(periods, demand_b, "s--", label="Demand B")
    ax3.set_ylabel("Units")
    ax3.set_title("Production vs Demand")
    ax3.legend()
    ax3.grid(True)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
