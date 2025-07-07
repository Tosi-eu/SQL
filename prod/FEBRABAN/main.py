import json
import os
import re
import mysql.connector
from mysql.connector import errorcode
from decimal import Decimal
import datetime
from colorama import init, Fore, Style
import pandas as pd

init(autoreset=True)

def info(msg): print(f"{Fore.LIGHTYELLOW_EX}[INFO]{Style.RESET_ALL} {msg}")
def success(msg): print(f"{Fore.GREEN}[SUCESSO]{Style.RESET_ALL} {msg}")
def error(msg): print(f"{Fore.RED}[ERRO]{Style.RESET_ALL} {msg}")
def input_info(prompt): return input(f"{Fore.LIGHTYELLOW_EX}[INFO]{Style.RESET_ALL} {prompt}")

"""

Entra no banco padrão do mysql, troca o level de isolamento para permitir operações sem commit e rollback, cria o banco principal e fecha conexão.
Conecta no banco criado, cria a tabela e popula algumas com dados.

"""
def get_connection():
    try:
        temp_conn = mysql.connector.connect(
            user='root', #seu usuario
            password='root', #sua usuario
            host='localhost' #nao mexe
        )
        temp_conn.autocommit = True
        temp_cursor = temp_conn.cursor()

        temp_cursor.execute("CREATE DATABASE IF NOT EXISTS market")
        success("Banco de dados 'market' verificado/criado.")
        temp_cursor.close()
        temp_conn.close()

        conn = mysql.connector.connect(
            user='root', #seu usuario
            password='root', # sua senha
            host='localhost', # mao mexe
            database='market' # nao mexe
        )
        info("Conectado ao banco 'market'.")

        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'market' AND table_name = 'products'
        """)
        if cur.fetchone()[0] == 0:
            schema_path = os.path.join(os.getcwd(), "schema.sql")
            with open(schema_path, "r", encoding="utf-8") as f:
                cur.execute("SET FOREIGN_KEY_CHECKS = 0;")  
                for statement in f.read().split(";"):
                    if statement.strip():
                        cur.execute(statement)
            conn.commit()
            success("Schema criado com sucesso.")
        else:
            info("Schema já existe.")
        cur.close()
        return conn

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            error("Usuário ou senha inválidos.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            error("Banco de dados inexistente.")
        else:
            error(err)
        return None
"""

necessário para fazer auditoria. Os tipos do python não são os mesmos do mysql, especialmente Decimal e datetime,
então converte Decimal para float e datetime para string

"""
def convert_for_json(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    return str(obj) 

"""

a cada operação no banco, de qualquer natureza, em qualquer tabela, essa tabela é populada com:

- que tabela foi alterada
- o que foi feito
- o que mudou

"""
def make_audit(cur, table, operation, data):
    json_data = json.loads(json.dumps(data, default=convert_for_json))
    cur.execute("""
        INSERT INTO audit_log (table_name, operation, changed_data)
        VALUES (%s, %s, %s)
    """, (table, operation, json.dumps(json_data)))
"""

verifica se o código é febraban e se for, extrai cada parte de dentro dele

"""
def parse_febraban_code(code):
    digits = re.sub(r'\D', '', code)
    if len(digits) != 44 or not digits.startswith('86'):
        error("Código inválido (esperado padrão FEBRABAN de 44 dígitos iniciando com 86).")
        return None
    try:
        return {
            "price": Decimal(digits[4:15]) / 100,
            "cnpj8": digits[15:23],
            "validity": datetime.datetime.strptime(digits[23:31], "%Y%m%d").date(),
            "segment_id": int(digits[31:33]),
            "product_id": int(digits[33:36]),
            "amount": int(digits[36:41])
        }
    except Exception as e:
        error(f"Erro ao interpretar FEBRABAN: {e}")
        return None

"""

verifica se o código do lote é o código personalizado, e se for, extrai e retorna os campos na forma de um dicionário

