# In your Python code
from balance_engine import balance_engine, py_init

if __name__ == "__main__":
    # This works with 2 arguments
    result = balance_engine.solve_linear_program([100, 200, 300], [150, 250, 350])
    print(result)  # Should print [10.0, 20.0, 30.0]

    # This works with 3 arguments
    result = balance_engine.solve_linear_program([100, 200, 300], [150, 250, 350], 100)
    print(result)  # Should print [10.0, 20.0, 30.0]

    py_init()  # Initialize the engine
