import json
import argparse
from datetime import datetime


def human_readable_size(size):
    if size < 1024:
        return f"{size}B"
    elif size < 1024**2:
        return f"{size / 1024:.1f}K"
    elif size < 1024**3:
        return f"{size / 1024**2:.1f}M"
    else:
        return f"{size / 1024**3:.1f}G"


def find_path(directory, path):
    components = path.split("/")
    current = directory

    for component in components:
        if component in (".", ""):
            continue
        if "contents" not in current:
            return None
        next_item = next((item for item in current["contents"] if item["name"] == component), None)
        if not next_item:
            return None
        current = next_item

    return current


def list_directory(directory, include_all=False, detailed=False, reverse=False, sort_by_time=False, filter_option=None):
    if "contents" not in directory:
        if detailed:
            permissions = directory["permissions"]
            size = human_readable_size(directory["size"])
            time_modified = datetime.fromtimestamp(directory["time_modified"]).strftime("%b %d %H:%M")
            return [f"{permissions} {size} {time_modified} ./{directory['name']}"]
        else:
            return [directory["name"]]

    contents = directory["contents"]
    result = []

    for item in contents:
        name = item["name"]

        if not include_all and name.startswith("."):
            continue
        if include_all and name in (".", ".."):
            continue

        if filter_option == "file" and "contents" in item:
            continue
        if filter_option == "dir" and "contents" not in item:
            continue

        if detailed:
            permissions = item["permissions"]
            size = human_readable_size(item["size"])
            time_modified = datetime.fromtimestamp(item["time_modified"]).strftime("%b %d %H:%M")
            result.append((name, f"{permissions} {size} {time_modified} {name}", item["time_modified"]))
        else:
            result.append((name, name, item["time_modified"]))

    if sort_by_time:
        result = sorted(result, key=lambda x: x[2])
    else:
        result = sorted(result, key=lambda x: x[0])

    if reverse:
        result = result[::-1]

    return [entry[1] for entry in result]


def main():
    parser = argparse.ArgumentParser(
        description="pyls: A Python implementation of the ls utility for listing directory contents.",
        epilog="Example usage:\n"
               "  pyls                # List all files and directories\n"
               "  pyls -l             # Long listing format\n"
               "  pyls -A             # Include hidden files and directories\n"
               "  pyls -r             # Reverse order\n"
               "  pyls --filter=file  # Show only files",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="The path to the directory or file to list (default: current directory).",
    )
    parser.add_argument(
        "-A",
        "--almost-all",
        action="store_true",
        help="List all entries including those starting with . except . and ..",
    )
    parser.add_argument(
        "-l",
        "--long",
        action="store_true",
        help="Use a long listing format with permissions, size, and timestamps.",
    )
    parser.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        help="Reverse the order of the results.",
    )
    parser.add_argument(
        "-t",
        "--time",
        action="store_true",
        help="Sort the results by time_modified (oldest first).",
    )
    parser.add_argument(
        "--filter",
        type=str,
        choices=["file", "dir"],
        help="Filter the output to show only 'file' or 'dir' entries.",
    )
    args = parser.parse_args()

    try:
        with open("structure.json", "r") as f:
            directory_structure = json.load(f)
    except FileNotFoundError:
        print("Error: 'structure.json' file not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON file. {e}")
        return

    target = find_path(directory_structure, args.path)
    if not target:
        print(f"error: cannot access '{args.path}': No such file or directory")
        return

    items = list_directory(
        target,
        include_all=args.almost_all,
        detailed=args.long,
        reverse=args.reverse,
        sort_by_time=args.time,
        filter_option=args.filter,
    )

    if args.long:
        print("\n".join(items))
    else:
        print(" ".join(items))


if __name__ == "__main__":
    main()