"""
def parse_custom_lot_code(code):
    match = re.fullmatch(r'RECEIVE(\d{3})(\d{3})(\d{3})(\d{8})(\d{5})(\d{7})(\d{8})', code)
    if not match:
        return None
    try:
        return {
            "product_id": int(match.group(1)),
            "company_id": int(match.group(2)),
            "segment_id": int(match.group(3)),
            "validity": datetime.datetime.strptime(match.group(4), "%Y%m%d").date(),
            "amount": int(match.group(5)),
            "price": Decimal(match.group(6)) / 100,
            "cnpj8": match.group(7)
        }
    except Exception as e:
        error(f"Erro ao interpretar código customizado: {e}")
        return None

"""

A cada interação com recebimento de lote ou saida de produto, é necessário atualizar estoque

- se for recebimento de lote, atualiza o estoque do produto com a quantidade N que está no código do lote
- se for checkout, atualiza o estoque decrementando em 1 o estoque do produto

"""
def update_stock(cur, product_id, amount, op_type):
    if op_type == 'entry':
        cur.execute("UPDATE stock SET quantity = quantity + %s WHERE product_id = %s", (amount, product_id))
    else:
        cur.execute("UPDATE stock SET quantity = quantity - %s WHERE product_id = %s", (amount, product_id))
        cur.execute("SELECT quantity FROM stock WHERE product_id = %s", (product_id,))
        new_qty = cur.fetchone()
        if new_qty and new_qty[0] < 0:
            raise Exception(f"Estoque insuficiente para o produto ID {product_id}")

"""
pega um código de barras FEBRABAN  e extrai as partes, no formato

Posição	       Significado	      Valor
01	            Produto	            8
02	            Segmento	        6
03	            Tipo de valor	    8
04	            Dígito Verificador  6
05 a 15	        Valor (R$6,99)	    00000000990
16 a 23	        CNPJ Nestlé         11111111
24 a 31	        Data validade       20251230
32 a 33	        Segmento	        01
34 a 36	        Produto ID 	        001
37 a 41	        Quantidade	        00010
42 a 44	        Ajuste	            000

"""
def fill_stock(conn):
    code = input_info("Digite o código do lote (FEBRABAN ou customizado): ").strip()
    data = parse_custom_lot_code(code) if code.startswith("RECEIVE") else parse_febraban_code(code)

    if not data or data["validity"] < datetime.date.today():
        error("Lote inválido ou vencido.")
        return

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM segments WHERE id = %s", (data["segment_id"],))
            if not cur.fetchone():
                error("Segmento não existe!")
                return

            cur.execute("SELECT id FROM suppliers WHERE cnpj LIKE %s", (data["cnpj8"] + '%',))
            if not cur.fetchone():
                error("Fornecedor não existe!")
                return

            cur.execute("SELECT id FROM products WHERE id = %s", (data["product_id"],))
            if not cur.fetchone():
                error("Produto não existe!")
                return

            cur.execute("SELECT id FROM lots WHERE code = %s", (code,))
            if cur.fetchone():
                error("Este lote já foi registrado.")
                return
            
            cur.execute("SELECT id FROM suppliers WHERE cnpj LIKE %s", (data["cnpj8"] + '%',))
            row = cur.fetchone()
            if row:
                company_id = row[0]
            else:
                error("Fornecedor não existe!")
                return
                
            cur.execute("""
                SELECT id FROM product_supplier
                WHERE product_id = %s AND supplier_id = %s AND segment_id = %s
            """, (data["product_id"], company_id, data["segment_id"]))
            row = cur.fetchone()
            if row:
                ps_id = row[0]

            cur.execute("INSERT INTO lots (code, product_id, quantity, validity) VALUES (%s, %s, %s, %s)",
                        (code, data["product_id"], data["amount"], data["validity"]))
            make_audit(cur, "lots", "INSERT", data)

            cur.execute("INSERT INTO transactions (transaction_type) VALUES ('entry')")
            trans_id = cur.lastrowid
            cur.execute("""
                INSERT INTO transaction_items (transaction_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (trans_id, data["product_id"], data["amount"], data["price"]))
            make_audit(cur, "transaction_items", "INSERT", data)

            update_stock(cur, ps_id, data["amount"], "entry")
            conn.commit()
            success(f"{data['amount']} unidades adicionadas ao estoque do produto {data['product_id']}")
    except Exception as e:
        error(f"Erro ao adicionar estoque: {e}")
        conn.rollback()

