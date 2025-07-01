import os
import re
import psycopg2
import datetime
from decimal import Decimal
from colorama import init, Fore, Style

init(autoreset=True)

def info(msg): print(f"{Fore.LIGHTYELLOW_EX}[INFO]{Style.RESET_ALL} {msg}")
def sucesso(msg): print(f"{Fore.GREEN}[SUCESSO]{Style.RESET_ALL} {msg}")
def erro(msg): print(f"{Fore.RED}[ERRO]{Style.RESET_ALL} {msg}")
def input_info(prompt): return input(f"{Fore.LIGHTYELLOW_EX}[INFO]{Style.RESET_ALL} {prompt}")

def get_connection():
    try:
        conn = psycopg2.connect(
            dbname='supermercado',
            user='postgres',
            password='postgres_Eu12',
            host='localhost',
            port=5432
        )
        sucesso("Conexão com o banco estabelecida com sucesso.")
        return conn
    except psycopg2.Error as e:
        erro(f"Falha ao conectar ao banco: {e}")
        return None

def is_febraban(code):
    digits = re.sub(r'\D', '', code)
    return len(digits) == 44 and digits.startswith('8')

def parse_codigo_febraban(codigo):
    digits = re.sub(r'\D', '', codigo)
    print(len(digits))
    if not is_febraban(digits):
        erro("Código inválido. Deve conter 44 dígitos e iniciar com 8.")
        return None
    try:
        valor = Decimal(digits[4:15]) / 100
        cnpj8 = digits[15:23]
        campo_livre = digits[23:]
        validade = datetime.datetime.strptime(campo_livre[0:8], "%Y%m%d").date()
        segmento_id = int(campo_livre[8:10])
        produto_id = int(campo_livre[10:13])
        quantidade = int(campo_livre[13:18])
        return {
            "valor": valor,
            "cnpj8": cnpj8,
            "validade": validade,
            "segmento_id": segmento_id,
            "produto_id": produto_id,
            "quantidade": quantidade,
            "raw": digits
        }
    except Exception as e:
        erro(f"Falha ao interpretar código FEBRABAN: {e}")
        return None

def parse_codigo_customizado(code):
    match = re.fullmatch(r'PROD(\d{1,5})(\d{1,5})(\d{1,5})', code)
    if not match:
        return None
    return {
        "produto_id": int(match.group(1)),
        "empresa_id": int(match.group(2)),
        "segmento_id": int(match.group(3))
    }

