import psycopg2
from psycopg2 import sql, Error
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from os import getenv

app = Flask(__name__)
load_dotenv()

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=getenv("DB_NAME"),
            user=getenv("USER"),
            password=getenv("PSSWD"),
            host=getenv("HOST"),
            port=getenv("PORT")
        )
        return conn
    except Error as e:
        print(f"Error connecting to the database: {e}")
        return None

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota para obter candidatos eleitos
@app.route('/candidaturas/eleitos', methods=['GET'])
def get_eleitos():
    query = """
    SELECT Candidatura.*, Individuo.Nome AS Nome, Partido.Nome AS Partido, Cargo.Localidade, Vice.Cod_Candidato AS Vice_Candidato
    FROM Candidatura
        JOIN Individuo ON Candidatura.Cod_Candidato = Individuo.CPF
        JOIN Partido ON Candidatura.Cod_Partido = Partido.Cod_Partido
        JOIN Cargo ON Candidatura.Cod_Cargo = Cargo.Cod_Cargo
        LEFT JOIN Candidatura AS Vice ON Candidatura.Cod_Candidatura_Vice = Vice.Cod_Candidatura
    WHERE Candidatura.Eleito = TRUE
    """

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    candidaturas = cursor.fetchall()
    cursor.close()
    conn.close()

    result = []
    for candidatura in candidaturas:
        result.append({
            'Cod_Candidatura': candidatura[0],
            'Cod_Candidato': candidatura[1],
            'Cod_Cargo': candidatura[2],
            'Ano': candidatura[3],
            'Cod_Pleito': candidatura[4],
            'Cod_Candidatura_Vice': candidatura[5],
            'Eleito': candidatura[6],
            'Partido': candidatura[7],
            'Localidade': candidatura[8],
            'Vice_Candidato': candidatura[9]
        })
    return render_template('eleitos.html', candidaturas=result)

@app.route('/candidaturas', methods=['GET'])
def list_candidaturas():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        ano = request.args.get('ano')
        nome_candidato = request.args.get('nome_candidato')
        cargo = request.args.get('cargo')
        order_by = request.args.get('order_by', 'Ano')
        order_dir = request.args.get('order_dir', 'ASC')

        query = """
        SELECT Candidatura.*, Individuo.Nome AS Nome_Candidato, Partido.Nome AS Partido, Cargo.Localidade, Total_doacoes AS totDoacoes
        FROM Candidatura 
        JOIN Individuo ON Candidatura.Cod_Candidato = Individuo.CPF 
        JOIN Partido ON Candidatura.Cod_Partido = Partido.Cod_Partido 
        JOIN Cargo ON Candidatura.Cod_Cargo = Cargo.Cod_Cargo
        """
        filters = []
        params = []

        if ano:
            filters.append("Candidatura.Ano = %s")
            params.append(ano)
        if nome_candidato:
            filters.append("Individuo.Nome LIKE %s")
            params.append(f"%{nome_candidato}%")
        if cargo:
            filters.append("Cargo.cod_cargo = %s")
            params.append(cargo)

        if filters:
            query += " WHERE " + " AND ".join(filters)

        query += f" ORDER BY {order_by} {order_dir}"

        cursor.execute(query, tuple(params))
        candidaturas = cursor.fetchall()

        cursor.close()
        conn.close()

        result = []
        for candidatura in candidaturas:
            print(candidatura)
            result.append({
                'Cod_Candidatura': candidatura[0],
                'Cod_Candidato': candidatura[1],
                'Cod_Cargo': candidatura[2],
                'Ano': candidatura[4],
                'Cod_Pleito': candidatura[5],
                'Cod_Candidatura_Vice': candidatura[6] ,
                'Eleito': candidatura[7],
                'Nome_Candidato': candidatura[9],
                'Partido': candidatura[3],
                'Localidade': candidatura[9],
                'total_doacoes': candidatura[8]
            })

        return render_template('candidaturas.html', candidaturas=result)

    except Error as e:
        return jsonify({'error': str(e)}), 500

# Rota para obter candidatos com ficha limpa
@app.route('/candidatos/ficha-limpa', methods=['GET'])
def get_ficha_limpa():
    query = "SELECT * FROM Individuo WHERE Ficha_Limpa = TRUE"
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(query)
        candidatos = cursor.fetchall()
        cursor.close()
        conn.close()
    except Error as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500

    result = []
    for candidato in candidatos:
        result.append({
            'CPF': candidato[0],
            'Nome': candidato[1],
            'Ficha_Limpa': candidato[2]
        })
    return render_template('ficha_limpa.html', candidatos=result)

