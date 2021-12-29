import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


app = Flask(__name__)
app.config['SECRET_KEY'] = "test"

@app.route("/")
def index():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

@app.route('/<int:task_id>')
def task(task_id):
    task = get_task(task_id)
    return render_template('task.html', task=task)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        assignee = request.form['assignee']
        state = request.form['state']
        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content, assignee, state) VALUES (?,?,?,?)',
                         (title, content, assignee, state))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/<int:task_id>/edit', methods=('GET', 'POST'))
def edit(task_id):
    task = get_task(task_id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        assignee = request.form['assignee']
        state = request.form['state']
        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?, assignee = ?, state = ?'
                         ' WHERE id = ?',
                         (title, content, assignee, state, task_id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', task=task)

@app.route('/<int:task_id>/delete', methods=['POST'])
def delete(task_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    flash('The task has been successfully deleted!')
    return redirect(url_for('index'))

def get_task(task_id):
    conn = get_db_connection()
    task = conn.execute('SELECT * from posts where id = ?', (task_id,)).fetchone()

    conn.close()
    if task is None:
        abort(404)

    return task

if __name__ == "__main__":
    app.run()