import os

def gerar_relatorio_usuario(nome_usuario, nome_arquivo):
    base_dir = f"/var/relatorios/{nome_usuario}"
    os.makedirs(base_dir, exist_ok=True)
    caminho_completo = os.path.join(base_dir, nome_arquivo)
    print(f"Caminho do arquivo gerado: {caminho_completo}")
    
    with open(caminho_completo, 'w') as f:
        f.write("Conteúdo do relatório secreto.")

gerar_relatorio_usuario("admin", “../../../../etc/passwd")
