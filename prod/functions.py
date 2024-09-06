from datetime import datetime
import random
import string
import mysql.connector

VERDE = '\033[92m'
VERMELHO = '\033[91m'
AMARELO = '\033[93m'
RESET = '\033[0m'
AZUL_MARINHO = '\033[94m'

def conexao_bd(db_host, db_user, psswd, db):
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=psswd,
        database=db
    )

def receber_material(conn, cursor):
    try:
        tipo_material = input(f"{AMARELO}[INPUT]{RESET} Digite o tipo de material ({AMARELO}F{RESET}io/{AMARELO}C{RESET}orante): ").strip().upper()[0]
        if tipo_material[0] not in ['F', 'C']:
            print( f"\n{VERMELHO}[ERRO]{RESET} Tipo de material não especificado" )
            return
        codigo_barra = _gerar_codigo_barra()
        fornecedor_id = int(input(f"{AMARELO}[INPUT]{RESET} Digite o ID do fornecedor: "))
        
        if tipo_material == 'F':
            metragem = float(input(f"{AMARELO}[INPUT]{RESET} Digite a metragem do fio: "))
            tipo_fio_id = int(input(f"{AMARELO}[INPUT]{RESET} Digite o ID do tipo de fio: "))
            cursor.execute("INSERT INTO Fio (codigo_barra, tipo_fio_id, metragem, em_estoque, fornecedor_id) VALUES (%s, %s, %s, TRUE, %s)", 
                           (codigo_barra, tipo_fio_id, metragem, fornecedor_id))
            if not conferir_fio(conn, cursor, codigo_barra, metragem, fornecedor_id):
                return f"{VERMELHO}[ERRO]{RESET} Material não confere com o enviado pelo fornecedor"
            conn.commit()
        elif tipo_material == 'C':
            litros = float(input(f"{AMARELO}[INPUT]{RESET} Digite a quantidade de galões de corante: "))
            tipo_corante_id = int(input(f"{AMARELO}[INPUT]{RESET} Digite o ID do tipo de corante: "))
            cursor.execute("INSERT INTO Corante (codigo_barra, tipo_corante_id, litros, em_estoque, fornecedor_id) VALUES (%s, %s, %s, TRUE, %s)", 
                           (codigo_barra, tipo_corante_id, litros * 4, fornecedor_id))
            if not conferir_corante(conn, cursor, codigo_barra, litros * 4, fornecedor_id):
                return f"{VERMELHO}[ERRO]{RESET} Material não confere com o enviado pelo fornecedor"
            conn.commit()
        else:
            print(f"{VERMELHO}[ERRO]{RESET} Tipo de material inválido!")
            return
        print(f"{VERDE}[SUCESSO]{RESET} Material recebido com sucesso!")
    except Exception as e:
        conn.rollback()
        print(f"{VERMELHO}[ERRO]{RESET} Ao receber material: {e}")


def conferir_fio(conn, cursor, codigo_barra, metragem_informada, fornecedor_id):
    try:
        cursor.execute("SELECT metragem, fornecedor_id FROM Fio WHERE codigo_barra = %s", (codigo_barra,))
        result = cursor.fetchone()
        if result:
            metragem_real, fornecedor_registrado = result
            if fornecedor_registrado != fornecedor_id:
                print(f"{VERMELHO}[ERRO]{RESET} Fornecedor não confere.")
                cursor.execute("DELETE FROM Fio WHERE codigo_barra = %s", (codigo_barra,))
                conn.commit()
                return False
            if metragem_real == metragem_informada:
                print(f"\n{VERDE}[SUCESSO]{RESET} Metragem confirmada.")
                return True
            else:
                print(f"{VERMELHO}[ERRO]{RESET} Metragem não confere. Entrada não permitida.")
                cursor.execute("DELETE FROM Fio WHERE codigo_barra = %s", (codigo_barra,))
                conn.commit()
                return False
        else:
            print(f"{VERMELHO}[ERRO]{RESET} Fio não encontrado no sistema.")
            return False
    except Exception as e:
        print(f"{VERMELHO}[ERRO]{RESET} Ao conferir fio: {e}")
        return False

