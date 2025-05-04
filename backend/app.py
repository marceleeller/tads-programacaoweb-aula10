from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
from dotenv import load_dotenv
from bcrypt import hashpw, gensalt  # Importação corrigida
import os

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração do Flask
app = Flask(__name__)
CORS(app)

# Conexão com o banco de dados MySQL
def get_db_connection():
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    return connection

# Rota para cadastrar um aluno (POST)
@app.route('/alunos', methods=['POST'])
def cadastrar_aluno():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    matricula = data.get('matricula')
    senha = data.get('senha')

    if not nome or not email or not matricula or not senha:
        return jsonify({'error': 'Todos os campos são obrigatórios!'}), 400

    senha_hash = hashpw(senha.encode('utf-8'), gensalt())  # Hash da senha

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO aluno (nome, email, matricula, senha) VALUES (%s, %s, %s, %s)',
            (nome, email, matricula, senha_hash)
        )
        conn.commit()
    except mysql.connector.Error as err:
        return jsonify({'error': f'Erro no banco de dados: {err}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return jsonify({'message': 'Aluno cadastrado com sucesso!'}), 201

# Rota para listar todos os alunos (GET)
@app.route('/alunos', methods=['GET'])
def listar_alunos():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    offset = (page - 1) * per_page

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM aluno LIMIT %s OFFSET %s', (per_page, offset))
        alunos = cursor.fetchall()
    except mysql.connector.Error as err:
        return jsonify({'error': f'Erro no banco de dados: {err}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return jsonify(alunos)

# Rota para a página inicial
@app.route('/')
def home():
    return jsonify({'message': 'Bem-vindo à API de Alunos!'})

# Rodar a aplicação
if __name__ == '__main__':
    app.run(debug=True)  # Lembre-se de desativar o debug em produção!