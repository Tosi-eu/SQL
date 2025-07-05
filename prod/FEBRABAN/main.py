import os
import re
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import datetime
from decimal import Decimal
from prettytable import PrettyTable

"""

faz conexão com o banco padrão do postgres, cria um outro banco chamado 'supermercado'
e encerra a conexão com o banco antigo para se conectar ao novo e criar as tabelas + inserções

"""
def get_connection():
    try:
        # Conecta ao banco padrão para criar o banco 'supermercado'
        conexao_temporaria = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='postgres_Eu12',
            host='localhost',
            port=5432
        )
        conexao_temporaria.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor_temporario = conexao_temporaria.cursor()

        # Cria o banco se ele ainda não existir
        cursor_temporario.execute("SELECT 1 FROM pg_database WHERE datname = 'supermercado'")
        banco_existe = cursor_temporario.fetchone()
        if not banco_existe:
            cursor_temporario.execute("CREATE DATABASE supermercado")
            print("Banco de dados 'supermercado' criado.")
        else:
            print("Banco de dados 'supermercado' já existe.")

        cursor_temporario.close()
        conexao_temporaria.close()

        # Conecta ao banco 'supermercado'
        conexao = psycopg2.connect(
            dbname='supermercado',
            user='postgres',
            password='postgres_Eu12',
            host='localhost',
            port=5432
        )
        print("Conectado ao banco 'supermercado'.")

        with conexao.cursor() as cur:
            # Verifica se uma das tabelas principais já existe, se uma já existe quer dizer que o script já foi executado
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'produtos'
                )
            """)
            tabela_existe = cur.fetchone()[0]

            # Executa o schema.sql apenas se a tabela ainda não existir
            if not tabela_existe:
                caminho_schema = os.path.join(os.getcwd(), "schema.sql") # dá para trocar o os.cwd() pelo caminho do arquivo
                with open(caminho_schema, "r", encoding="utf-8") as arquivo:
                    sql = arquivo.read()
                    cur.execute(sql)
                conexao.commit()
                print("Script schema.sql executado.")
            else:
                print("Tabelas já existem. Pulando execução do schema.sql.")

        return conexao
    except psycopg2.Error as e:
        print(f"Falha ao conectar ao banco: {e}")
        return None

def is_febraban(codigo):
    digitos = re.sub(r'\D', '', codigo)
    return len(digitos) == 44 and digitos.startswith('86')

def parse_codigo_febraban(codigo):
    digitos = re.sub(r'\D', '', codigo)
    if not is_febraban(digitos):
        print("Código inválido. Deve conter 44 dígitos e iniciar com 86.")
        return None
    try:
        valor = Decimal(digitos[4:15]) / 100
        cnpj8 = digitos[15:23]
        campo_livre = digitos[23:]
        validade = datetime.datetime.strptime(campo_livre[0:8], "%Y%m%d").date()
        id_segmento = int(campo_livre[8:10])
        id_produto = int(campo_livre[10:13])
        quantidade = int(campo_livre[13:18])
        return {
            "valor": valor,
            "cnpj8": cnpj8,
            "validade": validade,
            "id_segmento": id_segmento,
            "id_produto": id_produto,
            "quantidade": quantidade
        }
    except Exception as e:
        print(f"Falha ao interpretar código FEBRABAN: {e}")
        return None

def parse_codigo_lote_customizado(codigo):
    padrao = r'LOTE(\d{3})(\d{3})(\d{3})(\d{8})(\d{5})(\d{7})(\d{8})'
    match = re.fullmatch(padrao, codigo)
    if not match:
        return None
    try:
        return {
            "id_produto": int(match.group(1)),
            "empresa_id": int(match.group(2)),
            "id_segmento": int(match.group(3)),
            "validade": datetime.datetime.strptime(match.group(4), "%Y%m%d").date(),
            "quantidade": int(match.group(5)),
            "valor": Decimal(match.group(6)) / 100,
            "cnpj8": match.group(7)
        }
    except Exception as e:
        print(f"Erro ao interpretar código customizado de lote: {e}")
        return None

def atualizar_estoque(cursor, id_produto, quantidade, tipo):
    if tipo == 'entry':
        cursor.execute("UPDATE estoque SET quantidade = quantidade + %s WHERE id_produto = %s", (quantidade, id_produto))
    else:
        cursor.execute("UPDATE estoque SET quantidade = quantidade - %s WHERE id_produto = %s", (quantidade, id_produto))
        cursor.execute("SELECT quantidade FROM estoque WHERE id_produto = %s", (id_produto,))
        qnt = cursor.fetchone()
        if qnt and qnt[0] < 0:
            raise Exception(f"Estoque insuficiente para o produto ID {id_produto}")

#LOTE0010010012025123000500000690002345678
def adicionar_estoque(conexao):
    codigo = input("Digite o código de barras do lote: ").strip()
    dados = parse_codigo_lote_customizado(codigo) if codigo.startswith('LOTE') else parse_codigo_febraban(codigo)

    if not dados:
        print("Código inválido.")
        return

    if dados["validade"] < datetime.date.today():
        print("Produto vencido. Entrada não permitida.")
        return

    try:
        with conexao.cursor() as cur:
            cur.execute("SELECT id FROM segmentos WHERE id = %s", (dados["id_segmento"],))
            if not cur.fetchone():
                cur.execute("INSERT INTO segmentos (id, nome) VALUES (%s, %s)", (dados["id_segmento"], f"Segmento {dados['id_segmento']}"))

            cur.execute("SELECT id FROM fornecedores WHERE cnpj LIKE %s", (dados["cnpj8"] + '%',))
            row = cur.fetchone()
            if row:
                empresa_id = row[0]
            else:
                cur.execute("INSERT INTO fornecedores (nome, id_segmento, cnpj) VALUES (%s, %s, %s) RETURNING id",
                            (f"Empresa {dados['cnpj8']}", dados["id_segmento"], dados["cnpj8"] + "000000"))
                empresa_id = cur.fetchone()[0]

            cur.execute("SELECT preco FROM produtos WHERE id = %s", (dados["id_produto"],))
            preco_existente = cur.fetchone()
            if preco_existente and preco_existente[0] != dados["valor"]:
                print("Valor do lote difere do preço cadastrado. Entrada não permitida.")
                return

            if not preco_existente:
                cur.execute("INSERT INTO produtos (id, code, nome, preco, company_id) VALUES (%s, %s, %s, %s, %s)",
                            (dados["id_produto"], str(dados["id_produto"]).zfill(13), f"Produto {dados['id_produto']}", dados["valor"], empresa_id))
                cur.execute("INSERT INTO estoque (id_produto, quantidade) VALUES (%s, 0)", (dados["id_produto"],))

            cur.execute("SELECT id FROM lotes WHERE codigo = %s", (codigo,))
            if cur.fetchone():
                print("Este lote já foi registrado anteriormente.")
                return

            cur.execute("INSERT INTO lotes (codigo, id_produto, quantidade) VALUES (%s, %s, %s)",
                        (codigo, dados["id_produto"], dados["quantidade"]))
            cur.execute("INSERT INTO transacoes (tipo_transacao) VALUES ('entry') RETURNING id")
            trans_id = cur.fetchone()[0]
            cur.execute("INSERT INTO itens_transacionados (id_transacao, id_produto, quantidade, preco) VALUES (%s, %s, %s, %s)",
                        (trans_id, dados["id_produto"], dados["quantidade"], dados["valor"]))
            atualizar_estoque(cur, dados["id_produto"], dados["quantidade"], "entry")
            conexao.commit()
            print(f"{dados['quantidade']} unidades do produto {dados['id_produto']} adicionadas ao estoque.")
    except Exception as e:
        print(f"Erro ao processar lote: {e}")
        conexao.rollback()

def buscar_produto(conexao, id_produto):
    try:
        with conexao.cursor() as cur:
            cur.execute("""
                SELECT p.id, p.nome, p.preco, COALESCE(s.quantidade, 0)
                FROM produtos p
                JOIN estoque s ON s.id_produto = p.id
                WHERE p.id = %s
            """, (id_produto,))
            res = cur.fetchone()
            if res:
                return {"id": res[0], "nome": res[1], "preco": res[2], "estoque": res[3]}
            return None
    except Exception as e:
        print(f"Erro ao buscar produto: {e}")
        return None

def extrair_valor_arrecadacao(codigo):
    digitos = re.sub(r'\D', '', codigo)
    if not is_febraban(codigo):
        return None
    try:
        return Decimal(digitos[4:15]) / 100
    except:
        return None

def processo_checkout(conexao):
    total = Decimal("0.00")
    produtos = []
    contas = []
    try:
        with conexao.cursor() as cur:
            cur.execute("INSERT INTO transacoes (tipo_transacao) VALUES ('checkout') RETURNING id")
            trans_id = cur.fetchone()[0]

            while True:
                codigo = input("Digite ou escaneie o código (FIM para encerrar): ").strip()
                if codigo.upper() == "FIM":
                    break

                if is_febraban(codigo):
                    valor = extrair_valor_arrecadacao(codigo)
                    if valor is None:
                        print("Código FEBRABAN inválido.")
                        continue
                    contas.append(codigo)
                    total += valor
                    print(f"[Conta] Valor: R$ {valor:.2f}")
                    continue

                dados = parse_codigo_lote_customizado(codigo)
                if dados:
                    produto = buscar_produto(conexao, dados["id_produto"])
                    if not produto:
                        print("Produto não encontrado.")
                        continue
                    if produto["estoque"] <= 0:
                        print(f"Produto '{produto['nome']}' sem estoque.")
                        continue
                    cur.execute("""
                        INSERT INTO itens_transacionados (id_transacao, id_produto, quantidade, preco)
                        VALUES (%s, %s, 1, %s)
                    """, (trans_id, produto["id"], produto["preco"]))
                    total += produto["preco"]
                    produtos.append((produto["nome"], produto["preco"]))
                    print(f"[Produto] {produto['nome']} | R$ {produto['preco']:.2f}")
                else:
                    print("Formato de código inválido.")
            conexao.commit()
    except Exception as e:
        print(f"Falha no checkout: {e}")
        conexao.rollback()

    print("\n--- RESUMO DA COMPRA ---")
    for nome, valor in produtos:
        print(f"{nome}: R$ {valor:.2f}")
    for conta in contas:
        print(f"Conta FEBRABAN: {conta}")
    print(f"\nTOTAL A PAGAR: R$ {total:.2f}")

def menu(conexao):
    while True:
        print("\n======= SUPERMERCADO =======")
        tabela_menu = PrettyTable()
        tabela_menu.field_names = ["Opção", "Descrição"]
        tabela_menu.align = "l"
        tabela_menu.add_row(["1", "Receber Material"])
        tabela_menu.add_row(["2", "Fazer Checkout"])
        tabela_menu.add_row(["3", "Criar Produto"])
        tabela_menu.add_row(["4", "Listar Produtos"])
        tabela_menu.add_row(["5", "Sair"])

        print(tabela_menu)
        print("======= SUPERMERCADO =======\n")

        opcao = input("Escolha uma opção: ").strip()
        if opcao == "1":
            adicionar_estoque(conexao)
        elif opcao == "2":
            processo_checkout(conexao)
        elif opcao == "3":
            criar_produto(conexao)
        elif opcao == "4":
            listar_produtos(conexao)
        elif opcao == "5":
            print("Saindo do sistema. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")

def listar_produtos(conexao):
    try:
        with conexao.cursor() as cur:
            cur.execute("""
                SELECT p.id, p.nome, p.codigo, p.preco, COALESCE(s.quantidade, 0)
                FROM produtos p
                LEFT JOIN estoque s ON s.id_produto = p.id
                ORDER BY p.nome
            """)
            produtos = cur.fetchall()

            tabela = PrettyTable()
            tabela.field_names = ["ID", "Nome", "Código", "Preço (R$)", "Estoque"]

            for prod in produtos:
                tabela.add_row([prod[0], prod[1], prod[2], f"{prod[3]:.2f}", prod[4]])

            print(tabela)

    except Exception as e:
        print(f"Erro ao listar produtos: {e}")

def criar_produto(conexao):
    try:
        nome = input("Nome do produto: ").strip()
        codigo = input("Código do produto (ex: 7891234567890): ").strip()
        preco = Decimal(input("Preço do produto (ex: 5.99): ").strip())
        nome_segmento = input("Nome do segmento (ex: Alimentos): ").strip()
        nome_fornecedor = input("Nome do fornecedor: ").strip()
        cnpj = input("CNPJ do fornecedor (somente números): ").strip()

        with conexao.cursor() as cur:
            # Verifica ou cria segmento
            cur.execute("SELECT id FROM segmentos WHERE nome = %s", (nome_segmento,))
            seg = cur.fetchone()
            if seg:
                id_segmento = seg[0]
            else:
                cur.execute("INSERT INTO segmentos (nome) VALUES (%s) RETURNING id", (nome_segmento,))
                id_segmento = cur.fetchone()[0]
                print(f"Segmento '{nome_segmento}' criado.")

            # Verifica ou cria fornecedor
            cur.execute("SELECT id FROM fornecedores WHERE cnpj = %s", (cnpj,))
            fornecedor = cur.fetchone()
            if fornecedor:
                id_fornecedor = fornecedor[0]
            else:
                cur.execute("""
                    INSERT INTO fornecedores (nome, id_segmento, cnpj)
                    VALUES (%s, %s, %s) RETURNING id
                """, (nome_fornecedor, id_segmento, cnpj))
                id_fornecedor = cur.fetchone()[0]
                print(f"Fornecedor '{nome_fornecedor}' criado.")

            # Verifica se o produto já existe
            cur.execute("SELECT id FROM produtos WHERE codigo = %s", (codigo,))
            if cur.fetchone():
                print("Produto com este código já existe.")
                return

            # Cria o produto e o estoque
            cur.execute("""
                INSERT INTO produtos (codigo, nome, preco, id_empresa)
                VALUES (%s, %s, %s, %s) RETURNING id
            """, (codigo, nome, preco, id_fornecedor))
            id_produto = cur.fetchone()[0]
            cur.execute("INSERT INTO estoque (id_produto, quantidade) VALUES (%s, 0)", (id_produto,))
            conexao.commit()
            print(f"Produto '{nome}' cadastrado com sucesso.")
    except Exception as e:
        print(f"Erro ao criar produto: {e}")
        conexao.rollback()

if __name__ == "__main__":
    conexao = get_connection()
    if conexao:
        try:
            menu(conexao)
        finally:
            conexao.close()
            print("Conexão com o banco encerrada.")