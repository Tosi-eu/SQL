from mysql.connector import Error
import mysql.connector
from math import ceil

VERDE = '\033[92m'
VERMELHO = '\033[91m'
AMARELO = '\033[93m'
RESET = '\033[0m'
AZUL_MARINHO = '\033[94m'

def retirar_material_producao(conn, cursor):
    try:
        metros_tecido = float(input(f"\n{AMARELO}[INPUT]{RESET} Digite quantos metros^2 de tecido serão produzidos: "))
        fios_necessarios = metros_tecido * 1000 
        corante_necessario = metros_tecido * 0.5  

        if metros_tecido > 100.0:
            print(f"\n{VERMELHO}[ERRO]{RESET} Capacidade máxima de produção são 100 m²")
            return

        fio_id = int(input(f"\n{AMARELO}[INPUT]{RESET} Digite o ID do fio a ser utilizado: "))
        corante_id = int(input(f"\n{AMARELO}[INPUT]{RESET} Digite o ID do corante a ser utilizado: "))

        cursor.execute("""
            SELECT Fio.metragem, Fio.tipo_fio_id, TipoFio.cor 
            FROM Fio 
            JOIN TipoFio ON Fio.tipo_fio_id = TipoFio.id 
            WHERE Fio.id = %s AND Fio.em_estoque = TRUE
        """, (fio_id,))
        fio = cursor.fetchone()

        cursor.execute("SELECT litros FROM Corante WHERE id = %s AND em_estoque = TRUE", (corante_id,))
        corante = cursor.fetchone()

        if not fio or not corante:
            print(f"\n{VERMELHO}[ERRO]{RESET} Fio ou corante não encontrado ou fora de estoque.")
            return

        if fio[0] < fios_necessarios:
            print(f"\n{VERMELHO}[ERRO]{RESET} Fio insuficiente. Metragem disponível: {fio[0]} metros.")
            return

        if corante[0] < corante_necessario:
            print(f"\n{VERMELHO}[ERRO]{RESET} Corante insuficiente. Litros disponíveis: {corante[0]} litros.")
            return

        cursor.execute("UPDATE Fio SET metragem = metragem - %s WHERE id = %s", (fios_necessarios, fio_id))
        cursor.execute("UPDATE Corante SET litros = litros - %s WHERE id = %s", (corante_necessario, corante_id))

        if fio[0] == fios_necessarios:
            cursor.execute("UPDATE Fio SET em_estoque = FALSE WHERE id = %s", (fio_id,))
        if corante[0] == corante_necessario:
            cursor.execute("UPDATE Corante SET em_estoque = FALSE WHERE id = %s", (corante_id,))

        tipo_fio_id = fio[1] 
        cor_fio = fio[2]  

        codigo_barra = gerar_codigo_barra_ordem_producao(fio_id, corante_id, metros_tecido, tipo_fio_id, cor_fio.upper())

        cursor.execute("""
            INSERT INTO OrdemProducao (codigo_barra, metros_produzidos, fio_id, corante_id, data_inicio, status, litros)
            VALUES (%s, %s, %s, %s, NOW(), 'Em processamento', %s)
        """, (codigo_barra, metros_tecido, fio_id, corante_id, corante_necessario))

        conn.commit()
        print(f"\n{VERDE}[SUCESSO]{RESET} Materiais retirados e ordem de produção registrada com sucesso.")
    
    except Exception as e:
        conn.rollback()
        print(f"\n{VERMELHO}[ERRO]{RESET} Ao retirar material e gerar ordem de produção: {e}")

