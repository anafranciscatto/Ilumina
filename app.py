from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'chave_secreta_segura'

# Configuração do banco de dados
conn = mysql.connector.connect(
    host='localhost',
    user='root',  
    password='root',  
    database='lumina_db'
)
cursor = conn.cursor()

# Rota para a página inicial (index)
@app.route('/')
def index():
    # Verifica se o usuário está logado
    if 'user_id' in session:
        return redirect(url_for('dashboard'))  # Redireciona para o dashboard caso o usuário esteja logado
    return render_template('index.html')  # Exibe a página inicial com links para login e cadastro

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('entrar'))  # Se não estiver logado, redireciona para login

    user_nome = session.get('user_nome', 'Usuário')

    # Buscando dados no banco de dados
    cursor.execute("SELECT COUNT(*) FROM eventos WHERE status = 'pendente'")
    eventos_pendentes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM eventos WHERE status = 'confirmado'")
    eventos_confirmados = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM participantes")
    total_participantes = cursor.fetchone()[0]

    # Buscando os 5 eventos mais recentes para exibição
    cursor.execute("""
        SELECT nome, data_evento, status 
        FROM eventos 
        ORDER BY data_evento DESC 
        LIMIT 5
    """)
    eventos_recentes = cursor.fetchall()

    return render_template('adm-dashboard.html', 
                           user_nome=user_nome,
                           eventos_pendentes=eventos_pendentes,
                           eventos_confirmados=eventos_confirmados,
                           total_participantes=total_participantes,
                           eventos_recentes=eventos_recentes)


# Rota para a página de login
@app.route('/entrar', methods=['GET', 'POST'])
def entrar():
    if request.method == 'POST':
        cpf = request.form['cpf']
        senha = request.form['senha']
        
        # Consultar o banco de dados para verificar as credenciais
        cursor.execute("""
            SELECT id_usuario, nome FROM usuarios
            WHERE cpf = %s AND senha = %s
        """, (cpf, senha))

        user = cursor.fetchone()

        if user:
            session['user_id'] = user[0]
            session['user_nome'] = user[1]
            return redirect(url_for('dashboard'))  # Redireciona para o dashboard após login bem-sucedido
        else:
            return "CPF ou senha incorretos. Tente novamente."

    return render_template('login.html')

# Rota para a página de cadastro
@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        cpf = request.form['cpf']
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        # Verificar se o CPF ou e-mail já existe no banco
        cursor.execute("SELECT * FROM usuarios WHERE cpf = %s OR email = %s", (cpf, email))
        usuario_existente = cursor.fetchone()

        if usuario_existente:
            return "CPF ou e-mail já cadastrado. Tente novamente com outro."

        try:
            # Inserir o novo usuário no banco de dados
            cursor.execute("""
                INSERT INTO usuarios (cpf, nome, email, senha, tipo)
                VALUES (%s, %s, %s, %s, %s)
            """, (cpf, nome, email, senha, 'funcionario'))  # tipo é 'funcionario' por padrão
            conn.commit()  # Salvar no banco de dados

            return redirect(url_for('entrar'))  # Redirecionar para a página de login após o cadastro

        except mysql.connector.Error as err:
            return f"Erro ao cadastrar: {err}"

    return render_template('cadastro.html')  # Renderizar o formulário de cadastro

# Rota para logout
@app.route('/sair')
def sair():
    session.pop('user_id', None)
    session.pop('user_nome', None)
    return redirect(url_for('entrar'))  # Redireciona para o login após logout

if __name__ == '__main__':
    app.run(debug=True)
