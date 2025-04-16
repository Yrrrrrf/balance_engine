"""
Balance Engine - Production Mix Optimization Example

This script demonstrates how to solve a fuel production mix optimization problem
using linear programming.
"""

import engine
import pulp
import matplotlib.pyplot as plt
import numpy as np


def main():
    """Main demonstration function"""
    engine.init()  # Initialize the engine module
    
    print("Balance Engine - Production Mix Optimization Demo")
    
    # Define the problem data
    raw_materials = ['A', 'B', 'C']
    products = ['Super', 'Unleaded', 'Super_Unleaded']
    
    # Raw material properties
    octane_number = {'A': 120, 'B': 90, 'C': 130}
    material_cost = {'A': 38, 'B': 42, 'C': 105}  # euros per ton
    max_available = {'A': 1000, 'B': 1200, 'C': 700}  # tons per day
    
    # Product properties
    octane_requirement = {'Super': 94, 'Unleaded': 92, 'Super_Unleaded': 96}
    selling_price = {'Super': 85, 'Unleaded': 80, 'Super_Unleaded': 88}  # euros per ton
    demand = {'Super': 800, 'Unleaded': 1100, 'Super_Unleaded': 500}  # tons per day
    
    # Create the optimization model
    model = pulp.LpProblem(name="Production_Mix_Optimization", sense=pulp.LpMaximize)
    
    # Decision variables
    # z[i,j] = amount of raw material i used in product j (tons)
    z = {(i, j): pulp.LpVariable(f"z_{i}_{j}", lowBound=0) 
         for i in raw_materials for j in products}
    
    # y[j] = total amount of product j produced (tons)
    y = {j: pulp.LpVariable(f"y_{j}", lowBound=0, upBound=demand[j]) 
         for j in products}
    
    # Objective function: maximize total profit
    revenue = pulp.lpSum([selling_price[j] * y[j] for j in products])
    material_costs = pulp.lpSum([material_cost[i] * z[i, j] for i in raw_materials for j in products])
    
    model += revenue - material_costs, "Total Profit"
    
    # Constraints
    # 1. Raw material availability constraints
    for i in raw_materials:
        model += pulp.lpSum([z[i, j] for j in products]) <= max_available[i], f"Material_Availability_{i}"
    
    # 2. Mass balance constraints (sum of raw materials = product quantity)
    for j in products:
        model += pulp.lpSum([z[i, j] for i in raw_materials]) == y[j], f"Mass_Balance_{j}"
    
    # 3. Octane requirements
    for j in products:
        weighted_octane = pulp.lpSum([octane_number[i] * z[i, j] for i in raw_materials])
        model += weighted_octane >= octane_requirement[j] * y[j], f"Octane_Requirement_{j}"
    
    # Solve the model
    model.solve()
    
    print(f"Status: {pulp.LpStatus[model.status]}")
    
    if model.status == pulp.LpStatusOptimal:
        print("\nOptimal Solution Found:")
        print(f"Total Profit: €{pulp.value(model.objective):.2f}")
        
        # Print production plan
        print("\nProduction Quantities:")
        for j in products:
            print(f"{j}: {y[j].value():.2f} tons (Max demand: {demand[j]} tons)")
        
        # Print raw material usage
        print("\nRaw Material Usage:")
        for i in raw_materials:
            total_used = sum(z[i, j].value() for j in products)
            utilization = total_used / max_available[i] * 100
            print(f"{i}: {total_used:.2f} tons ({utilization:.1f}% of available {max_available[i]} tons)")
        
        # Print product composition for each product
        print("\nProduct Composition:")
        for j in products:
            print(f"\n{j} Mix:")
            if y[j].value() > 0.001:  # Only print if product is produced
                total_product = y[j].value()
                for i in raw_materials:
                    percentage = (z[i, j].value() / total_product) * 100
                    tons_used = z[i, j].value()
                    print(f"  {i}: {percentage:.1f}% ({tons_used:.2f} tons)")
            else:
                print("  Not produced")
        
        # Calculate weighted average octane for each product
        print("\nOctane Verification:")
        for j in products:
            if y[j].value() > 0.001:  # Only print if product is produced
                total_product = y[j].value()
                achieved_octane = sum(octane_number[i] * z[i, j].value() for i in raw_materials) / total_product
                print(f"{j}: Requirement = {octane_requirement[j]}, Achieved = {achieved_octane:.2f}")
        
        # Visualize the results
        plot_results(raw_materials, products, z, y, max_available, demand, octane_requirement, octane_number)
    else:
        print("No optimal solution found.")


def plot_results(raw_materials, products, z, y, max_available, demand, octane_requirement, octane_number):
    """Create visualization of production mix optimization results"""
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15))
    
    # Production quantities vs. demand
    ind = np.arange(len(products))
    width = 0.35
    
    production = [y[j].value() for j in products]
    demand_values = [demand[j] for j in products]
    
    ax1.bar(ind - width/2, production, width, label='Production')
    ax1.bar(ind + width/2, demand_values, width, label='Demand', alpha=0.7)
    ax1.set_ylabel('Tons')
    ax1.set_title('Production vs. Demand')
    ax1.set_xticks(ind)
    ax1.set_xticklabels(products)
    ax1.legend()
    
    # Raw material utilization
    material_usage = [sum(z[i, j].value() for j in products) for i in raw_materials]
    material_capacity = [max_available[i] for i in raw_materials]
    
    ind = np.arange(len(raw_materials))
    ax2.bar(ind, material_usage, width, label='Used')
    ax2.bar(ind, material_capacity, width, label='Available', alpha=0.3)
    ax2.set_ylabel('Tons')
    ax2.set_title('Raw Material Utilization')
    ax2.set_xticks(ind)
    ax2.set_xticklabels(raw_materials)
    ax2.legend()
    
    # Product composition visualization
    bottom = np.zeros(len(products))
    
    # Calculate proportions from the amount variables
    proportions = {}
    for j in products:
        if y[j].value() > 0.001:  # Avoid division by zero
            total_product = y[j].value()
            for i in raw_materials:
                proportions[i, j] = z[i, j].value() / total_product
        else:
            for i in raw_materials:
                proportions[i, j] = 0
    
    for i, material in enumerate(raw_materials):
        values = [proportions[material, j] for j in products]
        ax3.bar(ind, values, width, bottom=bottom, label=f'Material {material}')
        bottom += values
    
    ax3.set_ylabel('Proportion')
    ax3.set_title('Product Composition')
    ax3.set_xticks(ind)
    ax3.set_xticklabels(products)
    ax3.legend()
    
    # Add octane values as text annotations
    for j_idx, j in enumerate(products):
        if y[j].value() > 0.001:  # Only calculate if product is produced
            weighted_octane = sum(octane_number[i] * proportions[i, j] for i in raw_materials)
            ax3.text(j_idx, 1.05, f'Octane: {weighted_octane:.1f}\nReq: {octane_requirement[j]}', 
                    ha='center', va='bottom')
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
    