def receber_material(conn, cursor):
    try:
        tipo_material = input(f"\n{AMARELO}[INPUT]{RESET} Digite o tipo de material ({AMARELO}F{RESET}io/{AMARELO}C{RESET}orante): ").strip().upper()[0]
        if tipo_material not in ['F', 'C']:
            print(f"\n{VERMELHO}[ERRO]{RESET} Tipo de material não especificado")
            return
        
        fornecedor_id = int(input(f"\n{AMARELO}[INPUT]{RESET} Digite o ID do fornecedor: "))

        cursor.execute("SELECT id FROM FORNECEDOR WHERE id = %s", (fornecedor_id,))
        resp = cursor.fetchone()

        if not resp:
            print(f"\n{VERMELHO}[ERRO]{RESET} Fornecedor não encontrado!")
            return

        if tipo_material == 'F':
            codigo_barra = input(f"\n{AMARELO}[INPUT]{RESET} Digite o código de barras do fio: ").strip()
            tipo_fio_id, metragem_extraida = extrair_dados_codigo_barra(codigo_barra)
            if int(metragem_extraida) > 100000:
                print(f"\n{VERMELHO}[ERRO]{RESET}Metragem maior que o limite!")
                return

            if tipo_fio_id is None or metragem_extraida is None:
                print(f"\n{VERMELHO}[ERRO]{RESET} Código de barras inválido!")
                return

            resposta = input(f"\n{AMARELO}[CONFIRMAR]{RESET} A metragem é de {metragem_extraida}. Confirma? (S/N): ").strip().upper()[0]
            if resposta != 'S':
                print(f"\n{VERMELHO}[ERRO]{RESET} Metragem não confirmada!")
                return
            
            cursor.execute("SELECT metragem FROM Fio WHERE tipo_fio_id = %s AND fornecedor_id = %s", (tipo_fio_id, fornecedor_id))
            material_existente = cursor.fetchone()

            if material_existente:

                resp = input(f"\n{AMARELO}[INFO]{RESET} Produto já encontrado no sistema. Atualizar estoque?").strip().upper()[0]
                if resp == "S":
                    metragem_existente = material_existente[0]
                    nova_metragem = metragem_existente + metragem_extraida
                    codigo_barra = f"{tipo_fio_id}{nova_metragem}"
                    novo_codigo_barra = codigo_barra.zfill(12)

                    cursor.execute("UPDATE Fio SET metragem = %s, codigo_barra = %s, em_estoque = TRUE WHERE tipo_fio_id = %s AND fornecedor_id = %s", 
                                (nova_metragem, novo_codigo_barra, tipo_fio_id, fornecedor_id))
                    print(f"\n{VERDE}[INFO]{RESET} Mtragem e código de barras atualizados.")
                else:
                    print(f"\n{AMARELO}[INFO]{RESET} Operação cancelada")
                    return
            else:
                codigo_barra = f"{tipo_fio_id}{metragem_extraida}"
                novo_codigo_barra = codigo_barra.zfill(12)
                cursor.execute("INSERT INTO Fio (codigo_barra, tipo_fio_id, metragem, em_estoque, fornecedor_id) VALUES (%s, %s, %s, TRUE, %s)", 
                               (novo_codigo_barra, tipo_fio_id, metragem_extraida, fornecedor_id))
            conn.commit()

        elif tipo_material == 'C':
            codigo_barra = input(f"\n{AMARELO}[INPUT]{RESET} Digite o código de barras do corante: ").strip()
            tipo_corante_id, metragem_extraida = extrair_dados_codigo_barra(codigo_barra) 

            if tipo_corante_id is None or metragem_extraida is None:
                print(f"\n{VERMELHO}[ERRO]{RESET} Código de barras inválido!")
                return

            resposta = input(f"\n{AMARELO}[CONFIRMAR]{RESET} O total de litros é {metragem_extraida * 4}. Confirma? (S/N): ").strip().upper()[0]
            if resposta != 'S':
                print(f"\n{VERMELHO}[ERRO]{RESET} Quantidade não confirmada!")
                return

            cursor.execute("SELECT litros FROM Corante WHERE tipo_corante_id = %s AND fornecedor_id = %s", (tipo_corante_id, fornecedor_id))
            material_existente = cursor.fetchone()

            if material_existente:
                resp = input(f"\n{AMARELO}[INFO]{RESET} Produto já encontrado no sistema. Atualizar estoque?").strip().upper()[0]
                if resp == "S":
                    litros_existente = material_existente[0]
                    novo_litro = litros_existente + (metragem_extraida * 4)
                    codigo_barra = f"{tipo_corante_id}{novo_litro}"
                    novo_codigo_barra_somado = codigo_barra.zfill(12)
                    
                    cursor.execute("UPDATE Corante SET litros = %s, codigo_barra = %s, em_estoque = TRUE WHERE tipo_corante_id = %s AND fornecedor_id = %s", 
                                (novo_litro, novo_codigo_barra_somado, tipo_corante_id, fornecedor_id))
                    print(f"\n{VERDE}[INFO]{RESET} Material já cadastrado, litros e código de barras atualizados.")
                else:
                    print(f"\n{AMARELO}[INFO]{RESET} Operação cancelada")
                    return
            else:
                codigo_barra = f"{tipo_corante_id}{metragem_extraida * 4}"
                novo_codigo_barra = codigo_barra.zfill(12)
                cursor.execute("INSERT INTO Corante (codigo_barra, tipo_corante_id, fornecedor_id, litros, em_estoque) VALUES (%s, %s, %s, %s, TRUE)", 
                               (novo_codigo_barra, tipo_corante_id, fornecedor_id, metragem_extraida * 4))
            conn.commit()

        else:
            print(f"\n{VERMELHO}[ERRO]{RESET} Tipo de material inválido!")
            return

        print(f"\n{VERDE}[SUCESSO]{RESET} Material recebido com sucesso!")
    
    except Exception as e:
        conn.rollback()
        print(f"\n{VERMELHO}[ERRO]{RESET} Ao receber material: {e}")

