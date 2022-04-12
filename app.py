from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def homepage():
    """Takes the login status.
    Renders the homepage.
    Homepage looks differently, depending on the login status:
    - logged in: calendar view for the current user and search
    - logged out: search/call to action"""
    return render_template('/home.html')


@app.route("/search/<user_input>")
def search(user_input):
    """Takes the user input.
    Renders the result of search:
    - found meal/product that has the most fitting name
    - found table of replacements for that meal (sortable)
    - if meal not found: prompt to add"""
    return f"Searches the replacement for '{user_input}'"


@app.route("/contact")
def contact():
    """Returns simple contact page."""
    return "Contact info"


@app.route("/settings")
def settings():
    """Takes user's ID.
    Returns customizable user settings:
    - language
    - diet
    - password change (*)"""
    return "Settings"


@app.route("/day/<date>")
def day(date):
    """Takes user's ID and date.
    Renders customizable diet for the current date."""
    return f"Diet for {date}"


if __name__ == "__main__":
    app.run(debug=True)
