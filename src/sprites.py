import pygame

from src.config import (
    AMARELO,
    AZUL_JOGADOR,
    BRANCO,
    CARRO_ALTURA,
    CARRO_LARGURA,
    LARANJA_IA,
    TIPOS_OBJETO,
    VERDE,
)


def pegar_sprite(local_arquivo, x, y, width, height, scale=1):
    """Corta um único elemento de uma spritesheet BMP e remove o fundo."""

    # 1. Carrega o BMP e usa .convert() (sem alpha) para otimizar a velocidade
    sheet = pygame.image.load(local_arquivo).convert()

    # 2. Cria uma superfície padrão para o recorte (não precisa de SRCALPHA aqui)
    image = pygame.Surface((width, height))

    # 3. Copia o pedaço da folha BMP para a nossa nova imagem
    image.blit(sheet, (0, 0), (x, y, width, height))

    # 4. CONFIGURAÇÃO DA TRANSPARÊNCIA (O segredo para o BMP)
    # Pegamos a cor do pixel no canto superior esquerdo (0,0) do recorte,
    # assumindo que o fundo do seu sprite começa ali.
    cor_do_fundo = image.get_at((0, 0))

    # Dizemos ao Pygame para ignorar essa cor específica na hora de desenhar
    image.set_colorkey(cor_do_fundo)

    # 5. Aplica o redimensionamento, se houver
    if scale != 1:
        novo_largura = int(width * scale)
        novo_altura = int(height * scale)
        image = pygame.transform.scale(image, (novo_largura, novo_altura))

    return image


# ---------------------------------------------------------------------------
# Sprites desenhados por código (formas simples), conforme o escopo da proposta.
# ---------------------------------------------------------------------------
def criar_carro(cor_corpo):
    """Desenha um carro visto de cima, com a frente voltada para o topo da imagem."""
    largura, altura = CARRO_LARGURA, CARRO_ALTURA
    imagem = pygame.Surface((largura, altura), pygame.SRCALPHA)

    # Rodas (aparecem um pouco para fora do corpo)
    for y_roda in (8, altura - 24):
        pygame.draw.rect(imagem, (20, 20, 22), (0, y_roda, 6, 16), border_radius=2)
        pygame.draw.rect(imagem, (20, 20, 22), (largura - 6, y_roda, 6, 16), border_radius=2)

    # Corpo, para-brisa, vidro traseiro e faróis
    pygame.draw.rect(imagem, cor_corpo, (3, 0, largura - 6, altura), border_radius=10)
    pygame.draw.rect(imagem, (175, 215, 240), (8, 14, largura - 16, 14), border_radius=3)
    pygame.draw.rect(imagem, (110, 140, 165), (8, altura - 20, largura - 16, 9), border_radius=3)
    pygame.draw.rect(imagem, AMARELO, (6, 1, 7, 4), border_radius=2)
    pygame.draw.rect(imagem, AMARELO, (largura - 13, 1, 7, 4), border_radius=2)
    return imagem


def criar_cone():
    """Cone de trânsito laranja."""
    info = TIPOS_OBJETO["cone"]
    imagem = pygame.Surface((info["largura"], info["altura"]), pygame.SRCALPHA)
    largura, altura = info["largura"], info["altura"]
    pygame.draw.rect(imagem, (225, 225, 225), (2, altura - 7, largura - 4, 7), border_radius=2)
    pygame.draw.polygon(imagem, (245, 120, 25), [(largura // 2, 1), (largura - 6, altura - 7), (6, altura - 7)])
    pygame.draw.polygon(imagem, BRANCO, [(largura // 2 - 5, 11), (largura // 2 + 5, 11), (largura // 2 + 7, 16), (largura // 2 - 7, 16)])
    return imagem


def criar_oleo():
    """Poça de óleo na pista."""
    info = TIPOS_OBJETO["oleo"]
    imagem = pygame.Surface((info["largura"], info["altura"]), pygame.SRCALPHA)
    largura, altura = info["largura"], info["altura"]
    pygame.draw.ellipse(imagem, (18, 16, 24), (0, 4, largura, altura - 8))
    pygame.draw.ellipse(imagem, (70, 60, 110), (10, 10, largura // 2, altura // 3))
    pygame.draw.ellipse(imagem, (60, 110, 120), (largura // 2, altura // 2 - 2, largura // 4, altura // 5))
    return imagem


def criar_buraco():
    """Buraco no asfalto."""
    info = TIPOS_OBJETO["buraco"]
    imagem = pygame.Surface((info["largura"], info["altura"]), pygame.SRCALPHA)
    largura, altura = info["largura"], info["altura"]
    pygame.draw.ellipse(imagem, (110, 108, 102), (0, 0, largura, altura))
    pygame.draw.ellipse(imagem, (22, 22, 24), (4, 4, largura - 8, altura - 8))
    return imagem


def criar_bateria():
    """Bateria verde (energia limpa) com um raio no centro."""
    info = TIPOS_OBJETO["bateria"]
    largura, altura = info["largura"], info["altura"]
    imagem = pygame.Surface((largura, altura), pygame.SRCALPHA)
    pygame.draw.rect(imagem, (30, 80, 50), (largura // 2 - 5, 0, 10, 5), border_radius=2)
    pygame.draw.rect(imagem, VERDE, (1, 4, largura - 2, altura - 4), border_radius=5)
    pygame.draw.rect(imagem, (30, 80, 50), (1, 4, largura - 2, altura - 4), width=2, border_radius=5)
    meio = largura // 2
    raio = [(meio + 3, 8), (meio - 5, 21), (meio, 21), (meio - 3, 32), (meio + 6, 18), (meio + 1, 18)]
    pygame.draw.polygon(imagem, BRANCO, raio)
    return imagem


def carregar_sprites():
    """Cria todos os sprites do jogo e devolve em um dicionário (nome -> imagem)."""
    return {
        "carro_jogador": criar_carro(AZUL_JOGADOR),
        "carro_ia": criar_carro(LARANJA_IA),
        "cone": criar_cone(),
        "oleo": criar_oleo(),
        "buraco": criar_buraco(),
        "bateria": criar_bateria(),
    }
