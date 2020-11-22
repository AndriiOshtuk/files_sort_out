import shelve
import shutil
import time
from pathlib import Path

import click

db_filename = "files_sort_out.db"


@click.group()
def cli() -> None:
    """File Sort a tool to organize images on a path.

    To get started, run collect:

      $ files_sort_out collect

    To show collected image folders:

      $ files_sort_out show

    To remove(exclude) directories from list run:

      $ files_sort_out exclude <path>

    Then copy files to a new location:

      $ files_sort_out copy <path>

    Or move files to a new location:

      $ files_sort_out move <path>

    To find files duplicates run:

      $ files_sort_out duplicate <path>
    """
    pass


@cli.command()
@click.argument("root", type=click.Path(resolve_path=True),)
@click.option(
    "-p/-n",
    "--print/--no-print",
    default=True,
    help="Print all collected folders",
    show_default=True,
)
def collect(root: str, print: bool) -> None:
    """Collect folders where images make up 80% of files.

    ROOT is directory to search in
    """
    path = Path(root)
    image_dirs = []

    start_time = time.time()

    with click.progressbar(path.glob("**"), label="Searching:") as bar:
        for d in bar:
            if d.is_dir():
                total_files = 0
                image_files = 0

                for f in d.glob("*"):
                    if f.is_file():
                        total_files = total_files + 1

                        if f.suffix in ('.jpeg', '.jpg', '.bmp', '.png', '.gif', '.tiff'):
                            image_files = image_files + 1

                if total_files and image_files/total_files >= 0.8:
                    image_dirs.append(d)

    elapsed_time = time.time() - start_time
    click.echo(f"Found {len(image_dirs)} directories in {elapsed_time:.2f}s:")

    with shelve.open(db_filename) as db:
        db['image_dirs'] = image_dirs

    if print:
        for d in image_dirs:
            click.echo(str(d))


@cli.command()
@click.argument("dest", default=False, type=click.STRING)
def copy(dest: str) -> None:
    """Copy all or selected folders to DEST"""

    with shelve.open(db_filename, flag='r') as db:
        image_dirs = db['image_dirs']

    if not image_dirs:
        click.echo("No image folders are found.\nRun collect command first")
        return

    start_time = time.time()
    for n, d in enumerate(image_dirs):
        to_dir = Path(dest) / f"0{n}_{d.name}"
        to_dir.mkdir(parents=True)
        for file in d.iterdir():
            if file.is_file():
                to_file = to_dir / file.name
                shutil.copy(file, to_file)

    elapsed_time = time.time() - start_time
    click.echo(f"Copied {n+1}directories. Time:{elapsed_time:.2f}s.")


@cli.command()
def list() -> None:
    pass


@cli.command()
def show() -> None:
    pass


@cli.command()
def exclude() -> None:
    pass


@cli.command()
def move() -> None:
    pass


@cli.command()
def duplicates() -> None:
    pass

if __name__ == "__main__":
    cli()