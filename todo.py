#!/usr/bin/env python3
"""A small command-line to-do app.

Commands:
    add "<task>"    Add a new task.
    list            Show all tasks, numbered, with a checkmark for done items.
    done <number>   Mark the task at <number> as completed.
    clear           Remove all completed tasks.

Tasks are persisted to tasks.json in the same folder as this script.
Only the Python standard library is used (argparse + json).
"""

import argparse
import json
import os

# Store tasks.json next to this script so the data location is predictable
# regardless of the current working directory.
TASKS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")


def load_tasks():
    """Return the list of tasks from disk, or an empty list if none exist."""
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # Corrupt or empty file: start fresh rather than crashing.
            return []


def save_tasks(tasks):
    """Write the list of tasks to disk as formatted JSON."""
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)


def add_task(text):
    """Add a new, incomplete task."""
    tasks = load_tasks()
    tasks.append({"task": text, "done": False})
    save_tasks(tasks)
    print(f'Added: "{text}"')


def list_tasks():
    """Print all tasks as a clean, aligned, numbered list."""
    tasks = load_tasks()
    if not tasks:
        print("No tasks yet. Add one with:  todo.py add \"your task\"")
        return

    # Width of the largest task number, so the column stays aligned
    # even when the list grows past 9 items.
    number_width = len(str(len(tasks)))

    for index, item in enumerate(tasks, start=1):
        mark = "\u2713" if item["done"] else " "  # checkmark or blank
        print(f"{index:>{number_width}}. [{mark}] {item['task']}")


def mark_done(number):
    """Mark the task at the given 1-based position as completed."""
    tasks = load_tasks()
    # Validate the index before touching the data.
    if number < 1 or number > len(tasks):
        print(f"No task number {number}. Run 'list' to see valid numbers.")
        return
    tasks[number - 1]["done"] = True
    save_tasks(tasks)
    print(f'Marked done: "{tasks[number - 1]["task"]}"')


def clear_completed():
    """Remove all completed tasks, keeping the incomplete ones."""
    tasks = load_tasks()
    remaining = [item for item in tasks if not item["done"]]
    removed = len(tasks) - len(remaining)
    save_tasks(remaining)
    print(f"Cleared {removed} completed task(s).")


def build_parser():
    """Configure argparse with one subcommand per feature."""
    parser = argparse.ArgumentParser(description="A simple command-line to-do app.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add "<task>"
    add_parser = subparsers.add_parser("add", help="Add a new task.")
    add_parser.add_argument("task", help="The task description (quote it).")

    # list
    subparsers.add_parser("list", help="List all tasks.")

    # done <number>
    done_parser = subparsers.add_parser("done", help="Mark a task as completed.")
    done_parser.add_argument("number", type=int, help="The task number to mark done.")

    # clear
    subparsers.add_parser("clear", help="Remove all completed tasks.")

    return parser


def main():
    args = build_parser().parse_args()

    if args.command == "add":
        add_task(args.task)
    elif args.command == "list":
        list_tasks()
    elif args.command == "done":
        mark_done(args.number)
    elif args.command == "clear":
        clear_completed()


if __name__ == "__main__":
    main()
