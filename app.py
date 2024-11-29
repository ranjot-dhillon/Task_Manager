from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# Change time zone
import pytz

app = Flask(__name__)

#create connection with datbase

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.sqlite"
db = SQLAlchemy(app)


# Creating Table Todo
class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"


#complete task route

@app.route("/complete/<int:sno>")
def complete_task(sno):
    task = Todo.query.get_or_404(sno)
    task.status = 'Completed'
    db.session.commit()
    return redirect("/")


#pending task route
@app.route("/incomplete/<int:sno>")
def incomplete_task(sno):
    task = Todo.query.get_or_404(sno)
    task.status = 'Pending'
    db.session.commit()
    return redirect("/")


# Route for home

@app.route('/', methods=["GET", "POST"])
def home():
    filter_status = request.args.get('status', 'all')
    if request.method == "POST":
        user_title = request.form["title"]
        user_desc = request.form["desc"]

        ist_tz = pytz.timezone('Asia/Kolkata')
        ist_datetime = datetime.now(tz=ist_tz)
        date_format = '%d-%m-%Y %H:%M:%S'
        date_str = ist_datetime.strftime(date_format)
        date_created = datetime.strptime(date_str, date_format)
        todo = Todo(title=user_title, desc=user_desc,
                    date_created=date_created)
        db.session.add(todo)
        db.session.commit()

    try:
        if filter_status == 'pending':
            all_items = Todo.query.filter_by(status='Pending').all()
        elif filter_status == 'completed':
            all_items = Todo.query.filter_by(status='Completed').all()
        else:
            all_items = Todo.query.all()
    except Exception as e:
        print(f"Error fetching tasks: {e}")
        all_items = []
    return render_template("index.html", all_todos=all_items, filter_status=filter_status)


# Update route


@app.route("/update/<int:sno>", methods=["GET", "POST"])
def update_item(sno):
    if request.method == "POST":
        user_title = request.form["title"]
        user_desc = request.form["desc"]

        item = Todo.query.get_or_404(sno)
        item.title = user_title
        item.desc = user_desc
        db.session.add(item)
        db.session.commit()
        return redirect("/")

    item = Todo.query.get_or_404(sno)
    return render_template("update.html", todo=item)


# Delete route

@app.route('/delete/<int:sno>')
def delete_item(sno):
    item = Todo.query.get_or_404(sno)
    db.session.delete(item)
    db.session.commit()
    return redirect('/')


# Search route

@app.route('/search', methods=["GET", "POST"])
def search_item():
    # Get the search query from the URL parameter
    search_query = request.args.get('query')

    # Perform the search query

    result = Todo.query.filter(Todo.title == search_query).all()

    # Render the result

    return render_template('result.html', posts=result)


# Ensures the database schema is created
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)
