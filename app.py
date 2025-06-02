from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)
DB_NAME = "database.db"

def init_db():
    # Inicializa o banco de dados criando a tabela 'produtos' se ela não existir.
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
    CREATE TABLE produtos (
        id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL,
        quantidade INTEGER,
        preco REAL
    )
''')
        conn.commit()
        conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    # Rota principal que exibe os produtos e permite adicionar novos.
    if request.method == 'POST':
        nome = request.form['nome']
        quantidade = request.form['quantidade']
        preco = request.form['preco']
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO produtos (nome, quantidade, preco) VALUES (?, ?, ?)", (nome, quantidade, preco))
        conn.commit()
        conn.close()
        return redirect('/')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    conn.close()
    return render_template("index.html", produtos=produtos)

@app.route('/edit/<int:produto_id>', methods=['GET', 'POST'])
def edit(produto_id):
    # Rota para edição de um produto existente.
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if request.method == 'POST':
        nome = request.form['nome']
        quantidade = request.form['quantidade']
        preco = request.form['preco']
        cursor.execute("UPDATE produtos SET nome = ?, quantidade = ?, preco = ? WHERE id = ?", (nome, quantidade, preco, produto_id))
        conn.commit()
        conn.close()
        return redirect('/')
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
    produto = cursor.fetchone()
    conn.close()
    return render_template("edit_produto.html", produto=produto)

@app.route('/delete/<int:produto_id>')
def delete(produto_id):
    # Rota para deletar um produto.
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    conn.commit()

    # Reorganizar IDs
    cursor.execute("SELECT * FROM produtos ORDER BY id")
    produtos = cursor.fetchall()
    cursor.execute("DELETE FROM produtos")
    for index, produto in enumerate(produtos, start=1):
        cursor.execute(
            "INSERT INTO produtos (id, nome, quantidade, preco) VALUES (?, ?, ?, ?)",
            (index, produto[1], produto[2], produto[3])
        )
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