def gerar_codigo_barra_ordem_producao(fio_id, corante_id, metros, tipo_fio_id, cor_fio):
    codigo = str(f"{fio_id}{tipo_fio_id}{corante_id}{ceil(metros)}{cor_fio}")   
    codigo_barra = codigo.zfill(12)
    return codigo_barra

def conexao_bd(db_host, db_user, psswd, db):
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=psswd,
        database=db
    )

def extrair_dados_codigo_barra(codigo_barra):
    try:
        codigo_barra = codigo_barra.zfill(12)
        tipo_fio_id = int(codigo_barra[:6])  
        metragem = int(codigo_barra[6:])     

        return tipo_fio_id, metragem
    except ValueError:
        return None, None
    
def registrar_producao(conn, cursor):
    try:
        ordem_id = int(input(f"\n{AMARELO}[INPUT]{RESET} Digite o ID da ordem de produção: "))

        cursor.execute("""
            SELECT OP.id, OP.CODIGO_BARRA, OP.metros_produzidos, F.id, F.codigo_barra, C.id, C.codigo_barra, OP.status
            FROM OrdemProducao OP
            JOIN Fio F ON OP.fio_id = F.id
            JOIN Corante C ON OP.corante_id = C.id
            WHERE OP.id = %s
        """, (ordem_id,))
        ordem = cursor.fetchone()

        if not ordem:
            print(f"\n{VERMELHO}[ERRO]{RESET} Ordem de produção não encontrada.")
            return

        print(f"\n{AMARELO}[ORDEM ENCONTRADA]{RESET}")
        print(ordem)
        print(f"ID: {ordem[0]}")
        print(f"Código de barra: {ordem[1]}")
        print(f"Metros Produzidos: {ordem[2]}")
        print(f"Fio ID: {ordem[3]} | Código de Barras Fio: {ordem[4]}")
        print(f"Corante ID: {ordem[5]} | Código de Barras Corante: {ordem[6]}")
        print(f"Status: {ordem[7]}")

        if ordem[7] == 'Concluída':
            print(f"\n{VERMELHO}[ERRO]{RESET} Produto já esta processado no sistema!")

        confirmacao = input(f"\n{AMARELO}[INPUT]{RESET} Deseja finalizar essa ordem de produção? ({AMARELO}S{RESET}/{AMARELO}n{RESET}): ").upper()[0]
        if confirmacao != 'S':
            print(f"\n{VERMELHO}[CANCELADO]{RESET} A produção foi cancelada pelo usuário.")
            return

        cursor.execute("UPDATE OrdemProducao SET status = 'Concluída' WHERE id = %s", (ordem_id,))

        cursor.execute("SELECT id FROM TipoFio WHERE id = (SELECT tipo_fio_id FROM Fio WHERE id = %s)", (ordem[3],))
        tipo_fio_existe = cursor.fetchone()
        tipo_fio_id = tipo_fio_existe[0]

        cursor.execute("SELECT id FROM TipoCorante WHERE id = (SELECT tipo_corante_id FROM Corante WHERE id = %s)", (ordem[5],))
        tipo_corante_existe = cursor.fetchone()
        tipo_corante_id = tipo_corante_existe[0]

        if not tipo_fio_existe:
            print(f"\n{VERMELHO}[ERRO]{RESET} O tipo de fio (ID: {ordem[3]}) não existe.")
            return

        if not tipo_corante_existe:
            print(f"\n{VERMELHO}[ERRO]{RESET} O tipo de corante (ID: {ordem[5]}) não existe.")
            return

        cursor.execute("""
            INSERT INTO ProdutoFinal (codigo_barra, ordem_producao_id, tipo_corante_id, tipo_fio_id) 
            VALUES (%s, %s, %s, %s)
        """, (ordem[1], ordem_id, tipo_corante_id, tipo_fio_id)) 

        conn.commit()
        print(f"\n{VERDE}[SUCESSO]{RESET} Produção registrada com sucesso!")
    
    except Exception as e:
        conn.rollback()
        print(f"\n{VERMELHO}[ERRO]{RESET} Ao registrar produção: {e}")

