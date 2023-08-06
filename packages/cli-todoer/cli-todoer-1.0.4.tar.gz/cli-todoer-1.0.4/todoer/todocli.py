import typer
from rich.console import Console
from rich.table import Table
from model import Todo
from database import get_all_todos, delete_todo, insert_todo, complete_todo, update_todo, clear
from datetime import datetime

console = Console()

app = typer.Typer()


@app.command(short_help="add an item from to-do list")
def add(task: str, category: str):
    typer.echo(f"adding {task}, {category}")
    todo = Todo(task, category)
    insert_todo(todo)
    show()


@app.command(short_help="delete an item at specified position from to-do list")
def delete(position: int):
    typer.echo(f"deleting {position}")
    # indices in UI begin at 1, but in database at 0
    delete_todo(position-1)
    show()


@app.command(short_help="update status or description of an item at specified position")
def update(position: int, task: str = None, category: str = None):
    typer.echo(f"updating {position}")
    update_todo(position-1, task, category)
    show()


@app.command(short_help="complete an item at specified position")
def complete(position: int):
    typer.echo(f"complete {position}")
    complete_todo(position-1)
    show()


@app.command(short_help="show list of all tasks for current day")
def show():
    tasks = get_all_todos()
    console.print(f"[bold magenta]Todos on {datetime.today().strftime('%Y-%m-%d')}[/bold magenta]!")
    console.print("[bold green]Remember to finish all tasks for the end of the day. Good luck![/bold green]")

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("#", style="dim", width=6)
    table.add_column("Todo", min_width=20)
    table.add_column("Category", min_width=12, justify="right")
    table.add_column("Done", min_width=12, justify="right")

    def get_category_color(category):
        COLORS = {'Work': 'cyan', 'Sports': 'blue', 'Study': 'yellow', 'Home': 'white', 'Done': 'green'}
        if category in COLORS:
            return COLORS[category]
        return 'white'

    for idx, task in enumerate(tasks, start=1):
        c = get_category_color(task.category)
        is_done_str = "Done" if task.status == 2 else "In progress..."
        cc = get_category_color(is_done_str)
        table.add_row(str(idx), task.task, f"[{c}]{task.category}[/{c}]', f'[{cc}]{is_done_str}[/{cc}]")
    console.print(table)


@app.command(name="clear", short_help="delete all items from list")
def clear_screen(
    force: bool = typer.Option(
        ...,
        prompt="Delete all to-dos?",
        help="Force deletion without confirmation.",
    )):
    if force:
        clear()
        typer.secho("Delete all todoes and clear the screen", fg=typer.colors.RED)
        show()
    else:
        typer.echo("Operation canceled")


def main():
    print("calling main!!!")
    app()


if __name__ == "__main__":
    main()