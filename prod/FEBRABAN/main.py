import os
import re
import pandas as pd
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import datetime
from decimal import Decimal
from colorama import init, Fore, Style
import psycopg2.extras

# Inicializa o colorama para usar cores no terminal
init(autoreset=True)

# Funções para deixar o terminal colorido
def info(msg): print(f"{Fore.LIGHTYELLOW_EX}[INFO]{Style.RESET_ALL} {msg}")
def sucesso(msg): print(f"{Fore.GREEN}[SUCESSO]{Style.RESET_ALL} {msg}")
def erro(msg): print(f"{Fore.RED}[ERRO]{Style.RESET_ALL} {msg}")
def input_info(prompt): return input(f"{Fore.LIGHTYELLOW_EX}[INFO]{Style.RESET_ALL} {prompt}")

"""

conecta no banco padrão do postgres, cria o banco supermercado, fecha a conexão com o banco postgres
e abre conexão com o banco supermercado e enecerra populando algumas tabelas

"""
def get_connection():
    try:
        temp_connection = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='postgres_Eu12',
            host='localhost',
            port=5432
        )
        temp_connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        temp_cursor = temp_connection.cursor()

        temp_cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'supermercado'")
        banco_existe = temp_cursor.fetchone()
        if not banco_existe:
            temp_cursor.execute("CREATE DATABASE supermercado")
            print("Banco de dados 'supermercado' criado.")
        else:
            print("Banco de dados 'supermercado' já existe.")

        temp_cursor.close()
        temp_connection.close()

        connection = psycopg2.connect(
            dbname='supermercado',
            user='postgres',
            password='postgres_Eu12',
            host='localhost',
            port=5432
        )
        print("Conectado ao banco 'supermercado'.")

        with connection.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'products'
                )
            """)
            tabela_existe = cur.fetchone()[0]

            if not tabela_existe:
                caminho_schema = os.path.join(os.getcwd(), "schema.sql")
                with open(caminho_schema, "r", encoding="utf-8") as arquivo:
                    sql = arquivo.read()
                    cur.execute(sql)
                connection.commit()
                print("Script 'schema.sql' executado com sucesso.")
            else:
                print("Tabelas já existem. Pulando execução do 'schema.sql'.")

        return connection
    except psycopg2.Error as e:
        print(f"Erro ao conectar ou configurar o banco: {e}")
        return None

"""

para fins de auditoria, sempre que qualquer operação é realizada, essa tabela é populada com alguns dados:

- que tabela foi alterada

- que operacao foi realizada

- o que mudou

"""
def make_audit(cur, table, operacao, dados):
    cur.execute("""
        INSERT INTO audit_log(table_name, operation, changed_data)
        VALUES (%s, %s, %s)
    """, (table, operacao, psycopg2.extras.Json(dados)))

"""

pega um código de barras FEBRABAN e extrai os dados dele

"""
def parse_febraban_code(code):
    digits = re.sub(r'\D', '', code)
    print(len(digits))
    if len(digits) != 44 or not digits.startswith('86'):
        erro("Código inválido. Deve conter 44 dígitos e iniciar com 86.")
        return None
    try:
        price = Decimal(digits[4:15]) / 100
        cnpj8 = digits[15:23]
        campo_livre = digits[23:]
        validade = datetime.datetime.strptime(campo_livre[0:8], "%Y%m%d").date()
        segmento_id = int(campo_livre[8:10])
        product_id = int(campo_livre[10:13])
        amount = int(campo_livre[13:18])
        return {
            "price": price,
            "cnpj8": cnpj8,
            "validade": validade,
            "segmento_id": segmento_id,
            "product_id": product_id,
            "amount": amount,
        }
    except Exception as e:
        erro(f"Falha ao interpretar código FEBRABAN: {e}")
        return None

"""

recebe um código e extrai as partes no formato customizado

"""
def parse_custom_code(code):
    match = re.fullmatch(r'LOTE(\d{3})(\d{3})(\d{3})(\d{8})(\d{5})(\d{7})(\d{8})', code)
    if not match:
        return None
    try:
        return {
            "product_id": int(match.group(1)),
            "empresa_id": int(match.group(2)),
            "segmento_id": int(match.group(3)),
            "validade": datetime.datetime.strptime(match.group(4), "%Y%m%d").date(),
            "amount": int(match.group(5)),
            "price": Decimal(match.group(6)) / 100,
            "cnpj8": match.group(7),
        }
    except Exception as e:
        erro(f"Erro ao interpretar código customizado de lote: {e}")
        return None

"""

