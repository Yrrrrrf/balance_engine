<h1 align="center">
  <img src="https://raw.githubusercontent.com/Yrrrrrf/balance_engine/refs/heads/main/resources/img/success.png" alt="Balance Engine Optimization Icon" width="128" height="128">
  <div align="center">Balance Engine</div>
</h1>

<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-balance__engine-181717?logo=github)](https://github.com/Yrrrrrf/balance_engine)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://choosealicense.com/licenses/mit/)
[![PyPI version](https://img.shields.io/pypi/v/balance-engine?logo=python)](https://pypi.org/project/balance-engine/)
[![Crates.io](https://img.shields.io/crates/v/balance_engine.svg?logo=rust)](https://crates.io/crates/balance_engine)
[![Crates.io Downloads](https://img.shields.io/crates/d/balance_engine)](https://crates.io/crates/balance_engine)
<!-- [![Downloads](https://pepy.tech/badge/prism-py)](https://pepy.tech/project/prism-py) -->

</div>

> A Python/Rust module for production planning and optimization using linear programming.

**Balance Engine** automates calculations to balance production with demand, allowing for precise and efficient planning while reducing costs. It uses linear programming modeling to optimize resource allocation in limited production cycles.

The tool handles key production variables including:
- Yielded Supply
- On Hand (Finished Goods)
- Safety Stock Targets
- Sellable Supply
- Effective Demand
- Total Projected Inventory Balance

## Installation

### Python Package

```bash
pip install balance-engine
```

### Rust Crate

```bash
cargo add balance_engine
```

## Features

- **Hybrid Architecture**: Core optimization in Rust for performance, Python API for flexibility
- **Production Planning**: Balance supply with demand while respecting capacity constraints
- **Inventory Management**: Calculate optimal inventory levels that meet safety stock requirements
- **Resource Allocation**: Efficiently allocate limited resources in production cycles

## Project Structure

- **Rust Core**: High-performance linear programming solver
- **Python Interface**: Easy-to-use API for integration with data analysis workflows
- **Example Code**: Sample implementations for common production planning scenarios

## Usage

```python
import engine

# Initialize the engine
engine.init()

# Use the optimization functions
result = engine.optimize_production_plan(
    products=["ProductA", "ProductB"],
    demand_dict={"ProductA": 100, "ProductB": 150},
    production_rates_dict={"ProductA": 10, "ProductB": 15},
    available_hours=20,
    current_inventory_dict={"ProductA": 20, "ProductB": 10},
    min_inventory_dict={"ProductA": 10, "ProductB": 20}
)

print(result)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.