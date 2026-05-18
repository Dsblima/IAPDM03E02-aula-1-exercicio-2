import re
from pathlib import Path


BASE_REPORTS_DIR = (Path.cwd() / "relatorios").resolve()
SAFE_NAME = re.compile(r"^[a-zA-Z0-9._-]+$")


def gerar_relatorio_usuario(nome_usuario, nome_arquivo):
    if not SAFE_NAME.fullmatch(nome_usuario):
        raise ValueError("Nome de usuário inválido.")

    if Path(nome_arquivo).name != nome_arquivo or not SAFE_NAME.fullmatch(nome_arquivo):
        raise ValueError("Nome de arquivo inválido.")

    base_dir = (BASE_REPORTS_DIR / nome_usuario).resolve()
    base_dir.mkdir(parents=True, exist_ok=True)

    caminho_completo = (base_dir / nome_arquivo).resolve()

    if BASE_REPORTS_DIR not in caminho_completo.parents:
        raise ValueError("Tentativa de path traversal bloqueada.")

    print(f"Caminho do arquivo gerado: {caminho_completo}")

    caminho_completo.write_text("Conteúdo do relatório secreto.", encoding="utf-8")


try:
    gerar_relatorio_usuario("admin", "../../../../etc/passwd")
except ValueError as erro:
    print(f"Entrada bloqueada: {erro}")
