# Relatorio de Revisao de Seguranca Python

Escopo revisado:

- `example1.py`
- `exercicio2.py`
- `exercicio3.py`

## Sumario Executivo

Foram encontradas vulnerabilidades relevantes nos tres arquivos Python da pasta:

- 2 achados `Critical`: desserializacao YAML insegura e path traversal/arbitrary file write.
- 1 achado `Medium`: race condition em controle de estoque.
- 1 achado `Low`: exposicao de dados sensiveis em logs.

Tambem foi identificado um erro de sintaxe em `exercicio3.py` causado por aspas curvas na chamada final da funcao.

---

## Vulnerability

Unsafe YAML Deserialization

## Severity

Critical

## Location

`exercicio2.py:14`

```python
config_obj = yaml.load(decoded)
```

## Explanation

`yaml.load(decoded)` processa YAML controlado pelo usuario. Dependendo da versao/configuracao do PyYAML, isso pode permitir criacao de objetos Python perigosos e ate execucao de codigo. A funcao se chama `processar_configuracao_usuario_seguro`, mas usa uma API insegura para dados nao confiaveis.

## Exploitation Scenario

Um atacante envia um payload YAML codificado em Base64 contendo tags maliciosas para instanciar objetos ou acionar comportamento perigoso no interpretador Python. Em um backend real, isso pode resultar em execucao remota de codigo, vazamento de dados ou alteracao de estado no servidor.

## Secure Fix

Use `yaml.safe_load`, valide Base64 estritamente, limite o tamanho da entrada e valide schema/tipos dos campos aceitos.

## Hardened Python Example

```python
import base64
import yaml

def processar_configuracao_usuario_seguro(config_b64: str) -> bool:
    if len(config_b64) > 4096:
        return False

    try:
        decoded = base64.b64decode(config_b64, validate=True).decode("utf-8")
        config_obj = yaml.safe_load(decoded)
    except (ValueError, UnicodeDecodeError, yaml.YAMLError):
        return False

    if not isinstance(config_obj, dict):
        return False

    if set(config_obj) != {"nome", "timeout", "ativado"}:
        return False

    if not isinstance(config_obj["nome"], str):
        return False

    if not isinstance(config_obj["timeout"], int) or not 1 <= config_obj["timeout"] <= 300:
        return False

    if not isinstance(config_obj["ativado"], bool):
        return False

    return True
```

---

## Vulnerability

Path Traversal / Arbitrary File Write

## Severity

Critical

## Location

`exercicio3.py:4`

```python
base_dir = f"/var/relatorios/{nome_usuario}"
```

`exercicio3.py:6`

```python
caminho_completo = os.path.join(base_dir, nome_arquivo)
```

`exercicio3.py:9`

```python
with open(caminho_completo, 'w') as f:
```

## Explanation

`nome_usuario` e `nome_arquivo` entram diretamente no caminho do arquivo. Um valor como `../../../../etc/passwd` pode escapar de `/var/relatorios/admin` e escrever fora do diretorio esperado. Isso viola a fronteira de confianca do sistema de arquivos.

## Exploitation Scenario

Se esse codigo rodar com permissoes elevadas, um atacante pode sobrescrever arquivos sensiveis, plantar arquivos em diretorios criticos, corromper dados de outros usuarios ou substituir arquivos usados por outros processos.

## Secure Fix

Normalize o caminho, restrinja a escrita ao diretorio base permitido e aceite apenas nomes de usuario/arquivo simples via allowlist.

## Hardened Python Example

