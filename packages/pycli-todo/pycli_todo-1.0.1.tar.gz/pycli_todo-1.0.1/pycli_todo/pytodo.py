"""Simple to-do list in your terminal! Created with Python :-)"""

import os
import pathlib
import json
from datetime import datetime, timezone

import click
from click_aliases import ClickAliasedGroup


PENDING = "pending"
PENDING_SYMBOL = ("\033[91m" "\u2715" "\033[0m")
WORKING = "working"
WORKING_SYMBOL = ("\033[93m" "\u26A0" "\033[0m")
DONE = "done"
DONE_SYMBOL = ("\033[92m" "\u2713" "\033[0m")

@click.group(cls=ClickAliasedGroup, invoke_without_command=True)
@click.option(
    "-d", "--done",
    default=False,
    is_flag=True,
    help="print done todos")
@click.option(
    "-a",  "--all", "alltodos",
    default=False,
    is_flag=True,
    help="print all todos")
@click.version_option("1.0.1", "-v", "--version")
@click.help_option("-h", "--help")
@click.pass_context
def entry_point(ctx, done, alltodos):
    """
    pyToDo - your Python to-do manager for your terminal.
    """
    if not ctx.invoked_subcommand:
        todo_file = get_todo_list()
        todos = get_tasks(todo_file)
        # print items
        for key, val in todos.items():
            if val["status"] == PENDING and not done:
                print_task(key, val['desc'], PENDING_SYMBOL)
            elif val["status"] == WORKING and not done:
                print_task(key, val['desc'], WORKING_SYMBOL)
            elif val["status"] == DONE and (done or alltodos):
                print_task(key, val['desc'], DONE_SYMBOL)


def print_task(idx, desc, status_symbol):
    click.echo(f"{idx: <3} | {status_symbol} {desc}")


def get_current_timestamp():
    now = datetime.now().astimezone(timezone.utc)
    now_string = now.strftime('%Y-%m-%d %H:%M:%S.%f %z %Z')
    return now_string


def get_todo_list():
    """Find and return to-do file as a pathlib.Path object"""
    base_dir = None
    current_dir = pathlib.Path.cwd()
    for parent_dir in [current_dir, *current_dir.parents]:
        if parent_dir == pathlib.Path.home().parent:
            # doesn't go further than home directory
            break
        todo = parent_dir / ".todo"
        if todo.exists():
            base_dir = parent_dir
    if base_dir is None:
        click.echo(".todo file not found!")
        exit(1)
    todo_file = base_dir / ".todo"
    return todo_file

def get_tasks(todo_file):
    with open(todo_file, "r") as f:
        todos = json.load(f)
    return todos


@entry_point.command(aliases=["i"])
def init():
    """Initialize a collection of to-dos in current directory path"""
    current_dir = pathlib.Path.cwd()
    todo_file = current_dir / ".todo"
    try:
        todo_file.touch(exist_ok=False)
    except FileExistsError:
        click.echo(f"A \".todo\" file already exists in {current_dir}")
        raise SystemExit
    todo_file.write_text("{}\n")
    click.echo(f"A \".todo\" file is now added to {current_dir}")



@entry_point.command()
def split():
    """Print tasks split between categories."""
    todo_file = get_todo_list()
    todos = get_tasks(todo_file)
    # print pending
    print(f"{PENDING_SYMBOL} PENDING")
    for key, val in todos.items():
        if val["status"] == PENDING:
            print_task(key, val['desc'], "")
    click.echo()
    # print in progress
    print(f"{WORKING_SYMBOL} WORKING ON")
    for key, val in todos.items():
        if val["status"] == WORKING:
            print_task(key, val['desc'], "")
    click.echo()
    # print done
    print(f"{DONE_SYMBOL} DONE")
    for key, val in todos.items():
        if val["status"] == DONE:
            print_task(key, val['desc'], "")


@entry_point.command(aliases=["a"])
@click.argument("task")
def add(task):
    """Add a new to-do.

    TASK is the description of the new task."""
    todo_file = get_todo_list()
    todos = get_tasks(todo_file)
    # get new valid id
    keys = todos.keys()
    if len(keys) == 0:
        max_id = 0
    else:
        max_id = max([int(k) for k in keys])
    new_id = max_id + 1
    # assert new_id doesn't exist
    try:
        assert new_id not in todos.keys()
    except AssertionError as e:
        raise ValueError(f"id {new_id} exists!") from e
    # update new task data
    new_task_dict = {}
    new_task_dict["desc"] = task
    new_task_dict["status"] = PENDING
    new_task_dict["modified"] = get_current_timestamp()
    todos[str(new_id)] = new_task_dict
    # write to file
    with open(todo_file, "w") as f:
        json.dump(todos, f, indent=4)