def adicionar_estoque(conn):
    codigo_barras = input_info("Escaneie o código de barras do lote: ").strip()
    parsed = parse_codigo_febraban(codigo_barras)
    if not parsed:
        return

    if parsed["validade"] < datetime.date.today():
        erro("Produto vencido. Entrada não permitida.")
        return

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM segments WHERE id = %s", (parsed["segmento_id"],))
            if not cur.fetchone():
                cur.execute("INSERT INTO segments (id, name) VALUES (%s, %s)",
                            (parsed["segmento_id"], f"Segmento {parsed['segmento_id']}"))
                info(f"Segmento {parsed['segmento_id']} criado.")

            cur.execute("SELECT id FROM companies WHERE cnpj LIKE %s", (parsed["cnpj8"] + '%',))
            row = cur.fetchone()
            if row:
                company_id = row[0]
            else:
                cur.execute("INSERT INTO companies (name, segment_id, cnpj) VALUES (%s, %s, %s) RETURNING id",
                            (f"Empresa {parsed['cnpj8']}", parsed["segmento_id"], parsed["cnpj8"] + "000000"))
                company_id = cur.fetchone()[0]
                info(f"Empresa criada com CNPJ: {parsed['cnpj8']}")

            cur.execute("SELECT id FROM products WHERE id = %s", (parsed["produto_id"],))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO products (id, code, name, price, company_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (parsed["produto_id"], str(parsed["produto_id"]).zfill(13), f"Produto {parsed['produto_id']}", parsed["valor"], company_id))
                cur.execute("INSERT INTO stock (product_id, quantity) VALUES (%s, 0)", (parsed["produto_id"],))
                info(f"Produto {parsed['produto_id']} criado.")

            cur.execute("SELECT id FROM lots WHERE lot_code = %s", (codigo_barras,))
            if cur.fetchone():
                erro("Este lote já foi registrado anteriormente.")
                return

            cur.execute("INSERT INTO lots (lot_code, product_id, quantity) VALUES (%s, %s, %s)",
                        (codigo_barras, parsed["produto_id"], parsed["quantidade"]))
            cur.execute("INSERT INTO transactions (transaction_type) VALUES ('entry') RETURNING id")
            trans_id = cur.fetchone()[0]
            cur.execute("INSERT INTO transaction_items (transaction_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                        (trans_id, parsed["produto_id"], parsed["quantidade"], parsed["valor"]))
            conn.commit()
            sucesso(f"{parsed['quantidade']} unidades do produto {parsed['produto_id']} adicionadas ao estoque.")
    except Exception as e:
        erro(f"Erro ao processar lote: {e}")
        conn.rollback()

def buscar_produto(conn, product_id):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.id, p.name, p.price, COALESCE(s.quantity, 0)
                FROM products p
                LEFT JOIN stock s ON s.product_id = p.id
                WHERE p.id = %s
            """, (product_id,))
            res = cur.fetchone()
            if res:
                return {"id": res[0], "name": res[1], "price": res[2], "stock": res[3]}
            return None
    except Exception as e:
        erro(f"Erro ao buscar produto: {e}")
        return None

def extrair_valor_arrecadacao(codigo):
    digits = re.sub(r'\D', '', codigo)
    if len(digits) != 44:
        return None
    try:
        return Decimal(digits[4:15]) / 100
    except:
        return None

def processo_checkout(conn):
    total = Decimal("0.00")
    produtos = []
    contas = []
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO transactions (transaction_type) VALUES ('checkout') RETURNING id")
            trans_id = cur.fetchone()[0]

            while True:
                codigo = input_info("Digite ou escaneie o código (FIM para encerrar): ").strip()
                if codigo.upper() == "FIM":
                    break

                if is_febraban(codigo):
                    valor = extrair_valor_arrecadacao(codigo)
                    if valor is None:
                        erro("Código FEBRABAN inválido.")
                        continue
                    contas.append(codigo)
                    total += valor
                    info(f"[Conta] Valor: R$ {valor:.2f}")
                    continue

                custom = parse_codigo_customizado(codigo)
                if custom:
                    produto = buscar_produto(conn, custom["produto_id"])
                    if not produto:
                        erro("Produto não encontrado.")
                        continue
                    if produto["stock"] <= 0:
                        erro(f"Produto '{produto['name']}' sem estoque.")
                        continue
                    cur.execute("""
                        INSERT INTO transaction_items (transaction_id, product_id, quantity, price)
                        VALUES (%s, %s, 1, %s)
                    """, (trans_id, produto["id"], produto["price"]))
                    total += produto["price"]
                    produtos.append((produto["name"], produto["price"]))
                    sucesso(f"[Produto] {produto['name']} | R$ {produto['price']:.2f}")
                else:
                    erro("Formato de código inválido.")
            conn.commit()
    except Exception as e:
        erro(f"Falha no checkout: {e}")
        conn.rollback()

    print(Fore.GREEN + "\n--- RESUMO DA COMPRA ---")
    for nome, valor in produtos:
        print(f"{nome}: R$ {valor:.2f}")
    for conta in contas:
        print(f"Conta FEBRABAN: {conta}")
    print(Fore.GREEN + f"\nTOTAL A PAGAR: R$ {total:.2f}")

def menu(conn):
    while True:
        print(Fore.GREEN + "\n===== SISTEMA DO SUPERMERCADO =====")
        print("1 - Receber Material")
        print("2 - Fazer Checkout")
        print("3 - Sair")
        print(Fore.GREEN + "===================================\n")

        opcao = input_info("Escolha uma opção: ").strip()
        if opcao == "1":
            adicionar_estoque(conn)
        elif opcao == "2":
            processo_checkout(conn)
        elif opcao == "3":
            info("Saindo do sistema. Até logo!")
            break
        else:
            erro("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    conn = get_connection()
    if conn:
        try:
            menu(conn)
        finally:
            conn.close()
            info("Conexão com o banco encerrada.")