def gerar_relatorios(cursor):
    try:
        relatorio = input(f"\n{AMARELO}[INPUT]{RESET} Digite o tipo de relatório ({AMARELO}E{RESET}stoque/{AMARELO}P{RESET}rocesso/{AMARELO}I{RESET}nventario): ").strip().upper()[0]
        
        if relatorio == "E":
            cursor.execute("SELECT tipo_fio_id, metragem FROM Fio WHERE em_estoque = TRUE")
            fios = cursor.fetchall()
            cursor.execute("SELECT tipo_corante_id, litros FROM Corante WHERE em_estoque = TRUE")
            corantes = cursor.fetchall()
            
            print("\nEstoque de fios:")
            for fio in fios:
                print(f"Tipo de Fio ID: {fio[0]}, Metragem Total: {fio[1]}")
                
            print("\nEstoque de corantes:")
            for corante in corantes:
                print(f"Tipo de Corante ID: {corante[0]}, Litros Totais: {corante[1]}")
        
        elif relatorio == "P":
            cursor.execute("""
                SELECT OP.CODIGO_BARRA, TF.DESCRICAO, TC.DESCRICAO, OP.METROS_PRODUZIDOS, OP.DATA_INICIO, FR.NOME, FR.CEP, C.LITROS FROM ORDEMPRODUCAO OP
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
                print(f"Metros Produzidos: {processo[3]}, Litros utilizados: {processo[8]}, Data Início: {processo[4]}")
                print(f"Fornecedor: {processo[5]}, CEP: {processo[6]}")
                print('-' * 50)
        
        elif relatorio == "I":
            cursor.execute("""
                SELECT OP.ID, OP.METROS_PRODUZIDOS, OP.DATA_INICIO, 
                       TF.COR, TF.DESCRICAO, TC.COR, TC.DESCRICAO 
                FROM PRODUTOFINAL PF
                JOIN ORDEMPRODUCAO OP ON OP.ID = PF.ORDEM_PRODUCAO_ID
                JOIN TIPOFIO TF ON TF.ID = PF.TIPO_FIO_ID
                JOIN TIPOCORANTE TC ON TC.ID = PF.TIPO_CORANTE_ID
            """)
            inventario = cursor.fetchall()
            
            print("\nRelatório de Inventário:\n")
            for item in inventario:
                print(f"Ordem Produção ID: {item[0]}, Metros Produzidos: {item[1]}, Data Início: {item[2]}")
                print(f"Tipo de Fio - Cor: {item[3]}, Descrição: {item[4]}")
                print(f"Tipo de Corante - Cor: {item[5]}, Descrição: {item[6]}")
                print('-' * 50)
        
        else:
            print(f"\n{VERMELHO}[ERRO]{RESET} Tipo de relatório inválido!")
    
    except Exception as e:
        print(f"\n{VERMELHO}[ERRO]{RESET} Ao gerar relatório: {e}")

def cadastrar_tipo_material(conn, cursor):
    try:
        tipo_material = input(f"\n{AMARELO}[INPUT]{RESET} Digite o tipo de material que deseja cadastrar ({AMARELO}F{RESET}io/{AMARELO}C{RESET}orante): ").strip().upper()[0]
        
        if tipo_material == 'F':
            descricao = input(f"\n{AMARELO}[INPUT]{RESET} Digite a descrição do tipo de fio: ").strip()
            cor = input(f"\n{AMARELO}[INPUT]{RESET} Digite a cor do fio: ").strip()
            cursor.execute("INSERT INTO TipoFio (descricao, cor) VALUES (%s, %s)", (descricao, cor))
        elif tipo_material == 'C':
            descricao = input(f"\n{AMARELO}[INPUT]{RESET} Digite a descrição do tipo de corante: ").strip()
            cor = input(f"\n{AMARELO}[INPUT]{RESET} Digite a cor do corante: ").strip()
            cursor.execute("INSERT INTO TipoCorante (descricao, cor) VALUES (%s, %s)", (descricao, cor))
        else:
            print(f"\n{VERMELHO}[ERRO]{RESET} Tipo de material inválido!")
            return
        
        conn.commit()
        print(f"\n{VERDE}[SUCESSO]{RESET} Material cadastrado com sucesso!")
    except Exception as e:
        conn.rollback()
        print(f"\n{VERMELHO}[ERRO]{RESET} Ao cadastrar tipo de material: {e}")

def cadastrar_fornecedor(conn, cursor):
    try:
        nome = input(f"\n{AMARELO}[INPUT]{RESET} Digite o nome do fornecedor: ").strip()
        contato = input(f"\n{AMARELO}[INPUT]{RESET} Digite o contato do fornecedor: ").strip()
        cep = input(f"\n{AMARELO}[INPUT]{RESET} Digite o CEP do fornecedor: ").strip()

        cursor.execute("SELECT * FROM Fornecedor WHERE cep = %s AND nome = %s", (cep, nome))
        fornecedor_existente = cursor.fetchone()

        if fornecedor_existente:
            print(f"\n{VERMELHO}[ERRO]{RESET} Já existe um fornecedor com esse CEP cadastrado.")
            return

        cursor.execute("INSERT INTO Fornecedor (nome, contato, cep) VALUES (%s, %s, %s)", (nome, contato, cep))
        conn.commit()
        print(f"\n{VERDE}[SUCESSO]{RESET} Fornecedor cadastrado com sucesso!")
    except Exception as e:
        conn.rollback()
        print(f"\n{VERMELHO}[ERRO]{RESET} Ao cadastrar fornecedor: {e}")

try:
    conn = conexao_bd("localhost", "root", "tr%mmanc@p0t&", "industria_textil")
    cursor = conn.cursor()
        
    while True:
        print(f"\n{AMARELO}[MENU]{RESET}Escolha uma opção: \n")
        print(f"{AZUL_MARINHO}[OPÇÃO 1]{RESET} Receber material")
        print(f"{AZUL_MARINHO}[OPÇÃO 2]{RESET} Retirar material para produção")
        print(f"{AZUL_MARINHO}[OPÇÃO 3]{RESET} Cadastrar tipo de material")
        print(f"{AZUL_MARINHO}[OPÇÃO 4]{RESET} Cadastrar novo fornecedor")
        print(f"{AZUL_MARINHO}[OPÇÃO 5]{RESET} Registrar produção")
        print(f"{AZUL_MARINHO}[OPÇÃO 6]{RESET} Gerar relatórios")
        print(f"{AZUL_MARINHO}[OPÇÃO 7]{RESET} Sair")

        opcao = input(f"\n{AMARELO}[INPUT]{RESET} Digite o número da opção desejada: ").strip()

        if opcao == "1":
            receber_material(conn, cursor)
        elif opcao == "2":
            retirar_material_producao(conn, cursor)
        elif opcao == "3":
            cadastrar_tipo_material(conn, cursor)
        elif opcao == "4":
            cadastrar_fornecedor(conn, cursor)
        elif opcao == "5":
            registrar_producao(conn, cursor)
        elif opcao == "6":
            gerar_relatorios(cursor)
        elif opcao == "7":
            print(f"\n{AMARELO}[INFO]{RESET}Saindo do sistema...")
            cursor.close()
            break
        else:
            print(f"\n{VERMELHO}[ERRO]{RESET}Opção inválida! Tente novamente.")
except Error as e:
    print(f"\n{VERMELHO}[ERRO]{RESET}Erro ao tentar se conectar ao banco de dados: {e}")
except Exception as e:
    print(f"\n{VERMELHO}[ERRO]{RESET}Ocorreu um erro inesperado: {e}")
