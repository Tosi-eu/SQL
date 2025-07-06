import json
import os
import re
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import psycopg2.extras
from decimal import Decimal
import datetime
from colorama import init, Fore, Style
import pandas as pd

init(autoreset=True)

def info(msg): print(f"{Fore.LIGHTYELLOW_EX}[INFO]{Style.RESET_ALL} {msg}")
def sucesso(msg): print(f"{Fore.GREEN}[SUCESSO]{Style.RESET_ALL} {msg}")
def erro(msg): print(f"{Fore.RED}[ERRO]{Style.RESET_ALL} {msg}")
def input_info(prompt): return input(f"{Fore.LIGHTYELLOW_EX}[INFO]{Style.RESET_ALL} {prompt}")

"""

Entra no banco padrão do postgres, troca o level de isolamento para permitir operações sem commit e rollback, cria o banco principal e fecha conexão.
Conecta no banco criado, cria a tabela e popula algumas com dados.

"""
def get_connection():
    try:
        temp_conn = psycopg2.connect(
            dbname='postgres', #não mexe
            user='postgres', #não mexe
            password='postgres_Eu12', #sua senha
            host='localhost', #não mexe
            port=5432 #não mexe
        )
        temp_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT) #permite transação sem commit ou rollback
        temp_cursor = temp_conn.cursor()

        temp_cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'market'")
        if not temp_cursor.fetchone():
            temp_cursor.execute("CREATE DATABASE market")
            sucesso("Banco de dados 'market' criado.")
        temp_cursor.close()
        temp_conn.close()

        conn = psycopg2.connect(
            dbname='market', #não mexe
            user='postgres', #se você alterou user em cima, use o mesmo aqui
            password='postgres_Eu12', #sua senha
            host='localhost', #nao mexe
            port=5432 #nao mexe
        )
        info("Conectado ao banco 'market'.")

        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'products'
                )
            """)
            if not cur.fetchone()[0]:
                schema_path = os.path.join(os.getcwd(), "schema.sql")
                with open(schema_path, "r", encoding="utf-8") as f:
                    cur.execute(f.read())
                conn.commit()
                sucesso("Schema criado com sucesso.")
            else:
                info("Schema já existe.")
        return conn
    except Exception as e:
        erro(f"Erro ao conectar ou configurar o banco: {e}")
        return None

"""

necessário para fazer auditoria. Os tipos do python não são os mesmos do postgres, especialmente Decimal e datetime,
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
    """, (table, operation, psycopg2.extras.Json(json_data)))

"""

verifica se o código é febraban e se for, extrai cada parte de dentro dele

"""
def parse_febraban_code(code):
    digits = re.sub(r'\D', '', code)
    if len(digits) != 44 or not digits.startswith('86'):
        erro("Código inválido (esperado padrão FEBRABAN de 44 dígitos iniciando com 86).")
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
        erro(f"Erro ao interpretar FEBRABAN: {e}")
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
        erro(f"Erro ao interpretar código customizado: {e}")
        return None

"""

Verfica e interpreta um código de produto no formato: <id_produto><id_empresa><id_segmento>
Exemplo: 001002003

