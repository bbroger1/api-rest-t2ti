from flask import Flask, Response, request, jsonify, render_template

from models import db, Author, Book

app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = ("sqlite:////tmp/test.db")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql+psycopg2://postgres:root@localhost:5432/teste"
)

db.init_app(app)


@app.route("/")
def index():
    title = "RCS Soft - Livraria"
    return render_template("index.html", title=title)


@app.route("/authors/list")
def listAuthors():
    response = get_authors()
    autores = []
    if isinstance(response, Response):
        if response.json:
            autores = response.json["authors"]
        else:
            autores = []
    return render_template("list-author.html", autores=autores)


@app.route("/authors", methods=["GET"])
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
        return jsonify({"authors": authors_data})
    except Exception as error:
        print("Error", error)
        return jsonify({"message": "Internal server error"}), 500


@app.route("/authors/form", methods=["GET", "POST"])
def addFormAuthor():
    return render_template("form-author.html")


@app.route("/authors", methods=["POST"])
def add_author():
    try:
        content_type = request.headers.get("Content-Type")

        if content_type:
            if (
                "multipart/form-data" in content_type
                or "application/x-www-form-urlencoded" in content_type
            ):
                # A solicitação veio de um formulário HTML
                name = request.form.get("name")
                age = request.form.get("age")
            elif "application/json" in content_type:
                # A solicitação veio de uma chamada de API
                data = request.get_json()
                name = data["name"]
                age = data["age"]
            else:
                # Tipo de conteúdo desconhecido
                return "Tipo de conteúdo desconhecido", 400

        if not name or not age:
            return jsonify({"message": "Bad request, name or age not found"}), 400

        new_author = Author(name=name, age=age)
        db.session.add(new_author)
        db.session.commit()

        if content_type:
            if (
                "multipart/form-data" in content_type
                or "application/x-www-form-urlencoded" in content_type
            ):
                response = get_authors()
                autores = []
                if isinstance(response, Response):
                    if response.json:
                        autores = response.json["authors"]
                    else:
                        autores = []
                return render_template("list-author.html", autores=autores)

        return (
            jsonify(
                {
                    "author": {
                        "id": new_author.id,
                        "name": new_author.name,
                        "age": new_author.age,
                    }
                }
            ),
            201,
        )
    except Exception as error:
        print("Error", error)
        return jsonify({"message": "Internal server error"}), 500


@app.route("/books/list")
def listBooks():
    response = get_books()
    if isinstance(response, Response):
        if response.json:
            books = response.json["books"]
        else:
            books = []
    else:
        print("Response: ", response)
        books = []

    return render_template("list-book.html", livros=books)


@app.route("/books", methods=["GET"])
def get_books():
    try:
        books = Book.query.all()
        books_data = []
        for book in books:
            book_data = {
                "id": book.id,
                "isbn": book.isbn,
                "name": book.name,
                "cant_pages": book.cant_pages,
                "author_id": book.author_id,
                "author": {
                    "id": book.author.id,
                    "name": book.author.name,
                    "age": book.author.age,
                },
            }
            books_data.append(book_data)
        return jsonify({"books": books_data})
    except Exception as error:
        print("Error", error)
        return jsonify({"message": "Internal server error"}), 500


@app.route("/books/form", methods=["GET", "POST"])
def addFormBook():
    response = get_authors()
    autores = []
    if isinstance(response, Response):
        if response.json:
            autores = response.json["authors"]
        else:
            autores = []
    return render_template("form-book.html", autores=autores)


@app.route("/books", methods=["POST"])
def add_book():
    try:
        content_type = request.headers.get("Content-Type")

        if content_type:
            if (
                "multipart/form-data" in content_type
                or "application/x-www-form-urlencoded" in content_type
            ):
                isbn = request.form.get("isbn")
                name = request.form.get("name")
                cant_pages = request.form.get("cant_pages")
                author_id = request.form.get("author_id")
            elif "application/json" in content_type:
                data = request.json

                if data is not None:
                    isbn = data.get("isbn")
                    name = data.get("name")
                    cant_pages = data.get("cant_pages")
                    author_id = data.get("author_id")
            else:
                return "Tipo de conteúdo desconhecido", 400

        if not name or not cant_pages or not author_id or not isbn:
            return (
                jsonify({"message": "Bad request, all fields must be filled"}),
                400,
            )
        new_book = Book(
            isbn=isbn, name=name, cant_pages=cant_pages, author_id=author_id
        )
        db.session.add(new_book)
        db.session.commit()

        if content_type:
            if (
                "multipart/form-data" in content_type
                or "application/x-www-form-urlencoded" in content_type
            ):
                response = get_books()
                if isinstance(response, Response):
                    if response.json:
                        books = response.json["books"]
                    else:
                        books = []
                else:
                    print("Response: ", response)
                    books = []

                return render_template("list-book.html", livros=books)

        return (
            jsonify(
                {
                    "book": {
                        "id": new_book.id,
                        "isbn": new_book.isbn,
                        "name": new_book.name,
                        "cant_pages": new_book.cant_pages,
                    }
                }
            ),
            201,
        )
    except Exception as error:
        print("Error", error)
        return jsonify({"message": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)