atualiza o estoque somando ou subtraindo quantidade, dependendo se é entrada ou saída

"""
def update_stock(cur, product_id, amount, op_type):
    if op_type == 'entry':
        cur.execute("UPDATE stock SET quantity = quantity + %s WHERE product_id = %s", (amount, product_id))
    else:
        cur.execute("UPDATE stock SET quantity = quantity - %s WHERE product_id = %s", (amount, product_id))
        cur.execute("SELECT quantity FROM stock WHERE product_id = %s", (product_id,))
        amount = cur.fetchone()
        if amount and amount[0] < 0:
            raise Exception(f"Estoque insuficiente para o product ID {product_id}")

"""

recebe o código febraban ou customizado, e processa a entrada de material no sistema

"""
def adicionar_estoque(conn):
    barcode = input_info("Escaneie o código de barras do lote: ").strip()
    parsed = parse_custom_code(barcode) if barcode.startswith('LOTE') else parse_febraban_code(barcode)

    if not parsed:
        erro("Código inválido. Não segue padrão FEBRABAN nem lote customizado.")
        return
    if parsed["validade"] < datetime.date.today():
        erro("Produto vencido. Entrada não permitida.")
        return
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM segments WHERE id = %s", (parsed["segmento_id"],))
            if not cur.fetchone():
                cur.execute("INSERT INTO segments (id, name) VALUES (%s, %s)", (parsed["segmento_id"], f"Segmento {parsed['segmento_id']}"))
                make_audit(cur, "segments", "INSERT", {"id": parsed["segmento_id"]})

            cur.execute("SELECT id FROM companies WHERE cnpj LIKE %s", (parsed["cnpj8"] + '%',))
            row = cur.fetchone()
            company_id = row[0] if row else None
            if not company_id:
                cur.execute("INSERT INTO companies (name, segment_id, cnpj) VALUES (%s, %s, %s) RETURNING id",
                            (f"Empresa {parsed['cnpj8']}", parsed["segmento_id"], parsed["cnpj8"] + "000000"))
                company_id = cur.fetchone()[0]
                make_audit(cur, "companies", "INSERT", {"id": company_id})

            cur.execute("SELECT id FROM products WHERE id = %s", (parsed["product_id"],))
            if not cur.fetchone():
                cur.execute("INSERT INTO products (id, code, name, price, company_id) VALUES (%s, %s, %s, %s, %s)",
                            (parsed["product_id"], str(parsed["product_id"]).zfill(13), f"Produto {parsed['product_id']}", parsed["price"], company_id))
                cur.execute("INSERT INTO stock (product_id, quantity) VALUES (%s, 0)", (parsed["product_id"],))
                make_audit(cur, "products", "INSERT", {"id": parsed["product_id"]})

            cur.execute("SELECT id FROM lots WHERE lot_code = %s", (barcode,))
            if cur.fetchone():
                erro("Este lote já foi registrado anteriormente.")
                return

            cur.execute("INSERT INTO lots (lot_code, product_id, quantity) VALUES (%s, %s, %s)",
                        (barcode, parsed["product_id"], parsed["amount"]))
            make_audit(cur, "lots", "INSERT", {"lot_code": barcode})

            cur.execute("INSERT INTO transactions (transaction_type) VALUES ('entry') RETURNING id")
            trans_id = cur.fetchone()[0]
            cur.execute("INSERT INTO transaction_items (transaction_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                        (trans_id, parsed["product_id"], parsed["amount"], parsed["price"]))
            make_audit(cur, "transaction_items", "INSERT", {"product_id": parsed["product_id"]})

            update_stock(cur, parsed["product_id"], parsed["amount"], "entry")
            conn.commit()
            sucesso(f"{parsed['amount']} unidades do produto {parsed['product_id']} adicionadas ao estoque.")
    except Exception as e:
        erro(f"Erro ao processar lote: {e}")
        conn.rollback()

"""

procura no banco se o produto existe, buscando pelo seu id. Se existir, traz

- id do produto
- nome do produto
- preço
- estoque

