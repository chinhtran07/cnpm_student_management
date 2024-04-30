from flask import render_template, request, redirect, session
from studentManagement import app


@app.route('/')
def index():
    return render_template('admin/index.html')


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
