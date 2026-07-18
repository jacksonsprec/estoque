import re
from datetime import datetime

DATE_ONLY_FORMAT = "%d/%m/%Y"


def validar_quantidade(quantidade):
    try:
        valor = int(quantidade)
    except (TypeError, ValueError):
        raise ValueError("A quantidade deve ser um número inteiro.")

    if valor < 0:
        raise ValueError("A quantidade não pode ser negativa.")

    return valor


def validar_validade(validade):
    valor = validade.strip()
    if not valor:
        return ""

    numeros = re.sub(r"\D", "", valor)
    if len(numeros) != 8:
        raise ValueError("A validade deve seguir o formato DD/MM/AAAA.")

    try:
        datetime.strptime(valor, DATE_ONLY_FORMAT)
    except ValueError as exc:
        raise ValueError("A validade deve seguir o formato DD/MM/AAAA.") from exc

    return valor


def dias_ate_validade(validade):
    if not validade:
        return None

    try:
        data_validade = datetime.strptime(validade, DATE_ONLY_FORMAT).date()
    except ValueError:
        return None

    return (data_validade - datetime.now().date()).days