def conferir_corante(conn, cursor, codigo_barra, litros_informados, fornecedor_id):
    try:
        cursor.execute("SELECT litros, fornecedor_id FROM Corante WHERE codigo_barra = %s", (codigo_barra,))
        result = cursor.fetchone()
        if result:
            litros_reais, fornecedor_registrado = result
            if fornecedor_registrado != fornecedor_id:
                print(f"{VERMELHO}[ERRO]{RESET} Fornecedor não confere.")
                cursor.execute("DELETE FROM Corante WHERE codigo_barra = %s", (codigo_barra,))
                conn.commit()
                return False
            if litros_reais == litros_informados:
                print(f"\n{VERDE}[SUCESSO]{RESET} Quantidade de corante confirmada.")
                return True
            else:
                print(f"{VERMELHO}[ERRO]{RESET} Quantidade de corante não confere. Entrada não permitida.")
                cursor.execute("DELETE FROM Corante WHERE codigo_barra = %s", (codigo_barra,))
                conn.commit()
                return False
        else:
            print(f"{VERMELHO}[ERRO]{RESET} Corante não encontrado no sistema.")
            return False
        
    except Exception as e:
        print(f"{VERMELHO}[ERRO]{RESET} Ao conferir corante: {e}")
        return False

def _gerar_codigo_barra():
    return ''.join(random.choices(string.digits, k=12))

def retirar_material_producao(conn, cursor):
    try:
        metros_tecido = float(input(f"{AMARELO}[INPUT]{RESET} Digite quantos metros^2 de tecido serão produzidos: "))
        fios_necessarios = metros_tecido * 1000  
        corante_necessario = metros_tecido * 0.5  

        fio_id = int(input(f"{AMARELO}[INPUT]{RESET} Digite o ID do fio a ser utilizado: "))
        corante_id = int(input(f"{AMARELO}[INPUT]{RESET} Digite o ID do corante a ser utilizado: "))

        cursor.execute("SELECT metragem FROM Fio WHERE id = %s AND em_estoque = TRUE", (fio_id,))
        fio = cursor.fetchone()

        cursor.execute("SELECT litros FROM Corante WHERE id = %s AND em_estoque = TRUE", (corante_id,))
        corante = cursor.fetchone()

        if not fio or not corante:
            print(f"{VERMELHO}[ERRO]{RESET} Fio ou corante não encontrado ou fora de estoque.")
            return

        if fio[0] < fios_necessarios:
            print(f"{VERMELHO}[ERRO]{RESET} Fio insuficiente. Metragem disponível: {fio[0]} metros.")
            return

        if corante[0] < corante_necessario:
            print(f"{VERMELHO}[ERRO]{RESET} Corante insuficiente. Litros disponíveis: {corante[0]} litros.")
            return

        cursor.execute("UPDATE Fio SET metragem = metragem - %s WHERE id = %s", (fios_necessarios, fio_id))
        cursor.execute("UPDATE Corante SET litros = litros - %s WHERE id = %s", (corante_necessario, corante_id))

        if fio[0] == fios_necessarios:
            cursor.execute("UPDATE Fio SET em_estoque = FALSE WHERE id = %s", (fio_id,))
        if corante[0] == corante_necessario:
            cursor.execute("UPDATE Corante SET em_estoque = FALSE WHERE id = %s", (corante_id,))

        codigo_barra = _gerar_codigo_barra()
        data_fim = input(f"{AMARELO}[INPUT]{RESET} Digite a data de fim do projeto (dd/mm/yyyy): ")
        data_fim = datetime.strptime(data_fim, '%d/%m/%Y').replace(hour=23, minute=59, second=59)
        
        cursor.execute("""
            INSERT INTO OrdemProducao (codigo_barra, metros_produzidos, fio_id, corante_id, data_inicio, data_fim, status)
            VALUES (%s, %s, %s, %s, NOW(), %s, 'Em processamento')
        """, (codigo_barra, metros_tecido, fio_id, corante_id, data_fim))

        conn.commit()
        print(f"\n{VERDE}[SUCESSO]{RESET} Materiais retirados e ordem de produção registrada com sucesso.")
    except Exception as e:
        conn.rollback()
        print(f"{VERMELHO}[ERRO]{RESET} Ao retirar material e gerar ordem de produção: {e}")