@app.route('/delete', methods=['GET', 'POST'])
def delete_entity():
    if request.method == 'POST':
        entity = request.form['entity'].lower()
        id = request.form['id']

        table_mapping = {
            'pleito': 'Pleito',
            'candidatura': 'Candidatura',
            'cargo': 'Cargo',
            'individuo': 'Individuo',
            'equipeapoio': 'EquipeApoio',
            'doadoresf': 'DoacaoPF',
            'doadoresj': 'DoadorPJ',
            'processojudicial': 'ProcessoJudicial',
            'empresa': 'empresa'
        }

        id_column_mapping = {
            'pleito': 'Cod_Pleito',
            'candidatura': 'Cod_Candidatura',
            'individuo': 'CPF',
            'cargo': 'Cod_Cargo',
            'equipeapoio': 'Cod_Equipe',
            'doadoresf': 'Cod_Nota',
            'doadoresj': 'Cod_Candidatura',
            'processojudicial': 'Cod_Processo',
            'empresa': 'cnpj'
        }

        table = table_mapping.get(entity)
        id_column = id_column_mapping.get(entity)

        if table and id_column:
            if entity == 'individuo' and (len(id) != 14):
                message = "CPF inválido ou não encontrado!"
                return render_template('delete.html', message=message)
            elif entity == 'empresa' and (len(id) != 18):
                message = "CNPJ inválido ou não encontrado!"
                return render_template('delete.html', message=message)
                
            query = f"DELETE FROM {table} WHERE {id_column} = %s"

            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(query, (id,))
                
                if cursor.rowcount == 0:
                    message = f"Nenhum registro encontrado para {entity} com ID {id}."
                else:
                    conn.commit()
                    message = f"{entity.capitalize()} com ID {id} removido com sucesso."
            except Exception as e:
                conn.rollback()
                message = f"Erro ao remover {entity}: {e}"
            finally:
                cursor.close()
                conn.close()
        else:
            message = "Entidade ou coluna de ID inválida."

        return render_template('delete.html', message=message)

    return render_template('delete.html')

