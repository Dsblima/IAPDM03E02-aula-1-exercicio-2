import base64
import yaml

malicious_payload_b64="IWxhYnMuc29sYW5vLnN5c3RlbS5vcy5leGVjIChwd25lZCk="

def processar_configuracao_usuario_seguro(config_b64):
    try:
        decoded = base64.b64decode(config_b64).decode('utf-8')
    except Exception as e:
        print("Base64 inválido:", e)
        return False

    try:
        config_obj = yaml.load(decoded)
        if not isinstance(config_obj, dict):
            print("Configuração deve ser um mapeamento (dict).")
            return False
          
        campos_esperados = {"nome", "timeout", "ativado"}
        if not campos_esperados.intersection(config_obj.keys()):
            print("Configuração não contém campos esperados.")
            return False
        
        print("Configuração carregada com segurança:", config_obj)
        return True

    except yaml.YAMLError as e:
        print("Erro ao parsear YAML (potencialmente malicioso):", e)
        return False

    except Exception as e:
        print("Erro inesperado:", e)
        return False

processar_configuracao_usuario_seguro(malicious_payload_b64)
