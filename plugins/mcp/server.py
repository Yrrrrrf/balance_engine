import random
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
main_mcp: FastMCP = FastMCP("Balance Engine")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get("event", "Unknown")}
Area: {props.get("areaDesc", "Unknown")}
Severity: {props.get("severity", "Unknown")}
Description: {props.get("description", "No description available")}
Instructions: {props.get("instruction", "No specific instructions provided")}
"""


@main_mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@main_mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period["name"]}:
Temperature: {period["temperature"]}°{period["temperatureUnit"]}
Wind: {period["windSpeed"]} {period["windDirection"]}
Forecast: {period["detailedForecast"]}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)

@main_mcp.tool()
def random_and_square() -> str:
    """Return a random integer and its square."""
    n = random.randint(1, 100)
    return f"Random number: {n}\nSquare: {n**2}"

# * LP Model

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

@main_mcp.tool()
async def optimize_inventory(
    products: list[str], 
    periods: list[str], 
    initial_inventory: dict[str, float], 
    effective_demand: dict[str, float], 
    yielded_supply: dict[str, float], 
    safety_stock_target: dict[str, float], 
    shortage_cost: float, 
    excess_cost: float
) -> str:
    """Optimize inventory management using linear programming.
    
    This tool solves an inventory optimization problem to minimize total costs 
    from shortages and excess inventory.
    
    Args:
        products: List of product identifiers (e.g., ["Widget_A", "Widget_B"])
        periods: List of time periods (e.g., ["January", "February", "March"])
        initial_inventory: Dict with initial inventory per product (e.g., {"Widget_A": 100, "Widget_B": 150})
        effective_demand: Dict with demand using "product_period" as key (e.g., {"Widget_A_January": 250, "Widget_A_February": 300})
        yielded_supply: Dict with supply using "product_period" as key (e.g., {"Widget_A_January": 280, "Widget_A_February": 350})
        safety_stock_target: Dict with safety stock targets per product (e.g., {"Widget_A": 80, "Widget_B": 60})
        shortage_cost: Cost per unit of shortage (e.g., 5.0)
        excess_cost: Cost per unit of excess inventory above SST (e.g., 1.5)
    
    Note: For effective_demand and yielded_supply, use the format "product_period" as the key, 
    separating product and period with an underscore. For example:
    effective_demand = {
        "Widget_A_January": 250,
        "Widget_A_February": 300,
        "Widget_B_January": 200
    }
    """
    # Convert string keys back to tuples for the original lp_model function
    demand_tuples = {}
    supply_tuples = {}
    
    for key, value in effective_demand.items():
        parts = key.split('_', 1)
        if len(parts) == 2:
            product = parts[0] + '_' + parts[1].split('_')[0]  # Handle products with underscores
            period = parts[1].split('_', 1)[1] if '_' in parts[1] else parts[1]
            demand_tuples[(product, period)] = value
    
    for key, value in yielded_supply.items():
        parts = key.split('_', 1)
        if len(parts) == 2:
            product = parts[0] + '_' + parts[1].split('_')[0]  # Handle products with underscores
            period = parts[1].split('_', 1)[1] if '_' in parts[1] else parts[1]
            supply_tuples[(product, period)] = value
    
    # Run the original LP model
    results = lp_model(
        products=products,
        periods=periods,
        initial_inventory=initial_inventory,
        effective_demand=demand_tuples,
        yielded_supply=supply_tuples,
        safety_stock_target=safety_stock_target,
        shortage_cost=shortage_cost,
        excess_cost=excess_cost
    )
    
    # Format results into a readable string
    output = []
    output.append("Inventory Optimization Results")
    output.append("=" * 30)
    output.append(f"Status: {results['status']}")
    output.append(f"Total Cost: ${results['total_cost']:.2f}")
    output.append("")
    
    # Results by product
    for product in products:
        output.append(f"\n{product}:")
        output.append(f"{'Period':<8} {'Inventory':<12} {'Shortage':<12} {'Excess':<12}")
        output.append("-" * 45)
        for period in periods:
            inv_val = results['inventory'].get((product, period), 0) or 0
            short_val = results['shortage'].get((product, period), 0) or 0
            exc_val = results['excess'].get((product, period), 0) or 0
            output.append(f"{period:<8} {inv_val:<12.1f} {short_val:<12.1f} {exc_val:<12.1f}")
    
    # Cost breakdown
    output.append("\nCost Breakdown")
    output.append("=" * 20)
    
    total_shortage_cost = sum(
        shortage_cost * (results['shortage'].get((i, t), 0) or 0)
        for i in products for t in periods
    )
    total_excess_cost = sum(
        excess_cost * (results['excess'].get((i, t), 0) or 0)
        for i in products for t in periods
    )
    
    output.append(f"Total shortage cost: ${total_shortage_cost:.2f}")
    output.append(f"Total excess cost: ${total_excess_cost:.2f}")
    output.append(f"Total cost: ${total_shortage_cost + total_excess_cost:.2f}")
    
    return "\n".join(output)
