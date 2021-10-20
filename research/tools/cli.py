import typer

from research.parsers.sites import SiteParser
from research.storage import BookStorage

app = typer.Typer()

optinal = typer.Option(default=None)


@app.command()
def launch(
    site: str = optinal,  # noqa: WPS404
    start: int = optinal,  # noqa: WPS404
    count: int = optinal,  # noqa: WPS404
    max_urls: int = optinal,  # noqa: WPS404
    csv_file: str = optinal,  # noqa: WPS404
):

    site_parser = SiteParser(
        url=site,
        count=count,
        max_checks=max_urls,
        start=start,
    )

    books = site_parser.parse()
    BookStorage().to_csv(books, csv_file)


if __name__ == '__main__':
    app()
