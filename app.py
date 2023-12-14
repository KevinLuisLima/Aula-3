from flask import Flask, jsonify, request
from sqlalchemy import create_engine, text

app = Flask(__name__)
engine = create_engine('postgresql://user:senha@localhost:5432/nome_do_banco')


# Operação READ - Listar todos os alunos
@app.route('/disciplinas', methods=['GET'])
def listarDisciplina():
    with engine.connect() as conn:
        query = text('SELECT * FROM disciplina;')
        response = conn.execute(query)

        # Obter os nomes das colunas
        column_names = response.keys()

        # Coletar os resultados em uma lista de dicionários
        disciplinas = [dict(zip(column_names, row)) for row in response]

    return jsonify(disciplinas)


# Operação READ - Obter detalhes de um aluno específico
@app.route('/disciplinas/<int:disciplina_id>', methods=['GET'])
def obterDisciplina(disciplina_id):
    with engine.connect() as conn:
        query = text('SELECT * FROM disciplina WHERE id = :disciplina_id;')
        response = conn.execute(query, {'disciplina_id': disciplina_id})
        disciplina = response.fetchone()

        if disciplina:
            column_names = response.keys()
            disciplina_dict = dict(zip(column_names, disciplina))
            return jsonify(disciplina_dict)
        else:
            return jsonify({'message': 'Disciplina não encontrado'}), 404


# Operação CREATE - Adicionar um novo aluno
@app.route('/disciplinas', methods=['POST'])
def adicionarDisciplina():
    nova_disciplina = request.get_json()

    query = text('INSERT INTO disciplina (tipo, nome, credito, codigo, carga_horaria) '
                 'VALUES (:tipo, :nome, :credito, :codigo, :carga_horaria) RETURNING *;')

    with engine.connect() as conn:
        response = conn.execute(query, {'tipo': nova_disciplina.get('tipo'), 'nome': nova_disciplina.get('nome'),
                                        'credito': nova_disciplina.get('credito'),
                                        'codigo': nova_disciplina.get('codigo'),
                                        'carga_horaria': nova_disciplina.get('carga_horaria')})
        nova_disciplina_inserida = response.fetchone()

        # Commit da transação
        conn.commit()

    column_names = response.keys()
    disciplina_dict = dict(zip(column_names, nova_disciplina_inserida))

    return jsonify(disciplina_dict), 201


# Operação UPDATE - Atualizar informações de um aluno
@app.route('/disciplinas/<int:disciplina_id>', methods=['PUT'])
def atualizarDisciplina(disciplina_id):
    disciplina_atualizada = request.get_json()

    query = text('UPDATE disciplina SET tipo = :tipo, nome = :nome, credito = :credito, '
                 'carga_horaria = :carga_horaria WHERE id = :disciplina_id RETURNING *;')

    with engine.connect() as conn:
        response = conn.execute(query, {'tipo': disciplina_atualizada.get('tipo'), 'nome': disciplina_atualizada.get('nome'),
                                        'credito': disciplina_atualizada.get('credito'),
                                        'codigo': disciplina_atualizada.get('codigo'),
                                        'carga_horaria': disciplina_atualizada.get('carga_horaria'),
                                        'disciplina_id': disciplina_id})

        disciplina_atualizada = response.fetchone()

        # Commit da transação
        conn.commit()

    if disciplina_atualizada:
        column_names = response.keys()
        disciplina_dict = dict(zip(column_names, disciplina_atualizada))
        return jsonify(disciplina_dict)
    else:
        return jsonify({'message': 'Aluno não encontrado'}), 404


# Operação DELETE - Remover um aluno
@app.route('/disciplinas/<int:disciplina_id>', methods=['DELETE'])
def removerDisciplina(disciplina_id):
    query = text('DELETE FROM disciplina WHERE id = :disciplina_id RETURNING *;')
    with engine.connect() as conn:
        response = conn.execute(query, {'disciplina_id': disciplina_id})

        disciplina_removida = response.fetchone()

        # Commit da transação
        conn.commit()

    if disciplina_removida:
        column_names = response.keys()
        disciplina_dict = dict(zip(column_names, disciplina_removida))
        return jsonify(disciplina_dict)
    else:
        return jsonify({'message': 'Aluno não encontrado'}), 404


if __name__ == '__main__':
    app.run(debug=True)