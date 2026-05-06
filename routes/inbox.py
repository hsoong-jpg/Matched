@app.route("/inbox")
def inbox():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    from models import get_connection
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name FROM users LIMIT 5
    """)

    matches = cursor.fetchall()
    conn.close()

    print("DEBUG MATCHES:", matches)

    return render_template("inbox.html", matches=matches)