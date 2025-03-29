"""
Balance Engine - Simple Production Planning Demo

This script demonstrates the basic functionality of the Balance Engine
for optimizing production planning in a manufacturing scenario.
"""

import balance_engine
import matplotlib.pyplot as plt
import numpy as np


def main():
    """Main demonstration function"""
    # Initialize the engine
    balance_engine.py_init()
    print("\n=== Balance Engine Production Planning Demo ===\n")

    # Demonstrate basic optimization
    basic_optimization_demo()

    # Demonstrate multi-product production planning
    multi_product_demo()


def basic_optimization_demo():
    """Simple demonstration of balancing supply and demand across periods"""
    print("DEMO 1: Basic Supply-Demand Optimization")
    print("----------------------------------------")

    # Example: Monthly demand for a product over 6 months
    demand = [120, 150, 180, 200, 170, 140]

    # Example: Available supply capacity over 6 months
    supply = [130, 130, 130, 130, 130, 130]

    # Set overall capacity constraint
    capacity = 750  # Total units that can be produced

    # Solve the linear program
    optimal_production = balance_engine.solve_linear_program(demand, supply, capacity)

    # Print results
    print(f"Demand:              {demand}")
    print(f"Supply Capacity:     {supply}")
    print(f"Total Capacity:      {capacity}")
    print(f"Optimal Production:  {[round(x, 1) for x in optimal_production]}")

    # Check if demand is met
    total_demand = sum(demand)
    total_production = sum(optimal_production)
    print(f"Total Demand:        {total_demand}")
    print(f"Total Production:    {round(total_production, 1)}")
    print(f"Demand Coverage:     {round(total_production / total_demand * 100, 1)}%")

    # Visualize results
    periods = [f"Month {i + 1}" for i in range(len(demand))]

    plt.figure(figsize=(10, 6))
    plt.bar(periods, demand, alpha=0.6, label="Demand")
    plt.bar(periods, optimal_production, alpha=0.8, label="Production")
    plt.plot(periods, supply, "r--", linewidth=2, label="Supply Capacity")
    plt.axhline(
        y=capacity / len(demand), color="k", linestyle="-.", label="Avg. Capacity"
    )
    plt.xlabel("Period")
    plt.ylabel("Units")
    plt.title("Optimized Production Plan")
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig("basic_optimization.png")
    print("\nBasic optimization chart saved as 'basic_optimization.png'\n")


def multi_product_demo():
    """Demonstrates how to optimize production with multiple products and constraints"""
    print("DEMO 2: Multi-Product Production Planning")
    print("----------------------------------------")

    # Example: Product portfolio
    products = ["ProductA", "ProductB", "ProductC", "ProductD"]

    # Monthly demand for each product
    demand = {"ProductA": 200, "ProductB": 150, "ProductC": 300, "ProductD": 100}

    # Production rates (units per hour)
    production_rates = {
        "ProductA": 10,  # 10 units per hour
        "ProductB": 5,  # 5 units per hour
        "ProductC": 7,  # 7 units per hour
        "ProductD": 12,  # 12 units per hour
    }

    # Available production hours
    available_hours = 80  # Total production hours available

    # Current inventory levels
    current_inventory = {"ProductA": 50, "ProductB": 20, "ProductC": 10, "ProductD": 40}

    # Minimum required inventory (safety stock)
    min_inventory = {"ProductA": 40, "ProductB": 30, "ProductC": 60, "ProductD": 20}

    # Optimize production plan
    result = balance_engine.optimize_production_plan(
        products,
        demand,
        production_rates,
        available_hours,
        current_inventory,
        min_inventory,
    )

    # Debug what's being returned
    print("\nResult from Rust:")
    print(result)

    # Extract results
    production = result.get("production", {})
    projected_inventory = result.get("projected_inventory", {})
    hours_used = result.get("hours_used", 0)

    print(f"Production dictionary keys: {production.keys()}")

    # Create a table for display
    headers = ["Product", "Demand", "Current Inv", "Min Inv", "Production", "Final Inv"]

    # Print a simple table
    print("\nProduction Plan:")
    print("-" * 80)
    print(
        f"{headers[0]:<12} {headers[1]:<10} {headers[2]:<12} {headers[3]:<10} {headers[4]:<12} {headers[5]:<12}"
    )
    print("-" * 80)

    # Use the keys from the returned production dictionary
    for product in production.keys():
        prod_amount = round(production.get(product, 0), 1)
        final_inv = round(projected_inventory.get(product, 0), 1)

        print(
            f"{product:<12} {demand.get(product, 0):<10} {current_inventory.get(product, 0):<12} "
            f"{min_inventory.get(product, 0):<10} {prod_amount:<12} {final_inv:<12}"
        )

    print("-" * 80)
    print(f"Hours Used: {round(hours_used, 1)} of {available_hours} available")

    try:
        # Visualize the results if we have data
        products_to_plot = list(production.keys())
        if not products_to_plot:
            print("No production data to plot")
            return

        plt.figure(figsize=(12, 7))

        # Set up the bar chart
        x = np.arange(len(products_to_plot))
        width = 0.15

        # Get values for each product
        demand_values = [demand.get(p, 0) for p in products_to_plot]
        current_inv_values = [current_inventory.get(p, 0) for p in products_to_plot]
        production_values = [production.get(p, 0) for p in products_to_plot]
        final_inv_values = [projected_inventory.get(p, 0) for p in products_to_plot]
        min_inv_values = [min_inventory.get(p, 0) for p in products_to_plot]

        plt.bar(
            x - width * 2,
            demand_values,
            width,
            label="Demand",
            color="#1f77b4",
            alpha=0.7,
        )
        plt.bar(
            x - width,
            current_inv_values,
            width,
            label="Current Inventory",
            color="#ff7f0e",
            alpha=0.7,
        )
        plt.bar(
            x, production_values, width, label="Production", color="#2ca02c", alpha=0.7
        )
        plt.bar(
            x + width,
            final_inv_values,
            width,
            label="Final Inventory",
            color="#d62728",
            alpha=0.7,
        )
        plt.bar(
            x + width * 2,
            min_inv_values,
            width,
            label="Safety Stock",
            color="#9467bd",
            alpha=0.7,
        )

        plt.xlabel("Products")
        plt.ylabel("Units")
        plt.title("Multi-Product Production Plan")
        plt.xticks(x, products_to_plot)
        plt.legend()
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        storage_path = "temp\\multi_product_optimization.png"

        plt.savefig(storage_path)
        print(f"\nMulti-product optimization chart saved as '{storage_path}'\n")
    except Exception as e:
        print(f"Error generating chart: {e}")


if __name__ == "__main__":
    main()
