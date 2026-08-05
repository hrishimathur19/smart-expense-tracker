from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "smart_expense_tracker_secret"

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("expense.db")
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM users
        WHERE username=? AND password=?
        """, (username, password))

        user = cursor.fetchone()

        conn.close()

        if user:

            session["user_id"] = user[0]
            session["username"] = user[2]

            return redirect("/dashboard")

        else:
            return "Invalid Username or Password!"

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match!"

        conn = sqlite3.connect("expense.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO users(name, username, email, password)
        VALUES (?, ?, ?, ?)
        """, (name, username, email, password))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT SUM(amount)
    FROM expenses
    WHERE user_id = ?
    """, (session["user_id"],))
    total = cursor.fetchone()[0]

    cursor.execute("""
    SELECT SUM(amount)
    FROM expenses
    WHERE user_id = ?
    AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
    """, (session["user_id"],))
    monthly = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM expenses
    WHERE user_id = ?
    """, (session["user_id"],))
    transaction_count = cursor.fetchone()[0]

    cursor.execute("""
    SELECT id, category, amount, date, description
    FROM expenses
    WHERE user_id = ?
    ORDER BY date DESC
    LIMIT 5
    """, (session["user_id"],))
    recent_expenses = cursor.fetchall()

    if total is None:
        total = 0

    if monthly is None:
        monthly = 0

    cursor.execute("""  
    SELECT COUNT(*)
    FROM expenses
    WHERE user_id = ?
    """, (session["user_id"],))

    transaction_count = cursor.fetchone()[0]
    cursor.execute("""
SELECT amount
FROM budget
WHERE user_id = ?
""", (session["user_id"],))

    budget = cursor.fetchone()

    if budget:
        budget = budget[0]
    else:
        budget = 0

    budget_left = budget - total

    cursor.execute("""
SELECT id, category, amount, date, description
FROM expenses
WHERE user_id = ?
ORDER BY date DESC
LIMIT 5
""", (session["user_id"],))

    recent_expenses = cursor.fetchall()

    cursor.execute("""
    SELECT amount
FROM budget
WHERE user_id = ?
""", (session["user_id"],))

    budget = cursor.fetchone()

    if budget:
        budget = budget[0]
    else:
        budget = 0

    budget_left = budget - total

    conn.close()

    return render_template(
    "dashboard.html",
    total=total,
    monthly=monthly,
    budget=budget,
    budget_left=budget_left,
    transaction_count=transaction_count,
    recent_expenses=recent_expenses
)   
@app.route("/add-expense", methods=["GET", "POST"])
def add_expense():

    if "user_id" not in session:
        return redirect("/")

    if request.method == "POST":

        category = request.form["category"]
        amount = request.form["amount"]
        date = request.form["date"]
        description = request.form["description"]

        user_id = session["user_id"]

        conn = sqlite3.connect("expense.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO expenses(user_id, category, amount, date, description)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, category, amount, date, description))

        conn.commit()
        conn.close()

        return redirect(url_for("view_expense"))

    return render_template("add_expense.html")

@app.route("/view-expense")
def view_expense():
    if "user_id" not in session:
        return redirect("/")

    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    user_id = session["user_id"]

    cursor.execute("""
    SELECT * FROM expenses
    WHERE user_id = ?
    ORDER BY date DESC
    """, (user_id,))
    expenses = cursor.fetchall()

    conn.close()

    return render_template("view_expense.html", expenses=expenses)

@app.route("/delete/<int:id>")
def delete(id):

    if "user_id" not in session:
        return redirect("/")

    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM expenses
    WHERE id = ? AND user_id = ?
    """, (id, session["user_id"]))

    conn.commit()
    conn.close()

    return redirect(url_for("view_expense"))

@app.route("/edit/<int:id>")
def edit(id):

    if "user_id" not in session:
        return redirect("/")

    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM expenses
        WHERE id = ?
        AND user_id = ?
    """, (id, session["user_id"]))

    expense = cursor.fetchone()

    conn.close()

    if expense is None:
        return "Expense Not found or access denied"

    return render_template("edit_expense.html", expense=expense)

@app.route("/update/<int:id>", methods=["POST"])
def update(id):

    category = request.form["category"]
    amount = request.form["amount"]
    date = request.form["date"]
    description = request.form["description"]

    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE expenses
        SET category=?, amount=?, date=?, description=?
        WHERE id=? AND user_id=?
    """, (category, amount, date, description, id, session["user_id"]))

    conn.commit()
    conn.close()

    return redirect("/view-expense") 

@app.route("/set-budget", methods=["GET", "POST"])
def set_budget():

    if "user_id" not in session:
        return redirect("/")

    if request.method == "POST":

        amount = request.form["amount"]

        conn = sqlite3.connect("expense.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO budget(user_id, amount)
            VALUES (?, ?)
        """, (session["user_id"], amount))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("set_budget.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/") 



if __name__ == "__main__":
    app.run(debug=True)
    