```python
from pathlib import Path
import re

BASE_REPORTS_DIR = Path("/var/relatorios").resolve()
SAFE_NAME = re.compile(r"^[a-zA-Z0-9._-]+$")

def gerar_relatorio_usuario(nome_usuario: str, nome_arquivo: str) -> None:
    if not SAFE_NAME.fullmatch(nome_usuario):
        raise ValueError("Nome de usuario invalido")

    if Path(nome_arquivo).name != nome_arquivo or not SAFE_NAME.fullmatch(nome_arquivo):
        raise ValueError("Nome de arquivo invalido")

    user_dir = (BASE_REPORTS_DIR / nome_usuario).resolve()
    user_dir.mkdir(parents=True, exist_ok=True)

    output_path = (user_dir / nome_arquivo).resolve()

    if BASE_REPORTS_DIR not in output_path.parents:
        raise ValueError("Tentativa de path traversal bloqueada")

    output_path.write_text("Conteudo do relatorio secreto.", encoding="utf-8")
```

---

## Vulnerability

Race Condition / TOCTOU em Estoque

## Severity

Medium

## Location

`example1.py:13`

```python
if self.estoque['item_raro'] > 0:
```

`example1.py:15`

```python
self.estoque['item_raro'] -= 1
```

## Explanation

O codigo cria `self.mutex`, mas nao usa. A checagem `estoque > 0` e o decremento nao sao atomicos. O `time.sleep(0.5)` aumenta a janela da corrida, permitindo que varias threads passem pela validacao antes do estoque ser decrementado.

## Exploitation Scenario

Multiplas requisicoes simultaneas podem comprar o mesmo item raro. Em uma loja real, isso causa overselling, fraude de estoque, inconsistencias de pedidos e possivel prejuizo financeiro.

## Secure Fix

Use `with self.mutex` envolvendo a checagem e o decremento do estoque.

## Hardened Python Example

```python
import threading

class LojaOnline:
    def __init__(self):
        self.estoque = {"item_raro": 1}
        self.mutex = threading.Lock()

    def comprar_item(self, usuario: str) -> bool:
        with self.mutex:
            if self.estoque["item_raro"] <= 0:
                print(f"{usuario}: Estoque esgotado!")
                return False

            self.estoque["item_raro"] -= 1
            print(
                f"{usuario} comprou com sucesso! "
                f"Estoque restante: {self.estoque['item_raro']}"
            )
            return True
```

---

## Vulnerability

Sensitive Data Exposure in Logs

## Severity

Low

## Location

`exercicio2.py:24`

```python
print("Configuracao carregada com seguranca:", config_obj)
```

`exercicio2.py:31-32`

```python
except Exception as e:
    print("Erro inesperado:", e)
```

## Explanation

O codigo imprime a configuracao completa e detalhes de excecoes. Se a configuracao passar a conter tokens, paths internos, credenciais ou outros dados sensiveis, essas informacoes podem vazar em logs.

## Exploitation Scenario

Um atacante ou usuario interno com acesso a logs pode recuperar informacoes sensiveis registradas durante o processamento de configuracoes. Em ambientes reais, logs costumam ser enviados para ferramentas centralizadas, aumentando o raio de exposicao.

## Secure Fix

Logue mensagens genericas para usuario e detalhes sanitizados em logger interno. Evite imprimir payloads completos e excecoes com dados sensiveis.

## Hardened Python Example

```python
import logging

logger = logging.getLogger(__name__)

def registrar_configuracao_carregada(config_obj: dict) -> None:
    logger.info(
        "Configuracao carregada",
        extra={"campos": sorted(config_obj.keys())},
    )

def registrar_erro_parse() -> None:
    logger.warning("Falha ao processar configuracao de usuario")
```

---

## Observacao Adicional

`exercicio3.py:12` possui um erro de sintaxe:

```python
gerar_relatorio_usuario("admin", “../../../../etc/passwd")
```

A string comeca com aspas curvas (`“`) e termina com aspas retas (`"`), quebrando a execucao do arquivo. O correto seria usar aspas retas consistentes:

```python
gerar_relatorio_usuario("admin", "../../../../etc/passwd")
```

Mesmo corrigindo a sintaxe, esse valor demonstra exatamente o ataque de path traversal descrito acima.
