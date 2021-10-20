# Book Parser (Research)

This is book resource parser.

It parses given range of book pages of this resource and gets following information about books:

1. Title;
2. Author;
3. Publisher;
4. Publishing year;
5. Cover imager url;
6. Annotation;

To run our parser clone current repo to your system and run

```bash
make install
```

And enter project virtual environment

```bash
poetry shell
```

Then you can run our application from command line by executing following statement:

```bash
make run site="https://[enter resource here]/books/{}/" start=30000 count=3000 max-urls=5000 csv-file=books.csv
```

Arguments in this statement are:

*site* - resource url with {} for id of the book to be placed;

*start* - first book id in the range;

*count* - number of books to get from the resource;

*max-urls* - maximum book urls to be processed;

*csv-file* - the path to csv-file in wich to save parse results.