"""
def fetch_product(conn, product_id):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.id, p.name, p.price, COALESCE(s.quantity, 0)
                FROM products p
                LEFT JOIN stock s ON s.product_id = p.id
                WHERE p.id = %s
            """, (product_id,))
            data = cur.fetchone()
            if data:
                return {"id": data[0], "name": data[1], "price": data[2], "stock": data[3]}
            return None
    except Exception as e:
        erro(f"Erro ao buscar produto: {e}")
        return None

"""

extrai o valor do produto de um código FEBRABAN (do dígito 5 ao 15)

"""
def extract_product_value_in_lot(code):
    digits = re.sub(r'\D', '', code)
    if len(digits) != 44:
        return None
    try:
        return Decimal(digits[4:15]) / 100
    except:
        return None

"""

Realiza o processo de checkout:

- Aceita códigos de produto (custom ou FEBRABAN)

- Registra a venda em 'transactions' e 'transaction_items'

- Verifica se o produto existe e possui estoque

- Atualiza o total da compra

- Encerra operação se digitar FIM (maiúsculo ou não)

"""
def make_checkout(conn):
    checkout = Decimal("0.00")
    produtos = []

    try:
        with conn.cursor() as cur:
            # Cria uma nova transação do tipo 'checkout'
            cur.execute("INSERT INTO transactions (transaction_type) VALUES ('checkout') RETURNING id")
            trans_id = cur.fetchone()[0]

            while True:
                code = input_info("Digite ou escaneie o código (FIM para encerrar): ").strip()
                if code.upper() == "FIM":
                    break

                parsed = None
                if code.startswith("LOTE"):
                    parsed = parse_custom_code(code)
                elif len(code) == 44 and code.startswith("86"):
                    parsed = parse_febraban_code(code)

                if parsed:
                    product = fetch_product(conn, parsed["product_id"])
                    if not product:
                        erro("Produto não encontrado.")
                        continue
                    if product["stock"] <= 0:
                        erro(f"Produto '{product['name']}' sem estoque.")
                        continue

                    cur.execute("""
                        INSERT INTO transaction_items (transaction_id, product_id, quantity, price)
                        VALUES (%s, %s, 1, %s)
                    """, (trans_id, product["id"], product["price"]))

                    checkout += product["price"]
                    produtos.append((product["name"], product["price"]))
                    sucesso(f"[Produto] {product['name']} | R$ {product['price']:.2f}")
                else:
                    erro("Código inválido. Formato não reconhecido.")
            conn.commit()

    except Exception as e:
        erro(f"Falha no checkout: {e}")
        conn.rollback()

    print(Fore.GREEN + "\n--- RESUMO DA COMPRA ---")
    for name, price in produtos:
        print(f"{name}: R$ {price:.2f}")
    print(Fore.GREEN + f"\nTOTAL A PAGAR: R$ {checkout:.2f}")

"""

faz um select de todos os produtos com ou sem estoque e os lista, exibindo como tabela.

"""
def list_products(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.id, p.name AS nome, p.code AS código, p.price AS preco, COALESCE(s.quantity, 0) AS estoque
                FROM products p
                LEFT JOIN stock s ON s.product_id = p.id
                ORDER BY p.name
            """)
            colnames = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

        df = pd.DataFrame(rows, columns=colnames)
        print("\nProdutos disponíveis:\n")
        print(df.to_string(index=False))
    except Exception as e:
        erro(f"Falha ao listar produtos: {e}")

"""

menu principal com as opções do sistema

"""
def menu(conn):
    while True:
        print(Fore.GREEN + "\n===== SISTEMA DO SUPERMERCADO =====")
        print("1 - Receber Material")
        print("2 - Fazer Checkout")
        print("3 - Listar Produtos")
        print("4 - Sair")
        print(Fore.GREEN + "===================================\n")

        opcao = input_info("Escolha uma opção: ").strip()
        if opcao == "1":
            adicionar_estoque(conn)
        elif opcao == "2":
            make_checkout(conn)
        elif opcao == "3":
            list_products(conn)
        elif opcao == "4":
            info("Saindo do sistema. Até logo!")
            break
        else:
            erro("Opção inválida. Tente novamente.")

conn = get_connection()
if conn:
    try:
        menu(conn)
    finally:
        conn.close()
        info("Conexão com o banco encerrada.")