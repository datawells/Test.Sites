from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

with open('api.key') as key_file:
    MOVIE_DB_API_KEY = key_file.read()

print(MOVIE_DB_API_KEY)
MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie_collection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
db = SQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(240), unique=True, nullable=False)
    year = db.Column(db.Integer(), nullable=False)
    description = db.Column(db.String(240), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer(), nullable=True)
    review = db.Column(db.String(240), nullable=True)
    img_url = db.Column(db.String(240), nullable=False)

    def __repr__(self):
        return f'<Movie {self.title}>'

# db.create_all()

# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )

# db.session.add(new_movie)
# db.session.commit()

class MovieAddForm(FlaskForm):
    title = StringField('Movie Title')
    submit = SubmitField('Add')

class MovieUpdateForm(FlaskForm):
    rating = StringField('Enter Rating out of 10')
    review = StringField('Enter Review')
    submit = SubmitField('Done')

@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)

@app.route("/add", methods=['GET', 'POST'])
def add():
    form = MovieAddForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(MOVIE_DB_SEARCH_URL, params={"api_key": MOVIE_DB_API_KEY, "query": movie_title})
        movie_list = response.json()["results"]
        return render_template("select.html", options=movie_list)
    return render_template("add.html", form=form)

@app.route("/update", methods=['GET', 'POST'])
def update():
    form = MovieUpdateForm()
    movie_id = request.args.get('id')
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)

@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/add_selected")
def add_selected():
    movie_id = request.args.get('id')
    movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_id}"
    response = requests.get(movie_api_url, params={"api_key": MOVIE_DB_API_KEY, "language": "en-US"})
    movie_data = response.json()
    new_movie = Movie(
        title=movie_data["title"],
        year=movie_data["release_date"].split("-")[0],
        description=movie_data["overview"],
        img_url=f"{MOVIE_DB_IMAGE_URL}{movie_data['poster_path']}"
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('update', id=new_movie.id))

if __name__ == '__main__':
    app.run(debug=True)
