from flask import Flask, render_template, request, redirect, jsonify, session, url_for
import sqlite3
import uuid

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta' 

def create_table():
    with sqlite3.connect('codes.db') as conn:
        c = conn.cursor()
        try:
            c.execute('''CREATE TABLE IF NOT EXISTS codes (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         code TEXT NOT NULL
                         )''')
        except sqlite3.Error as e:
            print(f"Error de SQLite: {e}")

create_table()

def generate_code():
    code = '-'.join(str(uuid.uuid4().int)[:4] for _ in range(4))
    return code

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/generate_code', methods=['GET', 'POST'])
def generate_code_route():
    new_code = generate_code()
    with sqlite3.connect('codes.db') as conn:
        c = conn.cursor()
        try:
            c.execute("INSERT INTO codes (code) VALUES (?)", (new_code,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error de SQLite: {e}")
    
    session['new_code'] = new_code

    return redirect(url_for('index'))
@app.route('/clear_new_code', methods=['POST'])
def clear_new_code():
    session.pop('new_code', None)
    return redirect(url_for('index'))

@app.route('/clear_new_code_session', methods=['POST'])
def clear_new_code_session():
    session.clear()
    return jsonify({'success': True})

@app.route('/codes', methods=['GET', 'POST'])
def get_all_codes():
    with sqlite3.connect('codes.db') as conn:
        c = conn.cursor()
        try:
            c.execute("SELECT * FROM codes")
            codes = c.fetchall()
        except sqlite3.Error as e:
            print(f"Error de SQLite: {e}")
            codes = []

    return render_template('all_codes.html', codes=codes)

@app.route('/check_code', methods=['POST'])
@app.route('/check_code', methods=['POST'])
def check_code():
    group1 = request.form['group1']
    group2 = request.form['group2']
    group3 = request.form['group3']
    group4 = request.form['group4']

    input_code = f"{group1}-{group2}-{group3}-{group4}"

    with sqlite3.connect('codes.db') as conn:
        c = conn.cursor()
        try:
            c.execute("SELECT * FROM codes WHERE code=?", (input_code,))
            result = c.fetchone()
        except sqlite3.Error as e:
            print(f"Error de SQLite: {e}")
            result = None

    if result:
        message = f"El código {input_code} existe en la base de datos."
    else:
        message = f"El código {input_code} no existe en la base de datos."

    return render_template('check_code.html', message=message)


if __name__ == '__main__':
    app.run(debug=True)
