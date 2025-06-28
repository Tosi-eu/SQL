import os
import re
import psycopg2
from decimal import Decimal
from colorama import init, Fore, Style

init(autoreset=True)

# ===============================
# MENSAGENS COLORIDAS
# ===============================
def info(msg): print(f"{Fore.LIGHTYELLOW_EX}[INFO]{Style.RESET_ALL} {msg}")
def sucesso(msg): print(f"{Fore.GREEN}[SUCESSO]{Style.RESET_ALL} {msg}")
def erro(msg): print(f"{Fore.RED}[ERRO]{Style.RESET_ALL} {msg}")
def input_info(prompt): return input(f"{Fore.LIGHTYELLOW_EX}[INFO]{Style.RESET_ALL} {prompt}")

# ===============================
# CONEXÃO COM O BANCO
# ===============================
def get_connection():
    try:
        conn = psycopg2.connect(
            dbname='supermercado', #criar esse banco de dados ou usar o seu
            user='postgres', #seu usuario
            password='postgres_Eu12', #sua senha
            host='localhost', #nao mexe
            port=5432 #nao mexe
        )
        sucesso("Conexão com o banco estabelecida com sucesso.")
        return conn
    except psycopg2.Error as e:
        erro(f"Falha ao conectar ao banco: {e}")
        return None

# ===============================
# UTILITÁRIO FEBRABAN
# ===============================
def is_febraban(code):
    digits = re.sub(r'\D', '', code)
    return len(digits) in [44, 47] and digits.startswith('8')

# ===============================
# BUSCAR PRODUTO PELO CÓDIGO
# ===============================
def buscar_produto(conn, code):
    if is_febraban(code):
        info("Código FEBRABAN detectado.")
        return None
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.id, p.name, p.price, COALESCE(s.quantity, 0)
                FROM products p
                LEFT JOIN stock s ON s.product_id = p.id
                WHERE p.code = %s
            """, (code,))
            res = cur.fetchone()
            if not res:
                info("Produto não encontrado.")
                return None
            return {"id": res[0], "name": res[1], "price": res[2], "stock": res[3]}
    except Exception as e:
        erro(f"Erro ao buscar produto: {e}")
        return None

# ===============================
# CADASTRAR PRODUTO MANUALMENTE
# ===============================
def cadastrar_produto(conn):
    code = input_info("Código de barras do produto: ").strip()
    nome = input_info("Nome do produto: ").strip()
    try:
        preco = Decimal(input_info("Preço do produto (ex: 9.99): ").strip())
        if preco <= 0:
            erro("Preço deve ser maior que zero.")
            return
    except:
        erro("Preço inválido.")
        return

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM products WHERE code = %s", (code,))
            if cur.fetchone():
                erro("Produto com este código já existe.")
                return

            cur.execute("""
                INSERT INTO products (name, code, price)
                VALUES (%s, %s, %s) RETURNING id
            """, (nome, code, preco))
            product_id = cur.fetchone()[0]
            cur.execute("INSERT INTO stock (product_id, quantity) VALUES (%s, 0)", (product_id,))
            conn.commit()
            sucesso(f"Produto cadastrado: {nome} | ID: {product_id}")
    except Exception as e:
        erro(f"Erro ao cadastrar produto: {e}")
        conn.rollback()

# ===============================
# ADICIONAR ESTOQUE VIA CÓDIGO
# ===============================
def adicionar_estoque(conn):
    code = input_info("Escaneie o código de barras do lote: ").strip()

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM products WHERE code = %s", (code,))
            result = cur.fetchone()

            if result:
                product_id = result[0]
                sucesso("Produto já existente. Registrando entrada no estoque.")
            else:
                nome = f"Produto {code[-5:]}"
                preco = Decimal("9.99")
                cur.execute("""
                    INSERT INTO products (name, code, price)
                    VALUES (%s, %s, %s) RETURNING id
                """, (nome, code, preco))
                product_id = cur.fetchone()[0]
                cur.execute("INSERT INTO stock (product_id, quantity) VALUES (%s, 0)", (product_id,))
                sucesso(f"Novo produto cadastrado: {nome} | Preço: R$ {preco}")

            cur.execute("INSERT INTO transactions (transaction_type) VALUES ('entry') RETURNING id")
            trans_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO transaction_items (transaction_id, product_id, quantity, price)
                VALUES (%s, %s, 1, (SELECT price FROM products WHERE id = %s))
            """, (trans_id, product_id, product_id))

            conn.commit()
            sucesso("Produto registrado no estoque com sucesso.")
    except Exception as e:
        erro(f"Erro ao adicionar estoque: {e}")
        conn.rollback()

# ===============================
# CHECKOUT
# ===============================
def extrair_valor_arrecadacao(codigo):
    """
    Extrai o valor de um código de barras de arrecadação FEBRABAN (44 dígitos).
    Pega os dígitos de posição 5 a 15 (11 dígitos), divide por 100.
    """
    digits = re.sub(r'\D', '', codigo)
    if len(digits) != 44 or not digits.startswith('8'):
        return None
    valor_str = digits[4:15] 
    try:
        return Decimal(valor_str) / 100
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
                        erro("Código de arrecadação inválido ou valor não extraído.")
                        continue
                    contas.append(codigo)
                    info(f"[Conta FEBRABAN] Código: {codigo} | Valor: R$ {valor}")
                    total += valor
                else:
                    produto = buscar_produto(conn, codigo)
                    if not produto:
                        continue

                    if produto["stock"] == 0:
                        erro(f"Produto '{produto['name']}' sem estoque. Venda bloqueada.")
                        continue

                    cur.execute("""
                        INSERT INTO transaction_items (transaction_id, product_id, quantity, price)
                        VALUES (%s, %s, 1, %s)
                    """, (trans_id, produto["id"], produto["price"]))
                    total += produto["price"]
                    produtos.append((produto["name"], produto["price"]))
                    sucesso(f"[Produto] {produto['name']} | R$ {produto['price']}")

            conn.commit()

    except Exception as e:
        erro(f"Falha no processo de checkout: {e}")
        conn.rollback()

    print(Fore.GREEN + "\n--- RESUMO DA COMPRA ---")
    for nome, valor in produtos:
        print(f"{nome}: R$ {valor}")
    for conta in contas:
        print(f"Conta FEBRABAN: {conta}")
    print(f"\nTOTAL A PAGAR: R$ {total}")

# ===============================
# MENU PRINCIPAL
# ===============================
def menu(conn):
    while True:
        print(Fore.GREEN + "\n===== SISTEMA DO SUPERMERCADO =====")
        print("1 - Receber produto no estoque")
        print("2 - Fazer checkout de cliente")
        print("3 - Cadastrar novo produto")
        print("4 - Sair")
        print(Fore.GREEN + "===================================\n")

        opcao = input_info("Escolha uma opção: ").strip()

        if opcao == "1":
            adicionar_estoque(conn)
        elif opcao == "2":
            processo_checkout(conn)
        elif opcao == "3":
            cadastrar_produto(conn)
        elif opcao == "4":
            info("Saindo do sistema. Até logo!")
            break
        else:
            erro("Opção inválida. Tente novamente.")

# ===============================
# EXECUÇÃO PRINCIPAL
# ===============================
if __name__ == "__main__":
    conn = get_connection()
    if conn:
        try:
            menu(conn)
        finally:
            conn.close()
            info("Conexão com o banco encerrada.")