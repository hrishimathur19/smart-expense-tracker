from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0]
    return render_template("dashboard.html", total=total)

@app.route("/add-expense", methods=["GET", "POST"])
def add_expense():

    if request.method == "POST":

        category = request.form["category"]
        amount = request.form["amount"]
        date = request.form["date"]
        description = request.form["description"]

        conn = sqlite3.connect("expense.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO expenses(category, amount, date, description)
        VALUES (?, ?, ?, ?)
        """, (category, amount, date, description))

        conn.commit()
        conn.close()

        return redirect(url_for("view_expense"))

    return render_template("add_expense.html")

@app.route("/view-expense")
def view_expense():

    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()

    conn.close()

    return render_template("view_expense.html", expenses=expenses)

@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM expenses WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect(url_for("view_expense"))

if __name__ == "__main__":
    app.run(debug=True)
    