def registrar_producao(conn, cursor):
    try:
        ordem_id = int(input(f"{AMARELO}[INPUT]{RESET} Digite o ID da ordem de produção: "))

        cursor.execute("""
            SELECT OP.id, OP.metros_produzidos, F.id, F.codigo_barra, C.id, C.codigo_barra, OP.status
            FROM OrdemProducao OP
            JOIN Fio F ON OP.fio_id = F.id
            JOIN Corante C ON OP.corante_id = C.id
            WHERE OP.id = %s
        """, (ordem_id,))
        ordem = cursor.fetchone()

        if not ordem:
            print(f"{VERMELHO}[ERRO]{RESET} Ordem de produção não encontrada.")
            return

        print(f"\n{AMARELO}[ORDEM ENCONTRADA]{RESET}")
        print(f"ID: {ordem[0]}")
        print(f"Metros Produzidos: {ordem[1]}")
        print(f"Fio ID: {ordem[2]} | Código de Barras Fio: {ordem[3]}")
        print(f"Corante ID: {ordem[4]} | Código de Barras Corante: {ordem[5]}")
        print(f"Status: {ordem[6]}")

        confirmacao = input(f"{AMARELO}[INPUT]{RESET} Deseja colocar essa ordem em produção? ({AMARELO}S{RESET}/{AMARELO}n{RESET}): ").upper()[0]
        if confirmacao != 'S':
            print(f"{VERMELHO}[CANCELADO]{RESET} A produção foi cancelada pelo usuário.")
            return

        codigo_barra_produto = _gerar_codigo_barra()
        cursor.execute("UPDATE OrdemProducao SET data_fim = NOW(), status = 'Concluída' WHERE id = %s", (ordem_id,))

        cursor.execute("""
            INSERT INTO ProdutoFinal (codigo_barra, ordem_producao_id, tipo_corante_id, tipo_fio_id) 
            VALUES (%s, %s, %s, %s)
        """, (codigo_barra_produto, ordem_id, ordem[4], ordem[2]))

        conn.commit()
        print(f"\n{VERDE}[SUCESSO]{RESET} Produção registrada com sucesso!")
    
    except Exception as e:
        conn.rollback()
        print(f"{VERMELHO}[ERRO]{RESET} Ao registrar produção: {e}")

def gerar_relatorios(cursor):
    try:
        relatorio = input(f"{AMARELO}[INPUT]{RESET} Digite o tipo de relatório ({AMARELO}E{RESET}stoque/{AMARELO}P{RESET}rocesso/{AMARELO}I{RESET}nventario): ").strip().upper()[0]
        
        if relatorio == "E":
            cursor.execute("SELECT tipo_fio_id, SUM(metragem) FROM Fio WHERE em_estoque = TRUE GROUP BY tipo_fio_id")
            fios = cursor.fetchall()
            cursor.execute("SELECT tipo_corante_id, SUM(litros) FROM Corante WHERE em_estoque = TRUE GROUP BY tipo_corante_id")
            corantes = cursor.fetchall()
            
            print("\nEstoque de fios:")
            for fio in fios:
                print(f"Tipo de Fio ID: {fio[0]}, Metragem Total: {fio[1]}")
                
            print("\nEstoque de corantes:")
            for corante in corantes:
                print(f"Tipo de Corante ID: {corante[0]}, Litros Totais: {corante[1]}")
        
        elif relatorio == "P":
            cursor.execute("""
                SELECT OP.CODIGO_BARRA, TF.DESCRICAO, TC.DESCRICAO, OP.METROS_PRODUZIDOS, OP.DATA_INICIO, OP.DATA_FIM, FR.NOME, FR.CEP, C.LITROS FROM ORDEMPRODUCAO OP
                    JOIN FIO F ON F.ID = OP.FIO_ID
                    JOIN TIPOFIO TF ON TF.ID = F.TIPO_FIO_ID
                    JOIN CORANTE C ON C.ID = OP.CORANTE_ID
                    JOIN TIPOCORANTE TC ON TC.ID = C.TIPO_CORANTE_ID
                    JOIN FORNECEDOR FR ON FR.ID = F.FORNECEDOR_ID OR FR.ID = C.FORNECEDOR_ID
            """)
            processos = cursor.fetchall()
            
            print("\nRelatório de Processos em Andamento:\n")
            for processo in processos:
                print(f"Código de Barra: {processo[0]}, Fio: {processo[1]}, Corante: {processo[2]}")
                print(f"Metros Produzidos: {processo[3]}, Litros utilizados: {processo[8]}, Data Início: {processo[4]}, Data Fim: {processo[5]}")
                print(f"Fornecedor: {processo[6]}, CEP: {processo[7]}")
                print('-' * 50)
        
        elif relatorio == "I":
            cursor.execute("""
                SELECT OP.ID, OP.METROS_PRODUZIDOS, OP.DATA_INICIO, OP.DATA_FIM, 
                       TF.COR, TF.DESCRICAO, TC.COR, TC.DESCRICAO 
                FROM PRODUTOFINAL PF
                JOIN ORDEMPRODUCAO OP ON OP.ID = PF.ORDEM_PRODUCAO_ID
                JOIN TIPOFIO TF ON TF.ID = PF.TIPO_FIO_ID
                JOIN TIPOCORANTE TC ON TC.ID = PF.TIPO_CORANTE_ID
            """)
            inventario = cursor.fetchall()
            
            print("\nRelatório de Inventário:\n")
            for item in inventario:
                print(f"Ordem Produção ID: {item[0]}, Metros Produzidos: {item[1]}, Data Início: {item[2]}, Data Fim: {item[3]}")
                print(f"Tipo de Fio - Cor: {item[4]}, Descrição: {item[5]}")
                print(f"Tipo de Corante - Cor: {item[6]}, Descrição: {item[7]}")
                print('-' * 50)
        
        else:
            print(f"{VERMELHO}[ERRO]{RESET} Tipo de relatório inválido!")
    
    except Exception as e:
        print(f"{VERMELHO}[ERRO]{RESET} Ao gerar relatório: {e}")

