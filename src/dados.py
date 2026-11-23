import os


def salvar_recorde(caminho_arquivo, pontuacao):
    """Salva o recorde (aqui, o melhor tempo em ms) em arquivo texto.

    Retorna True se conseguiu gravar. Se a gravação falhar (pasta protegida, por
    exemplo), o jogo continua funcionando e retorna False.
    """
    try:
        os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)
        with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
            arquivo.write(str(pontuacao))
        return True
    except OSError:
        return False


def carregar_recorde(caminho_arquivo):
    """Carrega o recorde salvo; retorna 0 se não existir valor válido."""
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            conteudo = arquivo.read().strip()

            if conteudo == "":
                return 0

            return max(0, int(conteudo))

    except (FileNotFoundError, ValueError):
        return 0