@entry_point.command(aliases=["w"])
@click.argument("task_id", type=int)
def working(task_id):
    """Change the status of a todo to 'working' by giving his id.

    TASK_ID is the id of the task which will change status."""
    todo_file = get_todo_list()
    todos = get_tasks(todo_file)
    # check task_id is valid
    task_id = str(task_id)
    try:
        assert task_id in todos.keys()
    except AssertionError as e:
        raise ValueError(
            f"The todo with the id {task_id} was not found") from e
    # change status
    todos[task_id]["status"] = WORKING
    # update modified
    todos[task_id]["modified"] = get_current_timestamp()
    # write to file
    with open(todo_file, "w") as f:
        json.dump(todos, f, indent=4)


@entry_point.command(aliases=["t"])
@click.argument("task_id", type=int)
def toggle(task_id):
    """Change the status of a todo to 'done' by giving his id.

    TASK_ID is the id of the task which will change status."""
    todo_file = get_todo_list()
    todos = get_tasks(todo_file)
    # check task_id is valid
    task_id = str(task_id)
    try:
        assert task_id in todos.keys()
    except AssertionError as e:
        raise ValueError(
            f"The todo with the id {task_id} was not found") from e
    # change status
    if todos[task_id]["status"] == DONE:
        todos[task_id]["status"] = PENDING
    elif todos[task_id]["status"] in (PENDING, WORKING):
        todos[task_id]["status"] = DONE
    # update modified
    todos[task_id]["modified"] = get_current_timestamp()
    # write to file
    with open(todo_file, "w") as f:
        json.dump(todos, f, indent=4)


@entry_point.command(aliases=["m"])
@click.argument("task_id", type=int)
@click.argument("new_desc", type=str)
def modify(task_id, new_desc):
    """Modify the text of an existing todo.

    \b
    TASK_ID is the id of the task to modify.
    NEW_DESC is the new description of the task."""
    todo_file = get_todo_list()
    todos = get_tasks(todo_file)
    # check task_id is valid
    task_id = str(task_id)
    try:
        assert task_id in todos.keys()
    except AssertionError as e:
        raise ValueError(
            f"The todo with the id {task_id} was not found") from e
    # change description
    todos[task_id]["desc"] = new_desc
    # update modified
    todos[task_id]["modified"] = get_current_timestamp()
    # write to file
    with open(todo_file, "w") as f:
        json.dump(todos, f, indent=4)


@entry_point.command(aliases=["r"])
@click.argument("ids", type=int, nargs=2, required=False)
def reorder(ids):
    """Reset ids of todo (no arguments) or swap the position of two todos.

    IDS are the two ids of the tasks that must be reordered."""
    todo_file = get_todo_list()
    todos = get_tasks(todo_file)
    new_todos = {}
    if ids is None:
        for idx, key in enumerate(todos.keys()):
            new_todos[idx + 1] = todos[key]
        todos = new_todos.copy()
    else:
        # check ids are valid
        id_1 = str(ids[0])
        id_2 = str(ids[1])
        try:
            assert id_1 in todos.keys()
        except AssertionError:
            click.echo(f"The todo with the id {id_1} was not found")
            return
        try:
            assert id_2 in todos.keys()
        except AssertionError:
            click.echo(f"The todo with the id {id_2} was not found")
            return
        # reorder
        task_1 = todos[id_1]
        todos[id_1] = todos[id_2]
        todos[id_2] = task_1
    # write to file
    with open(todo_file, "w") as f:
        json.dump(todos, f, indent=4)


@entry_point.command(aliases=["c"])
def clean():
    """Remove finished todos from the list"""
    todo_file = get_todo_list()
    todos = get_tasks(todo_file)
    # create copy so 'todos' dictionary doesnt change size during iteration
    todos_copy = todos.copy()
    for key, val in todos_copy.items():
        if val["status"] == DONE:
            todos.pop(key)
    # write to file
    with open(todo_file, "w") as f:
        json.dump(todos, f, indent=4)


@entry_point.command(aliases=["s"])
@click.argument("pattern", type=str)
def search(pattern):
    """Search a string in all todos.

    PATTERN is the string to search for among the to-dos."""
    todo_file = get_todo_list()
    todos = get_tasks(todo_file)
    for key, val in todos.items():
        if pattern in val["desc"]:
            if val['status'] == PENDING:
                status_symbol = PENDING_SYMBOL
            elif val['status'] == DONE:
                status_symbol = DONE_SYMBOL
            print_task(key, val['desc'], status_symbol)
