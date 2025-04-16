<h1 align="center">
  <img src="https://raw.githubusercontent.com/Yrrrrrf/balance_engine/refs/heads/main/resources/img/success.png" alt="Balance Engine Optimization Icon" width="128" height="128">
  <div align="center">Balance Engine</div>
</h1>

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

```bash
pip install balance-engine
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
### Building from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/balance-engine.git
cd balance-engine

# Build the package
maturin develop

# Run tests
pytest python/tests
```

<!-- ## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. -->