"""

recebe o código do produto e faz uma busca completa para obter

- nome do produto
- preço do produto
- estoque do produto

"""
def fetch_product(conn, product_supplier_id):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT ps.id, p.name, ps.price, COALESCE(s.quantity, 0)
            FROM product_supplier ps
            JOIN products p ON p.id = ps.product_id
            LEFT JOIN stock s ON s.product_id = ps.id
            WHERE ps.id = %s
        """, (product_supplier_id,))
        r = cur.fetchone()
        if r:
            return {"id": r[0], "name": r[1], "price": r[2], "stock": r[3]}
        return None
    
def make_checkout(conn):
    total = Decimal("0.00")
    itens = []
    vendidos = []
    contas_febraban = set() 

    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO transactions (transaction_type) VALUES ('checkout')")
            trans_id = cur.lastrowid

            while True:
                code = input_info("Escaneie o produto ou lote (ou 'FIM'): ").strip()
                if code.upper() == "FIM":
                    break

                data = None
                product_supplier_id = None

                if code.startswith("RECEIVE"):
                    data = parse_custom_lot_code(code)
                    if data:
                        cur.execute("""
                            SELECT id FROM product_supplier
                            WHERE product_id = %s AND supplier_id = %s AND segment_id = %s
                        """, (data["product_id"], data["company_id"], data["segment_id"]))
                        row = cur.fetchone()
                        product_supplier_id = row[0] if row else None

                elif code.startswith("86") and len(code) == 44:
                    contas_febraban.add(code) 
                    data = parse_febraban_code(code)
                    if data:
                        cur.execute("""
                            SELECT ps.id
                            FROM product_supplier ps
                            JOIN suppliers s ON s.id = ps.supplier_id
                            WHERE ps.product_id = %s AND ps.segment_id = %s AND s.cnpj LIKE %s
                        """, (data["product_id"], data["segment_id"], data["cnpj8"] + '%'))
                        row = cur.fetchone()
                        product_supplier_id = row[0] if row else None

                elif code.startswith("PROD"):
                    cur.execute("SELECT id FROM product_supplier WHERE code = %s", (code,))
                    row = cur.fetchone()
                    product_supplier_id = row[0] if row else None

                else:
                    error("Código inválido.")
                    continue

                if not product_supplier_id:
                    error("Produto não encontrado.")
                    continue

                produto = fetch_product(conn, product_supplier_id)
                if not produto or produto["stock"] <= 0:
                    error(f"Produto sem estoque ou inválido.")
                    continue

                cur.execute("""
                    INSERT INTO transaction_items (transaction_id, product_id, quantity, price)
                    VALUES (%s, %s, 1, %s)
                """, (trans_id, produto["id"], produto["price"]))
                total += produto["price"]
                itens.append((produto["name"], produto["price"]))
                vendidos.append((produto["id"], 1))
                success(f"[Produto] {produto['name']} | R$ {produto['price']:.2f}")

            for prod_id, qtd in vendidos:
                update_stock(cur, prod_id, qtd, "checkout")
            conn.commit()

    except Exception as e:
        error(f"Erro no checkout: {e}")
        conn.rollback()

    if contas_febraban:
        print(Fore.CYAN + "\nCONTAS FEBRABAN UTILIZADAS\n")
        for conta in sorted(contas_febraban):
            print(f"→ {conta}")

    print(Fore.GREEN + "\nRESUMO DA COMPRA\n")
    for nome, _ in itens:
        print(f"→ {nome}")
    print(Fore.GREEN + f"\nTOTAL A PAGAR: R$ {total:.2f}")

"""

seleciona todos os produtos e os lista em forma de tabela, trazendo informações de produto
- nome
- codigo
- preco
- estoque (caso houver)
- validade (caso houver)

