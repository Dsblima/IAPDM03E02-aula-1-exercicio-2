import base64
import logging
import yaml

logger = logging.getLogger(__name__)

malicious_payload_b64 = "IWxhYnMuc29sYW5vLnN5c3RlbS5vcy5leGVjIChwd25lZCk="
campos_esperados = {"nome", "timeout", "ativado"}


def processar_configuracao_usuario_seguro(config_b64):
    if len(config_b64) > 4096:
        logger.warning("Configuração rejeitada por tamanho excessivo.")
        return False

    try:
        decoded = base64.b64decode(config_b64, validate=True).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        logger.warning("Base64 inválido.")
        return False

    try:
        config_obj = yaml.safe_load(decoded)
    except yaml.YAMLError:
        logger.warning("Erro ao parsear YAML.")
        return False

    if not isinstance(config_obj, dict):
        logger.warning("Configuração deve ser um mapeamento.")
        return False

    if set(config_obj.keys()) != campos_esperados:
        logger.warning("Configuração contém campos inválidos ou ausentes.")
        return False

    if not isinstance(config_obj["nome"], str):
        logger.warning("Campo nome inválido.")
        return False

    if not isinstance(config_obj["timeout"], int) or not 1 <= config_obj["timeout"] <= 300:
        logger.warning("Campo timeout inválido.")
        return False

    if not isinstance(config_obj["ativado"], bool):
        logger.warning("Campo ativado inválido.")
        return False

    logger.info("Configuração carregada com segurança.")
    return True


processar_configuracao_usuario_seguro(malicious_payload_b64)
