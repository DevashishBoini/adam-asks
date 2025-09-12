"""
Mini GitHub Copilot CLI
Phase 0, Step 2: CLI Scaffold (argparse)

Usage:
    python main.py askcode "test"
"""
import argparse

# Dummy function for askcode
def askcode(query: str):
    print(f"Query: {query}")
    print("Snippet: def dummy_function(): pass")
    print("Explanation: This is a placeholder snippet returned by the CLI.")


def main():
    parser = argparse.ArgumentParser(description="Mini GitHub Copilot CLI")
    subparsers = parser.add_subparsers(dest="command")

    # askcode command
    askcode_parser = subparsers.add_parser("askcode", help="Ask for code snippet and explanation")
    askcode_parser.add_argument("query", type=str, help="Natural language query")

    args = parser.parse_args()

    if args.command == "askcode":
        askcode(args.query)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
