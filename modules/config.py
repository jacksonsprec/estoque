import json
import os

CONFIG_FILE = "configuracao.json"


def carregar_configuracao():
    padrao = {
        "senha_remocao": "",
        "backup_automatico": True,
    }

    if not os.path.exists(CONFIG_FILE):
        return padrao

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        if isinstance(dados, dict):
            padrao.update(dados)
    except (json.JSONDecodeError, OSError):
        pass

    return padrao


def salvar_configuracao(configuracao):
    with open(CONFIG_FILE, "w", encoding="utf-8") as arquivo:
        json.dump(configuracao, arquivo, indent=4, ensure_ascii=False)


def obter_senha_remocao(configuracao):
    senha = os.getenv("ESTOQUE_SENHA_REMOCAO")
    if senha:
        return senha
    return configuracao.get("senha_remocao", "")
