from server import main_mcp


def main():
    print("\033[H\033[J", end="")
    print("Starting MCP server...")
    main_mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