@app.route('/inserir', methods=['GET', 'POST'])
def inserir():
    if request.method == 'POST':
        entity = request.form['entity']
        conn = get_db_connection()
        cursor = conn.cursor()
        message = "Dados inseridos com sucesso!"
        
        try:
            if entity == 'pleito':
                cod_pleito = request.form['Cod_Pleito']
                qtd_votos = request.form['qtdVotos']
                query = "INSERT INTO Pleito (Cod_Pleito, Qtd_Votos) VALUES (%s, %s)"
                cursor.execute(query, (cod_pleito, qtd_votos))

            elif entity == 'partido':
                cod_partido = request.form['cod_partido']
                nome = request.form['nome']
                cod_programa = request.form['cod_programa']
                query = "INSERT INTO Partido (Cod_Partido, Nome, Cod_Programa) VALUES (%s, %s, %s)"
                cursor.execute(query, (cod_partido, nome, cod_programa))
            
            elif entity == 'programaPartido':
                cod_programa = request.form['cod_programaPartido']
                descricao = request.form['programa']

                query = "INSERT INTO ProgramaPartido (Cod_Programa, Descricao) VALUES (%s, %s)"
                cursor.execute(query, (cod_programa, descricao))

            
            elif entity == 'candidatura':
                codigo_candidatura = request.form['cod_candidatura']
                codigo_candidato = request.form['cod_individuo']
                codigo_cargo = request.form['cod_cargo']
                cod_partido = request.form['cod_Partido']
                ano = request.form['ano']
                cod_pleito = request.form['pleito']
                cod_candidatura_vice = request.form['cod_candidatura_vice']
                eleito = request.form['eleito']
                eleito = True if eleito == 'SIM' else False
                total_doacoes = request.form['total_doacoes']
                
                if not cod_candidatura_vice:
                    cod_candidatura_vice = None
                
                if not total_doacoes:  
                    total_doacoes = 0

                # Verificação 1: se o candidato já se candidatou para o mesmo cargo no mesmo ano
                query_check_same_cargo = """
                    SELECT 1 FROM Candidatura 
                    WHERE Cod_Candidato = %s 
                    AND Ano = %s 
                    AND Cod_Cargo = %s
                """
                cursor.execute(query_check_same_cargo, (codigo_candidato, ano, codigo_cargo))
                if cursor.fetchone():
                    raise Exception('Candidato já se candidatou para o mesmo cargo no mesmo ano.')

                # Verificação 2: se o candidato já se candidatou para outro cargo no mesmo ano
                query_check_other_cargo = """
                    SELECT 1 FROM Candidatura 
                    WHERE Cod_Candidato = %s 
                    AND Ano = %s 
                    AND Cod_Cargo <> %s
                """
                cursor.execute(query_check_other_cargo, (codigo_candidato, ano, codigo_cargo))
                if cursor.fetchone():
                    raise Exception('Candidato já se candidatou para outro cargo no mesmo ano.')


                query = """
                    INSERT INTO Candidatura 
                    (Cod_Candidatura, Cod_Candidato, Cod_Cargo, Cod_Partido, Ano, Cod_Pleito, Cod_Candidatura_Vice, Eleito, Total_Doacoes) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (codigo_candidatura, codigo_candidato, codigo_cargo, cod_partido, ano, cod_pleito, cod_candidatura_vice, eleito, total_doacoes))
            
            elif entity == 'individuo':
                cpf = request.form['cpf']
                nome = request.form['nome_ind']
                ficha_limpa = request.form.get('ficha_limpa', 'FALSE')
                cod_equipe = request.form['partido']

                if not cod_equipe:
                    cod_equipe = None

                query = "INSERT INTO Individuo (CPF, Nome, Ficha_Limpa, Cod_Equipe) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (cpf, nome, ficha_limpa, cod_equipe))
            
            elif  entity == 'cargo':
                codigo_cargo = request.form['cod_Cargo']
                descricao = request.form['descricao']
                localidade = request.form['localidade']
                qtd_eleitos = request.form['qtd_Eleitos']
                pais = request.form['pais']
                estado = request.form.get('estado', None)
                cidade = request.form.get('cidade', None)
                
                query = """
                    INSERT INTO Cargo (Cod_Cargo, Descricao, Localidade, Qtd_Eleitos, Pais, Estado, Cidade) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (codigo_cargo, descricao, localidade, qtd_eleitos, pais, estado, cidade))
                    
            elif entity == 'equipeapoio':
                cod_equipe = request.form['cod_equipe']
                nome_equipe = request.form['nomeEquipe']
                query = "INSERT INTO EquipeApoio (Cod_Equipe, Nome) VALUES (%s, %s)"
                cursor.execute(query, (cod_equipe, nome_equipe))

            elif entity == 'empresa':
                cnpj = request.form['cnpj']
                nome = request.form['nomeEmpresa']
                query = "INSERT INTO Empresa (CNPJ, Nome) VALUES (%s, %s)"
                cursor.execute(query, (cnpj, nome))

            elif entity == 'processojudicial':
                codigo_processo = request.form['codigo_processo']
                codigo_individuo = request.form['codigo_individuo']
                data_inicio = request.form['data_Inicio']
                julgado = request.form.get('julgado', 'FALSE')
                data_termino = request.form['data_termino'] if 'data_termino' in request.form else None
                procedente = request.form.get('procedente', 'FALSE')
                
                query = """
                    INSERT INTO ProcessoJudicial 
                    (Cod_Processo, Cod_Individuo, Data_Inicio, Julgado, Data_Termino, Procedente) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (codigo_processo, codigo_individuo, data_inicio, julgado, data_termino, procedente))

            conn.commit()
        
        except (Exception, psycopg2.Error) as error:
            conn.rollback()
            message = f"Houve um problema com os inputs: inputs inválidos!"
            print(error)
        
        finally:
            cursor.close()
            conn.close()

        return render_template('inserir.html', message=message)
    
    return render_template('inserir.html')

@app.route('/doacoes', methods=['GET', 'POST'])
def doacoes():
    message = ""
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        doador_tipo = request.form['doador_tipo']
        
        try:
            if doador_tipo == "Físico":
                nf_doacao = request.form['nota_doacao']
                cod_doador = request.form['cod_doador_pf']
                valor = request.form['valor_pf']
                data_doacao = request.form['data_doacao_pf']
                query_check = "SELECT 1 FROM DoacaoPF WHERE Cod_Nota = %s"
                cursor.execute(query_check, (nf_doacao,))
                exists = cursor.fetchone()
                
                if exists:
                    query_update_candidatura = """
                        UPDATE Candidatura
                        SET Total_Doacoes = Total_Doacoes + %s
                        WHERE Cod_Candidatura = (
                            SELECT Cod_Candidatura FROM Candidatura WHERE Cod_Candidato = %s
                        )
                    """
                    cursor.execute(query_update_candidatura, (valor, cod_doador))
                else:
                    query_update_candidatura = """
                        UPDATE Candidatura
                        SET Total_Doacoes = Total_Doacoes + %s
                        WHERE Cod_Candidatura = (
                            SELECT Cod_Candidatura FROM Candidatura WHERE Cod_Candidato = %s
                        )
                    """
                    cursor.execute(query_update_candidatura, (valor, cod_doador))

                    query_insert_doacaopf = """
                        INSERT INTO DoacaoPF (Cod_Nota, Cod_Individuo, Valor, data_doacao)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(query_insert_doacaopf, (nf_doacao, cod_doador, valor, data_doacao))
                
                conn.commit()
                message = "Dados inseridos com sucesso!"
            elif doador_tipo == "Jurídico":
                cod_doador = request.form['cod_doador_pj']
                cod_candidatura = request.form['cod_candidatura_pj']
                valor = request.form['valor_pj']
                data_doacao = request.form['data_doacao_pj']
                query = "INSERT INTO DoadorPJ (Cod_Empresa, Cod_Candidatura, Valor, data_doacao) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (cod_doador, cod_candidatura, valor, data_doacao))
                conn.commit()
                message = "Dados inseridos com sucesso!"
            else:
                raise ValueError("Tipo de doador inválido.")
        
        except Exception as e:
            conn.rollback()
            message = f"Erro ao registrar doação"
            print(e)
        
        finally:
            cursor.close()
            conn.close()
    
        return render_template('doacoes.html', message=message)

    return render_template('doacoes.html')

if __name__ == '__main__':
    app.run(debug=True)

