from flask import Flask, render_template
from post import Post
import requests
app = Flask(__name__)

post_data = requests.get("https://api.npoint.io/c9468542d038568fc8c3").json()

post_objects = []
for post in post_data:
    post_obj = Post(int(post["id"]), post["title"], post["subtitle"], post["body"], post["author"], post["date"])
    post_objects.append(post_obj)

@app.route('/')
def home():
    return render_template("index.html", all_posts=post_objects)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/posts/<int:index>')
def posts(index):
    for blog_post in post_objects:
        if blog_post.id == index:
            requested_post = blog_post
    return render_template("post.html", post=requested_post)

if __name__ == "__main__":
    app.run(debug=True)
