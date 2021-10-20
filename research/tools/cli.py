import typer

from research.tools.run import run

app = typer.Typer()


@app.command()
def launch(
    site: str = typer.Option(default=None),
    start: int = typer.Option(default=None), 
    count: int = typer.Option(default=None), 
    max_urls: int = typer.Option(default=None),
    csv_file: str = typer.Option(default=None),
):

    run(site, start, count, max_urls, csv_file)


if __name__ == '__main__':
    app()