def cadastrar_tipo_material(conn, cursor):
    try:
        tipo_material = input(f"{AMARELO}[INPUT]{RESET} Digite o tipo de material que deseja cadastrar ({AMARELO}f{RESET}io/{AMARELO}c{RESET}orante): ").strip().upper()[0]
        
        if tipo_material == 'F':
            descricao = input(f"{AMARELO}[INPUT]{RESET} Digite a descrição do tipo de fio: ").strip()
            cor = input(f"{AMARELO}[INPUT]{RESET} Digite a cor do fio: ").strip()
            cursor.execute("INSERT INTO TipoFio (descricao, cor) VALUES (%s, %s)", (descricao, cor))
        elif tipo_material == 'C':
            descricao = input(f"{AMARELO}[INPUT]{RESET} Digite a descrição do tipo de corante: ").strip()
            cor = input(f"{AMARELO}[INPUT]{RESET} Digite a cor do corante: ").strip()
            cursor.execute("INSERT INTO TipoCorante (descricao, cor) VALUES (%s, %s)", (descricao, cor))
        else:
            print(f"{VERMELHO}[ERRO]{RESET} Tipo de material inválido!")
            return
        
        conn.commit()
        print(f"\n{VERDE}[SUCESSO]{RESET} Material cadastrado com sucesso!")
    except Exception as e:
        conn.rollback()
        print(f"{VERMELHO}[ERRO]{RESET} Ao cadastrar tipo de material: {e}")

def cadastrar_fornecedor(conn, cursor):
    try:
        nome = input(f"{AMARELO}[INPUT]{RESET} Digite o nome do fornecedor: ").strip()
        contato = input(f"{AMARELO}[INPUT]{RESET} Digite o contato do fornecedor: ").strip()
        cep = input(f"{AMARELO}[INPUT]{RESET} Digite o CEP do fornecedor: ").strip()

        cursor.execute("SELECT * FROM Fornecedor WHERE cep = %s AND nome = %s", (cep, nome))
        fornecedor_existente = cursor.fetchone()

        if fornecedor_existente:
            print(f"{VERMELHO}[ERRO]{RESET} Já existe um fornecedor com esse CEP cadastrado.")
            return

        cursor.execute("INSERT INTO Fornecedor (nome, contato, cep) VALUES (%s, %s, %s)", (nome, contato, cep))
        conn.commit()
        print(f"\n{VERDE}[SUCESSO]{RESET} Fornecedor cadastrado com sucesso!")
    except Exception as e:
        conn.rollback()
        print(f"{VERMELHO}[ERRO]{RESET} Ao cadastrar fornecedor: {e}")

def read_file(file_path="prod/secret.txt"):
    file = open(file_path, "r")
    content = file.readlines()
    content_list = [data.replace("\n", "") for data in content]
    file.close()
    return content_list