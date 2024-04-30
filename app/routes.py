from flask import render_template, jsonify, request, Response, Blueprint
from app.database import db

from .models.author import Author
from .models.book import Book
from .controllers.book_controller import *
from .controllers.author_controller import *

main = Blueprint("main", __name__)


@main.route("/")
def index():
    title = "RCS Soft - Livraria"
    return render_template("index.html", title=title)


@main.route("/authors/list")
def list_authors():
    try:
        autores = get_authors()
        if is_request_json():
            return response_json("success", "Lista de autores", autores)

        return render_template("list-author.html", autores=autores)
    except Exception as error:
        print("Error: ", error)
        message = "Lista de autores não pode ser recuperada"
        if is_request_json():
            return response_json("error", message, data=None)

        return render_template("erro.html", message=message)


@main.route("/authors/form", methods=["GET", "POST"])
def addFormAuthor():
    return render_template("form-author.html")


@main.route("/authors", methods=["POST"])
def add_author():
    try:
        content_type = request.headers.get("Content-Type")

        if content_type:
            if (
                "multipart/form-data" in content_type
                or "mainlication/x-www-form-urlencoded" in content_type
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


@main.route("/books/list")
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


@main.route("/books", methods=["GET"])
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


@main.route("/books/form", methods=["GET", "POST"])
def addFormBook():
    response = get_authors()
    autores = []
    if isinstance(response, Response):
        if response.json:
            autores = response.json["authors"]
        else:
            autores = []
    return render_template("form-book.html", autores=autores)


@main.route("/books", methods=["POST"])
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


def is_request_json():
    return request.headers.get("Content-Type") == "application/json"


def response_json(status, message, data):
    return jsonify({"status": status, "message": message, "data": data})