"""
def parse_custom_product_code(code):
    match = re.fullmatch(r'(\d{3})(\d{3})(\d{3})', code)
    if not match:
        return None
    try:
        return {
            "product_id": int(match.group(1)),
            "supplier_id": int(match.group(2)),
            "segment_id": int(match.group(3))
        }
    except Exception as e:
        erro(f"Erro ao interpretar código de produto customizado: {e}")
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
        erro("Lote inválido ou vencido.")
        return

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM segments WHERE id = %s", (data["segment_id"],))
            if not cur.fetchone():
                cur.execute("INSERT INTO segments (id, name) VALUES (%s, %s)", (data["segment_id"], f"Segment {data['segment_id']}"))
                make_audit(cur, "segments", "INSERT", data)

            cur.execute("SELECT id FROM suppliers WHERE cnpj LIKE %s", (data["cnpj8"] + '%',))
            row = cur.fetchone()
            if row:
                company_id = row[0]
            else:
                cur.execute("INSERT INTO suppliers (name, segment_id, cnpj) VALUES (%s, %s, %s) RETURNING id",
                            (f"Company {data['cnpj8']}", data["segment_id"], data["cnpj8"] + "000000"))
                company_id = cur.fetchone()[0]
                make_audit(cur, "suppliers", "INSERT", data)

            cur.execute("SELECT id FROM products WHERE id = %s", (data["product_id"],))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO products (id, code, name, price, company_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    data["product_id"],
                    str(data["product_id"]).zfill(13),
                    f"Product {data['product_id']}",
                    data["price"],
                    company_id
                ))
                cur.execute("INSERT INTO stock (product_id, quantity) VALUES (%s, 0)", (data["product_id"],))
                make_audit(cur, "products", "INSERT", data)

            cur.execute("SELECT id FROM lots WHERE code = %s", (code,))
            if cur.fetchone():
                erro("Este lote já foi registrado.")
                return

            cur.execute("INSERT INTO lots (code, product_id, quantity, validity) VALUES (%s, %s, %s, %s)",
                        (code, data["product_id"], data["amount"], data["validity"]))
            make_audit(cur, "lots", "INSERT", data)

            cur.execute("INSERT INTO transactions (transaction_type) VALUES ('entry') RETURNING id")
            trans_id = cur.fetchone()[0]
            cur.execute("""
                INSERT INTO transaction_items (transaction_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (trans_id, data["product_id"], data["amount"], data["price"]))
            make_audit(cur, "transaction_items", "INSERT", data)

            update_stock(cur, data["product_id"], data["amount"], "entry")
            conn.commit()
            sucesso(f"{data['amount']} unidades adicionadas ao estoque do produto {data['product_id']}")
    except Exception as e:
        erro(f"Erro ao adicionar estoque: {e}")
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
            cur.execute("INSERT INTO transactions (transaction_type) VALUES ('checkout') RETURNING id")
            trans_id = cur.fetchone()[0]

            while True:
                code = input_info("Escaneie o produto ou lote (ou 'FIM'): ").strip()
                if code.upper() == "FIM":
                    break

                data = None
                product_supplier_id = None

                if code.startswith("LOTE"):
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

                else:
                    parsed = parse_custom_product_code(code)
                    if parsed:
                        cur.execute("""
                            SELECT id FROM product_supplier
                            WHERE product_id = %s AND supplier_id = %s AND segment_id = %s
                        """, (parsed["product_id"], parsed["supplier_id"], parsed["segment_id"]))
                        row = cur.fetchone()
                        product_supplier_id = row[0] if row else None

                if not product_supplier_id:
                    erro("Produto não encontrado.")
                    continue

                produto = fetch_product(conn, product_supplier_id)
                if not produto or produto["stock"] <= 0:
                    erro(f"Produto sem estoque ou inválido.")
                    continue

                cur.execute("""
                    INSERT INTO transaction_items (transaction_id, product_id, quantity, price)
                    VALUES (%s, %s, 1, %s)
                """, (trans_id, produto["id"], produto["price"]))
                total += produto["price"]
                itens.append((produto["name"], produto["price"]))
                vendidos.append((produto["id"], 1))
                sucesso(f"[Produto] {produto['name']} | R$ {produto['price']:.2f}")

            for prod_id, qtd in vendidos:
                update_stock(cur, prod_id, qtd, "checkout")
            conn.commit()

    except Exception as e:
        erro(f"Erro no checkout: {e}")
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
                select p.name as nome, pe.code as codigo_produto, pe.price as preço, s.quantity as estoque, l.validity as validade from product_supplier pe
                join products p on pe.product_id = p.id
                left join lots l on l.product_id = p.id
                left join stock s on s.product_id = pe.id
                order by s.quantity desc, l.validity desc;
            """)
            cols = [d[0] for d in cur.description]
            df = pd.DataFrame(cur.fetchall(), columns=cols)
        print("\nProdutos disponíveis:\n")
        print(df.to_string(index=False))
    except Exception as e:
        erro(f"Erro ao listar produtos: {e}")

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
                cur.execute("INSERT INTO segments (name) VALUES (%s) RETURNING id", (segment_name,))
                segment_id = cur.fetchone()[0]
                make_audit(cur, "segments", "INSERT", {"name": segment_name})

            # Supplier
            cur.execute("SELECT id FROM suppliers WHERE cnpj = %s", (cnpj,))
            row = cur.fetchone()
            if row:
                supplier_id = row[0]
            else:
                cur.execute("INSERT INTO suppliers (name, cnpj) VALUES (%s, %s) RETURNING id",
                            (supplier_name, cnpj))
                supplier_id = cur.fetchone()[0]
                make_audit(cur, "suppliers", "INSERT", {"name": supplier_name, "cnpj": cnpj})

            cur.execute("SELECT id FROM products WHERE name ILIKE %s", (name,))
            if cur.fetchone():
                erro("Já existe um produto com esse nome!")
                return

            cur.execute("INSERT INTO products (name) VALUES (%s) RETURNING id", (name,))
            product_id = cur.fetchone()[0]
            make_audit(cur, "products", "INSERT", {"name": name})

            # Product-Supplier
            code = f"PROD{product_id:03d}{supplier_id:03d}{segment_id:03d}"
            cur.execute("""
                INSERT INTO product_supplier (product_id, supplier_id, segment_id, price, code)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (product_id, supplier_id, segment_id, price, code))
            product_supplier_id = cur.fetchone()[0]
            make_audit(cur, "product_supplier", "INSERT", {"product_id": product_id, "supplier_id": supplier_id})

            # Stock
            cur.execute("INSERT INTO stock (product_id, quantity) VALUES (%s, 0)", (product_supplier_id,))
            make_audit(cur, "stock", "INSERT", {"product_id": product_supplier_id, "quantity": 0})

            conn.commit()
            sucesso(f"Produto '{name}' criado com o código '{code}'.")

    except Exception as e:
        erro(f"Erro criado produto: {e}")
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
            erro("Opção inválida.")

if __name__ == "__main__":
    conn = get_connection()
    if conn:
        try:
            menu(conn)
        finally:
            conn.close()
            info("Conexão encerrada.")
