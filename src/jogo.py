import random

import pygame

from src.config import (
    ALTURA_TELA,
    CAMINHO_RECORDE,
    FPS,
    LARGURA_TELA,
    TITULO_JOGO,
    TOTAL_ROUNDS,
)
from src.dados import carregar_recorde, salvar_recorde
from src.desenho import criar_fontes, desenhar_cena
from src.partida import (
    FASE_MENU,
    atualizar_estado,
    avancar_fase,
    criar_estado,
)
from src.sprites import carregar_sprites

DT_MAXIMO = 0.05  # evita "saltos" na física se o jogo travar por um instante


def ler_comandos(teclas):
    """Converte as teclas pressionadas em comandos do jogo (aceita setas e WASD)."""
    return {
        "esquerda": teclas[pygame.K_LEFT] or teclas[pygame.K_a],
        "direita": teclas[pygame.K_RIGHT] or teclas[pygame.K_d],
        "acelerar": teclas[pygame.K_UP] or teclas[pygame.K_w],
        "frear": teclas[pygame.K_DOWN] or teclas[pygame.K_s],
    }


def montar_titulo_janela(estado):
    """Texto da barra de título com as informações principais da partida."""
    if estado["fase"] == FASE_MENU:
        return TITULO_JOGO

    numero = min(estado["indice_round"] + 1, TOTAL_ROUNDS)
    vitorias = estado["vitorias"]
    return f"{TITULO_JOGO} | Round {numero}/{TOTAL_ROUNDS} | Você {vitorias['jogador']} x {vitorias['ia']} IA"


def executar_jogo():
    """Executa o loop principal do jogo: eventos, atualização do estado e desenho."""
    pygame.init()

    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption(TITULO_JOGO)

    relogio = pygame.time.Clock()
    sprites = carregar_sprites()
    fontes = criar_fontes()
    rng = random.Random()

    # O recorde é o melhor tempo (em milissegundos) de um round vencido.
    estado = criar_estado(carregar_recorde(CAMINHO_RECORDE))
    rodando = True

    # Loop principal: processa entrada, atualiza estado e renderiza a cena.
    while rodando:
        dt = min(relogio.tick(FPS) / 1000, DT_MAXIMO)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    avancar_fase(estado, rng)

        comandos = ler_comandos(pygame.key.get_pressed())
        atualizar_estado(estado, dt, comandos, rng)

        # Grava o recorde assim que um novo melhor tempo é registrado.
        if estado["salvar_pendente"]:
            salvar_recorde(CAMINHO_RECORDE, estado["melhor_tempo"])
            estado["salvar_pendente"] = False

        pygame.display.set_caption(montar_titulo_janela(estado))
        desenhar_cena(tela, estado, sprites, fontes)
        pygame.display.flip()

    pygame.quit()
