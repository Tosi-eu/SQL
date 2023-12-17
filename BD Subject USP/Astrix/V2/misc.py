import psycopg2
from prettytable import PrettyTable
from dotenv import load_dotenv
from os import getenv

tabela = PrettyTable()

#conectar ao banco de dados 
def conectar():
    try:
        load_dotenv()
        connection = psycopg2.connect(
            user=getenv("USER"),
            password=getenv("PSWD"),
            host=getenv("HOST"),
            port=getenv("PORT"),
            database=getenv("DB")
        )
        return connection
    except psycopg2.Error as psy:
        print(f"Erro ao conectar ao banco de dados: {psy}")
        return None
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def check_null(cursor, table_name):
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        if count == 0:
            return True
        return False

def viagem_existe(cursor, origem, destino, ccf):
        try:
            if cosmonauta_fisico_existe(cursor, ccf):
                cursor.execute("SELECT * FROM viagem WHERE origem = %s AND destino = %s", (origem,destino,))
                return True
            else:
                print("CF não existe!")
        except Exception as e:
            print(f"Erro ao verificar a existência da viagem: {e}")
            return False
        return False

def piloto_existe(cursor, ccp):
    try:
        cursor.execute("SELECT COUNT(*) FROM piloto WHERE cp = %s", (ccp,))
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        print(f"Erro ao verificar a existência do Piloto: {e}")
        return False

def planeta_existe(cursor, nome):
    try:
        cursor.execute("SELECT COUNT(*) FROM PLANETA WHERE NOME = %s", (nome,))
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        print(f"Erro ao verificar a existência do Planeta: {e}")
        return False

def empregado_existe(cursor, cf):
    try:
        cursor.execute("SELECT COUNT(*) FROM empregado WHERE cf = %s", (cf,))
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        print(f"Erro ao verificar a existência do Empregado: {e}")
        return False

def nave_existe(cursor, n_serie):
    try:
        cursor.execute("SELECT COUNT(*) FROM ESPACONAVE WHERE nro_serie = %s", (n_serie,))
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        print(f"Erro ao verificar a existência da Espaçonave: {e}")
        return False
            

def cosmonauta_fisico_existe(cursor, cf_codigo):
    try:
        cursor.execute("SELECT COUNT(*) FROM c_fisico WHERE ccf = %s", (cf_codigo,))
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        print(f"Erro ao verificar a existência do CF: {e}")
        return False

def administrador_existe(cursor, cf_admin):
    try:
        cursor.execute("SELECT COUNT(*) FROM Administrador WHERE CF = %s", (cf_admin,))
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        print(f"Erro ao verificar a existência do administrador: {e}")
        return False
    
def cosmonauta_juridico_existe(cursor, cj):
    try:
        cursor.execute("SELECT COUNT(*) FROM c_juridico WHERE ccj = %s", (cj,))
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        print(f"Erro ao verificar a existência do CJ: {e}")
        return False
    
# Tabela de distâncias médias do Sol para os planetas em quilômetros
distancias_medias = {
    'Mercurio': 57910000,
    'Venus': 108200000,
    'Terra': 149600000,
    'Marte': 227900000,
    'Jupiter': 778300000,
    'Saturno': 1429000000,
    'Urano': 2871000000,
    'Netuno': 4496000000
}

def calcular_distancia(cursor, origem, destino, ccj):
    origem = origem.capitalize()
    destino = destino.capitalize()

    if viagem_existe(cursor, origem, destino, ccj):
            distancia = (abs(distancias_medias[destino] - distancias_medias[origem])) / 1000000
            return distancia
    else:
        print("Viagem não realizada!")
        return False