"""
def list_products(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    p.name AS nome,
                    pe.code AS codigo_produto,
                    pe.price AS preço,
                    s.quantity AS estoque,
                    l.validity AS validade
                FROM product_supplier pe
                JOIN products p ON pe.product_id = p.id
                LEFT JOIN lots l ON l.product_id = pe.id
                LEFT JOIN stock s ON s.product_id = pe.id
                ORDER BY s.quantity DESC, l.validity DESC;
            """)
            cols = [d[0] for d in cur.description]
            df = pd.DataFrame(cur.fetchall(), columns=cols)
        print("\nProdutos disponíveis:\n")
        print(df.to_string(index=False))
    except Exception as e:
        error(f"Erro ao listar produtos: {e}")

"""

Cria um novo produto no banco

- verifica se já existe produto com tal nome, se exisitr, cancela
- verifica se o segmento já existe, se não, cria
- verifica se o cnpj da empresa existe, se não, insere na tabela
- cria um estoque zerado do produto
- cria um código do produto, que pode ser usado no checkout


"""
def create_product(conn):
    try:
        name = input_info("Nome do Produto: ").strip()
        price = Decimal(input_info("Preço do Produto (ex: 4.99): ").strip())
        segment_name = input_info("Nome do Segmento: ").strip()
        supplier_name = input_info("Nome do Fornecedor: ").strip()
        cnpj = input_info("CNPJ do Fornecedor: ").strip()

        with conn.cursor() as cur:
            # Segment
            cur.execute("SELECT id FROM segments WHERE name = %s", (segment_name,))
            row = cur.fetchone()
            if row:
                segment_id = row[0]
            else:
                cur.execute("INSERT INTO segments (name) VALUES (%s)", (segment_name,))
                segment_id = cur.lastrowid
                make_audit(cur, "segments", "INSERT", {"name": segment_name})

            # Supplier
            cur.execute("SELECT id FROM suppliers WHERE cnpj = %s", (cnpj,))
            row = cur.fetchone()
            if row:
                supplier_id = row[0]
            else:
                cur.execute("INSERT INTO suppliers (name, cnpj) VALUES (%s, %s)",
                            (supplier_name, cnpj))
                supplier_id = cur.lastrowid
                make_audit(cur, "suppliers", "INSERT", {"name": supplier_name, "cnpj": cnpj})

            cur.execute("SELECT id FROM products WHERE LOWER(name) = LOWER(%s)", (name,))
            if cur.fetchone():
                error("Já existe um produto com esse nome!")
                return

            cur.execute("INSERT INTO products (name) VALUES (%s)", (name,))
            product_id = cur.lastrowid
            make_audit(cur, "products", "INSERT", {"name": name})

            # Product-Supplier
            code = f"PROD{product_id:03d}{supplier_id:03d}{segment_id:03d}"
            cur.execute("""
                INSERT INTO product_supplier (product_id, supplier_id, segment_id, price, code)
                VALUES (%s, %s, %s, %s, %s)
            """, (product_id, supplier_id, segment_id, price, code))
            product_supplier_id = cur.lastrowid
            make_audit(cur, "product_supplier", "INSERT", {"product_id": product_id, "supplier_id": supplier_id})

            # Stock
            cur.execute("INSERT INTO stock (product_id, quantity) VALUES (%s, 0)", (product_supplier_id,))
            make_audit(cur, "stock", "INSERT", {"product_id": product_supplier_id, "quantity": 0})

            conn.commit()
            success(f"Produto '{name}' criado com o código '{code}'.")

    except Exception as e:
        error(f"Erro criado produto: {e}")
        conn.rollback()

def menu(conn):
    while True:
        print(Fore.GREEN + "\n======= SUPERMARKET SYSTEM =======")
        print("     1 - Receber Lote")
        print("     2 - Checkout de Produtos")
        print("     3 - Listar Produtos")
        print("     4 - Criar Produto")
        print("     5 - Sair")
        print(Fore.GREEN + "==================================\n")

        op = input_info("Selecione uma opção: ").strip()
        if op == "1":
            fill_stock(conn)
        elif op == "2":
            make_checkout(conn)
        elif op == "3":
            list_products(conn)
        elif op == "4":
            create_product(conn)
        elif op == "5":
            info("Finalizando sistema.")
            break
        else:
            error("Opção inválida.")

if __name__ == "__main__":
    conn = get_connection()
    if conn:
        try:
            menu(conn)
        finally:
            conn.close()
            info("Conexão encerrada.")
