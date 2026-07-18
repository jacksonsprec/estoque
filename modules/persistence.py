import json
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

DATA_FILE = "estoque_data.json"
LIXEIRA_FILE = "lixeira.json"
THEME_FILE = "tema_config.json"
DB_FILE = "estoque.db"
BACKUP_DIR = "backups"
MAX_BACKUPS = 10
DATE_TIME_FORMAT = "%d/%m/%Y %H:%M:%S"
DATE_ONLY_FORMAT = "%d/%m/%Y"


def _conectar_db():
    conexao = sqlite3.connect(DB_FILE)
    conexao.row_factory = sqlite3.Row
    return conexao


def _inicializar_db():
    with _conectar_db() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS itens (
                chave_material TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                descricao TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                validade TEXT,
                chegada TEXT NOT NULL
            )
            """
        )
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS movimentacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chave_material TEXT NOT NULL,
                nome TEXT NOT NULL,
                tipo TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                motivo TEXT NOT NULL,
                data TEXT NOT NULL,
                hora TEXT NOT NULL
            )
            """
        )
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS lixeira (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                item_json TEXT NOT NULL,
                removido_em TEXT NOT NULL
            )
            """
        )


def _carregar_json_legacy():
    if not os.path.exists(DATA_FILE):
        return None

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except (json.JSONDecodeError, OSError):
        return None

    if isinstance(dados, dict) and "itens" in dados and "log_global" in dados:
        for chave, item in list(dados["itens"].items()):
            if isinstance(item, dict) and "nome" not in item:
                item["nome"] = chave.split(" | ")[0] if " | " in chave else chave
        return dados

    return None


def _migrar_json_legacy_para_sqlite():
    _inicializar_db()

    with _conectar_db() as conexao:
        total_itens = conexao.execute("SELECT COUNT(*) AS total FROM itens").fetchone()["total"]
        total_movimentacoes = conexao.execute("SELECT COUNT(*) AS total FROM movimentacoes").fetchone()["total"]

    if total_itens > 0 or total_movimentacoes > 0:
        return

    dados = _carregar_json_legacy()
    if not dados:
        return

    with _conectar_db() as conexao:
        for chave, item in dados.get("itens", {}).items():
            conexao.execute(
                """
                INSERT OR REPLACE INTO itens (
                    chave_material, nome, descricao, quantidade, validade, chegada
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    chave,
                    item.get("nome", chave),
                    item.get("descricao", ""),
                    item.get("quantidade", 0),
                    item.get("validade", ""),
                    item.get("chegada", datetime.now().strftime(DATE_TIME_FORMAT)),
                ),
            )

        for movimento in dados.get("log_global", []):
            conexao.execute(
                """
                INSERT INTO movimentacoes (
                    chave_material, nome, tipo, quantidade, motivo, data, hora
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    movimento.get("chave_material") or movimento.get("nome") or "",
                    movimento.get("nome", ""),
                    movimento.get("tipo", ""),
                    movimento.get("quantidade", 0),
                    movimento.get("motivo", ""),
                    movimento.get("data", ""),
                    movimento.get("hora", ""),
                ),
            )


def carregar_tema():
    if os.path.exists(THEME_FILE):
        try:
            with open(THEME_FILE, "r", encoding="utf-8") as arquivo:
                tema = json.load(arquivo)
            if tema in {"claro", "escuro"}:
                return tema
        except (json.JSONDecodeError, OSError):
            pass
    return "claro"


def salvar_tema(tema):
    with open(THEME_FILE, "w", encoding="utf-8") as arquivo:
        json.dump(tema, arquivo, ensure_ascii=False)


def carregar_dados():
    _inicializar_db()
    _migrar_json_legacy_para_sqlite()

    with _conectar_db() as conexao:
        itens_rows = conexao.execute(
            "SELECT chave_material, nome, descricao, quantidade, validade, chegada FROM itens"
        ).fetchall()
        movimentacoes_rows = conexao.execute(
            "SELECT id, chave_material, nome, tipo, quantidade, motivo, data, hora FROM movimentacoes ORDER BY id"
        ).fetchall()

    itens = {}
    log_global = []

    for linha in itens_rows:
        chave_material = linha["chave_material"]
        item = {
            "nome": linha["nome"],
            "descricao": linha["descricao"],
            "quantidade": linha["quantidade"],
            "validade": linha["validade"],
            "chegada": linha["chegada"],
            "log": [],
        }
        itens[chave_material] = item

    for linha in movimentacoes_rows:
        movimento = {
            "tipo": linha["tipo"],
            "nome": linha["nome"],
            "quantidade": linha["quantidade"],
            "motivo": linha["motivo"],
            "data": linha["data"],
            "hora": linha["hora"],
        }
        log_global.append(movimento)

        chave_material = linha["chave_material"]
        if chave_material in itens:
            itens[chave_material]["log"].append(movimento)

    return {"itens": itens, "log_global": log_global}


def carregar_lixeira():
    _inicializar_db()

    with _conectar_db() as conexao:
        linhas = conexao.execute(
            "SELECT id, nome, item_json, removido_em FROM lixeira ORDER BY id"
        ).fetchall()

    itens_removidos = []
    for linha in linhas:
        itens_removidos.append(
            {
                "nome": linha["nome"],
                "item": json.loads(linha["item_json"]),
                "removido_em": linha["removido_em"],
            }
        )

    return {"itens_removidos": itens_removidos}


def criar_backup_automatico(origem, configuracao):
    if not configuracao.get("backup_automatico", True):
        return

    destino_dir = Path(BACKUP_DIR)
    destino_dir.mkdir(exist_ok=True)

    nome_arquivo = Path(origem).name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = destino_dir / f"{timestamp}_{nome_arquivo}"

    try:
        shutil.copy2(origem, destino)
    except OSError:
        pass

    backups = sorted(destino_dir.glob("*"), key=lambda item: item.stat().st_mtime, reverse=True)
    while len(backups) > MAX_BACKUPS:
        try:
            backups[-1].unlink(missing_ok=True)
        except OSError:
            pass
        backups = backups[:-1]


def salvar_dados(estoque, configuracao):
    _inicializar_db()
    criar_backup_automatico(DB_FILE, configuracao)

    with _conectar_db() as conexao:
        conexao.execute("DELETE FROM itens")
        conexao.execute("DELETE FROM movimentacoes")

        for chave_material, item in estoque.get("itens", {}).items():
            conexao.execute(
                """
                INSERT INTO itens (
                    chave_material, nome, descricao, quantidade, validade, chegada
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    chave_material,
                    item.get("nome", chave_material),
                    item.get("descricao", ""),
                    item.get("quantidade", 0),
                    item.get("validade", ""),
                    item.get("chegada", datetime.now().strftime(DATE_TIME_FORMAT)),
                ),
            )

        for movimento in estoque.get("log_global", []):
            conexao.execute(
                """
                INSERT INTO movimentacoes (
                    chave_material, nome, tipo, quantidade, motivo, data, hora
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    movimento.get("chave_material", ""),
                    movimento.get("nome", ""),
                    movimento.get("tipo", ""),
                    movimento.get("quantidade", 0),
                    movimento.get("motivo", ""),
                    movimento.get("data", ""),
                    movimento.get("hora", ""),
                ),
            )


def salvar_lixeira(lixeira, configuracao):
    _inicializar_db()
    criar_backup_automatico(DB_FILE, configuracao)

    with _conectar_db() as conexao:
        conexao.execute("DELETE FROM lixeira")

        for item_removido in lixeira.get("itens_removidos", []):
            conexao.execute(
                """
                INSERT INTO lixeira (nome, item_json, removido_em)
                VALUES (?, ?, ?)
                """,
                (
                    item_removido.get("nome", ""),
                    json.dumps(item_removido.get("item", {}), ensure_ascii=False),
                    item_removido.get("removido_em", datetime.now().strftime(DATE_TIME_FORMAT)),
                ),
            )
