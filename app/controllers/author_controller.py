from app.models import Author

def get_authors():
    try:
        authors = Author.query.all()
        authors_data = []
        for author in authors:
            author_data = {
                "id": author.id,
                "name": author.name,
                "age": author.age,
                "books": [],
            }
            for book in author.books:
                book_data = {
                    "id": book.id,
                    "isbn": book.isbn,
                    "name": book.name,
                    "cant_pages": book.cant_pages,
                    "createdAt": book.created_at,
                }
                author_data["books"].append(book_data)
            authors_data.append(author_data)
        return authors_data
    except Exception as error:
        print("Error get_authors: ", error)
        return None
