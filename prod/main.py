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
        metros_tecido = float(input(f"\n{AMARELO}[INPUT]{RESET} Digite quantos metros² de tecido serão produzidos: "))
        fios_necessarios = metros_tecido * 1000 
        corante_necessario = metros_tecido * 0.5  

        if metros_tecido > 100.0:
            print(f"\n{VERMELHO}[ERRO]{RESET} Capacidade máxima de produção são 100 m²")
            return

        fio_id = int(input(f"\n{AMARELO}[INPUT]{RESET} Digite o ID do fio a ser utilizado: "))
        corante_id = int(input(f"\n{AMARELO}[INPUT]{RESET} Digite o ID do corante a ser utilizado: "))

        cursor.execute("""
            SELECT Fio.metragem, Fio.tipo_fio_id, Cores.id
            FROM Fio 
            JOIN TipoFio ON Fio.tipo_fio_id = TipoFio.id 
            JOIN Cores ON Cores.id = TipoFio.cor
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

        codigo_barra = gerar_codigo_barra_ordem_producao(fio_id, corante_id, metros_tecido, tipo_fio_id, cor_fio)

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
        codigo_barra = input(f"\n{AMARELO}[INPUT]{RESET} Digite o código de barras: ").strip()
        
        tipo_material = codigo_barra[0]
        if tipo_material not in ['1', '2'] or len(codigo_barra) != 12:
            print(f"\n{VERMELHO}[ERRO]{RESET} Código de barras inválido!")
            return

        fornecedor_id = codigo_barra[1:4].lstrip('0')
        tipo_material_id = codigo_barra[4:6].lstrip('0') 
        quantidade_extraida = int(codigo_barra[6:].lstrip('0'))

        cursor.execute("SELECT id FROM FORNECEDOR WHERE id = %s", (fornecedor_id,))
        resp = cursor.fetchone()
        if not resp:
            print(f"\n{VERMELHO}[ERRO]{RESET} Fornecedor não encontrado!")
            return

        if tipo_material == '1':  # Para fios
            if quantidade_extraida > 100000:
                print(f"\n{VERMELHO}[ERRO]{RESET} Metragem maior que o limite!")
                return
            
            resposta = input(f"\n{AMARELO}[CONFIRMAR]{RESET} A metragem é de {quantidade_extraida}. Confirma? (S/N): ").strip().upper()[0]
            if resposta != 'S':
                print(f"\n{VERMELHO}[ERRO]{RESET} Metragem não confirmada!")
                return

            cursor.execute("SELECT metragem FROM Fio WHERE tipo_fio_id = %s AND fornecedor_id = %s", (tipo_material_id, fornecedor_id))
            material_existente = cursor.fetchone()

            if material_existente:
                resp = input(f"\n{AMARELO}[INFO]{RESET} Produto já encontrado no sistema. Atualizar estoque? (S/N): ").strip().upper()[0]
                if resp == "S":
                    metragem_existente = material_existente[0]
                    nova_metragem = metragem_existente + quantidade_extraida
                    novo_codigo_barra = codigo_barra[:6] + str(nova_metragem).zfill(6)

                    cursor.execute("""
                        UPDATE Fio 
                        SET metragem = %s, codigo_barra = %s, em_estoque = TRUE 
                        WHERE tipo_fio_id = %s AND fornecedor_id = %s
                    """, (nova_metragem, novo_codigo_barra, tipo_material_id, fornecedor_id))
                    print(f"\n{VERDE}[INFO]{RESET} Metragem e código de barras atualizados.")
                else:
                    print(f"\n{AMARELO}[INFO]{RESET} Operação cancelada")
                    return
            else:
                cursor.execute("""
                    INSERT INTO Fio (codigo_barra, tipo_fio_id, metragem, em_estoque, fornecedor_id) 
                    VALUES (%s, %s, %s, TRUE, %s)
                """, (codigo_barra, tipo_material_id, quantidade_extraida, fornecedor_id))
            conn.commit()

        if tipo_material == '2':  # Para corantes
            resposta = input(f"\n{AMARELO}[CONFIRMAR]{RESET} O total de litros é {quantidade_extraida} galões. Confirma? (S/N): ").strip().upper()[0]
            if resposta != 'S':
                print(f"\n{VERMELHO}[ERRO]{RESET} Quantidade não confirmada!")
                return

            cursor.execute("SELECT litros FROM Corante WHERE tipo_corante_id = %s AND fornecedor_id = %s", (tipo_material_id, fornecedor_id))
            material_existente = cursor.fetchone()

            if material_existente:
                resp = input(f"\n{AMARELO}[INFO]{RESET} Produto já encontrado no sistema. Atualizar estoque? (S/N): ").strip().upper()[0]
                if resp == "S":
                    litros_existente = material_existente[0]
                    novo_litro = litros_existente + (quantidade_extraida * 4)
                    novo_codigo_barra = codigo_barra[:6] + str(novo_litro).zfill(6)

                    cursor.execute("""
                        UPDATE Corante 
                        SET litros = %s, codigo_barra = %s, em_estoque = TRUE 
                        WHERE tipo_corante_id = %s AND fornecedor_id = %s
                    """, (novo_litro, novo_codigo_barra, tipo_material_id, fornecedor_id))
                    print(f"\n{VERDE}[INFO]{RESET} Material já cadastrado, litros e código de barras atualizados.")
                else:
                    print(f"\n{AMARELO}[INFO]{RESET} Operação cancelada")
                    return
            else:
                cursor.execute("""
                    INSERT INTO Corante (codigo_barra, tipo_corante_id, fornecedor_id, litros, em_estoque) 
                    VALUES (%s, %s, %s, %s, TRUE)
                """, (codigo_barra, tipo_material_id, fornecedor_id, quantidade_extraida * 4))
            conn.commit()

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
            # Estoque de Fios
            cursor.execute("""
                SELECT TF.descricao, C.cor, F.metragem 
                FROM Fio F
                JOIN TipoFio TF ON F.tipo_fio_id = TF.id
                JOIN Cores C ON TF.cor = C.id
                WHERE F.em_estoque = TRUE
            """)
            fios = cursor.fetchall()
            
            cursor.execute("""
                SELECT TC.descricao, C.cor, COR.litros 
                FROM Corante COR
                JOIN TipoCorante TC ON COR.tipo_corante_id = TC.id
                JOIN Cores C ON TC.cor = C.id
                WHERE COR.em_estoque = TRUE
            """)
            corantes = cursor.fetchall()
            
            print("\nEstoque de fios:")
            for fio in fios:
                print(f"Descrição do Fio: {fio[0]}, Cor: {fio[1]}, Metragem Total: {fio[2]}")
                
            print("\nEstoque de corantes:")
            for corante in corantes:
                print(f"Descrição do Corante: {corante[0]}, Cor: {corante[1]}, Litros Totais: {corante[2]}")
        
        elif relatorio == "P":
            cursor.execute("""
                SELECT OP.codigo_barra, TF.descricao, CF.cor, TC.descricao, CC.cor, OP.metros_produzidos, OP.data_inicio, 
                       FR.nome, FR.cep, OP.litros 
                FROM OrdemProducao OP
                JOIN Fio F ON F.id = OP.fio_id
                JOIN TipoFio TF ON TF.id = F.tipo_fio_id
                JOIN Cores CF ON TF.cor = CF.id
                JOIN Corante C ON C.id = OP.corante_id
                JOIN TipoCorante TC ON TC.id = C.tipo_corante_id
                JOIN Cores CC ON TC.cor = CC.id
                JOIN Fornecedor FR ON FR.id = F.fornecedor_id OR FR.id = C.fornecedor_id
            """)
            processos = cursor.fetchall()
            
            print("\nRelatório de Processos em Andamento:\n")
            for processo in processos:
                print(f"Código de Barra: {processo[0]}, Fio: {processo[1]} (Cor: {processo[2]}), Corante: {processo[3]} (Cor: {processo[4]})")
                print(f"Metros Produzidos: {processo[5]}, Litros utilizados: {processo[9]}, Data Início: {processo[6]}")
                print(f"Fornecedor: {processo[7]}, CEP: {processo[8]}")
                print('-' * 50)
        
        elif relatorio == "I":
            cursor.execute("""
                SELECT OP.id, OP.metros_produzidos, OP.data_inicio, CF.cor, TF.descricao, CC.cor, TC.descricao
                FROM ProdutoFinal PF
                JOIN OrdemProducao OP ON OP.id = PF.ordem_producao_id
                JOIN TipoFio TF ON TF.id = PF.tipo_fio_id
                JOIN Cores CF ON TF.cor = CF.id
                JOIN TipoCorante TC ON TC.id = PF.tipo_corante_id
                JOIN Cores CC ON TC.cor = CC.id
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
        
        if tipo_material not in ['F', 'C']:
            print(f"\n{VERMELHO}[ERRO]{RESET} Tipo de material inválido!")
            return

        descricao = input(f"\n{AMARELO}[INPUT]{RESET} Digite a descrição do tipo de material: ").strip()
        cor = input(f"\n{AMARELO}[INPUT]{RESET} Digite a cor do material: ").strip().title()

        cursor.execute("SELECT id FROM Cores WHERE cor = %s", (cor,))
        cor_id = cursor.fetchone()

        if cor_id is None:
            print(f"\n{VERMELHO}[ERRO]{RESET} Cor '{cor}' não encontrada!")
            return

        cor_id = cor_id[0] 

        if tipo_material == 'F':
            cursor.execute("INSERT INTO TipoFio (descricao, cor) VALUES (%s, %s)", (descricao, cor_id))
        elif tipo_material == 'C':
            cursor.execute("INSERT INTO TipoCorante (descricao, cor) VALUES (%s, %s)", (descricao, cor_id))

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
