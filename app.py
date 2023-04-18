# Lucas Bubner, 2023
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            raise Exception("Error")
        except Exception as e:
            return redirect(url_for("index.html", error=e, **request.args))
    else:
        return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)