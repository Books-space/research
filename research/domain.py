from dataclasses import dataclass


@dataclass
class Book:
    id: int
    title: str
    author: str
    publisher: str
    year: int
    isbn: str
    cover_image_url: str
    annotation: str
