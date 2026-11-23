# Tudo o que é desenhado na tela: pistas, HUD e telas de menu/resultado.
import math

import pygame

from src.config import (
    ALCANCE_SENSOR,
    ALTURA_HUD,
    ALTURA_PAINEL,
    ALTURA_RODAPE,
    ALTURA_TELA,
    AMARELO,
    AZUL_JOGADOR,
    BRANCO,
    CARRO_ALTURA,
    COR_ASFALTO,
    COR_CALCADA,
    COR_FAIXA,
    COR_FUNDO_HUD,
    COR_PAINEL,
    CORES_PREDIOS,
    DISTANCIA_PISTA,
    ESPACO_PREDIOS,
    LARANJA_IA,
    LARGURA_FAIXA,
    LARGURA_PAINEL,
    LARGURA_TELA,
    MARGEM_PISTA,
    N_FAIXAS,
    PADRAO_PREDIOS,
    PRETO,
    TIPOS_OBJETO,
    TOTAL_ROUNDS,
    VERDE,
    VERMELHO,
    Y_CARRO,
)
from src.funcoes import (
    centro_da_faixa,
    distancia_em_metros,
    formatar_tempo,
    velocidade_em_kmh,
)
from src.partida import (
    FASE_CONTAGEM,
    FASE_CORRENDO,
    FASE_FIM_PARTIDA,
    FASE_FIM_ROUND,
    FASE_MENU,
    configuracao_do_round,
    dica_do_round,
    mensagem_assistente,
)

COR_TEXTO_SECUNDARIO = (185, 190, 200)
PERIODO_TRACEJADO = 60  # distância entre os tracejados da faixa
Y_RODAPE = ALTURA_TELA - ALTURA_RODAPE


# ------------------------------------------------------------------ texto
def criar_fontes():
    """Cria as fontes usadas no jogo (fonte padrão do Pygame, em vários tamanhos)."""
    return {
        "contagem": pygame.font.Font(None, 170),
        "titulo": pygame.font.Font(None, 72),
        "grande": pygame.font.Font(None, 48),
        "media": pygame.font.Font(None, 32),
        "pequena": pygame.font.Font(None, 24),
        "mini": pygame.font.Font(None, 20),
    }


def escrever(tela, fonte, texto, cor, posicao, alinhamento="esquerda", sombra=False, alfa=255):
    """Desenha um texto. O alinhamento define qual ponto do texto fica em `posicao`."""
    imagem = fonte.render(texto, True, cor)
    imagem.set_alpha(alfa)
    retangulo = imagem.get_rect()
    if alinhamento == "centro":
        retangulo.midtop = posicao
    elif alinhamento == "direita":
        retangulo.topright = posicao
    else:
        retangulo.topleft = posicao

    if sombra:
        sombra_img = fonte.render(texto, True, PRETO)
        sombra_img.set_alpha(alfa)
        tela.blit(sombra_img, retangulo.move(2, 2))
    tela.blit(imagem, retangulo)
    return retangulo


def quebrar_texto(texto, fonte, largura_maxima):
    """Divide um texto em linhas que cabem na largura informada."""
    linhas = []
    atual = ""
    for palavra in texto.split():
        tentativa = f"{atual} {palavra}".strip()
        if fonte.size(tentativa)[0] <= largura_maxima:
            atual = tentativa
        else:
            linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def escrever_paragrafo(tela, fonte, texto, cor, x_centro, y, largura_maxima, espacamento=4):
    """Escreve um texto centralizado, quebrando em várias linhas. Retorna o próximo Y livre."""
    for linha in quebrar_texto(texto, fonte, largura_maxima):
        escrever(tela, fonte, linha, cor, (x_centro, y), "centro")
        y += fonte.get_linesize() + espacamento
    return y


def desenhar_cartao(tela, retangulo):
    """Caixa escura semitransparente usada nas telas de menu e de resultado."""
    cartao = pygame.Surface(retangulo.size, pygame.SRCALPHA)
    pygame.draw.rect(cartao, COR_PAINEL, cartao.get_rect(), border_radius=18)
    pygame.draw.rect(cartao, (255, 255, 255, 70), cartao.get_rect(), width=2, border_radius=18)
    tela.blit(cartao, retangulo.topleft)


# ------------------------------------------------------------------ pista
def y_na_tela(dist_objeto, dist_carro, y0):
    """Converte uma distância do mundo em posição Y na tela (o carro fica sempre em Y_CARRO)."""
    return y0 + Y_CARRO - (dist_objeto - dist_carro)


def desenhar_predios(tela, x0, y0, dist):
    """Prédios nas calçadas, para dar sensação de movimento e de cidade."""
    primeiro = int((dist - (ALTURA_PAINEL - Y_CARRO)) // ESPACO_PREDIOS) - 1
    ultimo = int((dist + Y_CARRO) // ESPACO_PREDIOS) + 1
    largura = MARGEM_PISTA - 10

    for k in range(primeiro, ultimo + 1):
        for lado, deslocamento in (("esq", 0), ("dir", 3)):
            altura, indice_cor = PADRAO_PREDIOS[(k + deslocamento) % len(PADRAO_PREDIOS)]
            cor = CORES_PREDIOS[indice_cor]
            y_topo = y_na_tela(k * ESPACO_PREDIOS + altura, dist, y0)
            x = x0 + 4 if lado == "esq" else x0 + LARGURA_PAINEL - 4 - largura
            pygame.draw.rect(tela, cor, (x, y_topo, largura, altura), border_radius=3)
            telhado = tuple(min(255, c + 35) for c in cor)
            pygame.draw.rect(tela, telhado, (x + 6, y_topo + 6, largura - 12, altura - 12), border_radius=2)


def desenhar_linha_horizontal(tela, retangulo_pista, y, xadrez):
    """Linha de largada (lisa) ou de chegada (xadrez) atravessando a pista."""
    if not xadrez:
        pygame.draw.rect(tela, COR_FAIXA, (retangulo_pista.x, y - 3, retangulo_pista.width, 6))
        return

    tamanho = 19
    for coluna in range(retangulo_pista.width // tamanho + 1):
        for linha in range(2):
            cor = BRANCO if (coluna + linha) % 2 == 0 else PRETO
            largura = min(tamanho, retangulo_pista.width - coluna * tamanho)
            if largura > 0:
                tela.fill(cor, (retangulo_pista.x + coluna * tamanho, y - tamanho + linha * tamanho, largura, tamanho))


def desenhar_cone_sensor(tela, x0, y0, x_carro):
    """Mostra o "campo de visão" do sensor do carro autônomo."""
    superficie = pygame.Surface((LARGURA_PAINEL, ALTURA_PAINEL), pygame.SRCALPHA)
    topo_y = Y_CARRO - ALCANCE_SENSOR
    pontos = [(x_carro - 8, Y_CARRO), (x_carro + 8, Y_CARRO), (x_carro + 70, topo_y), (x_carro - 70, topo_y)]
    pygame.draw.polygon(superficie, (255, 235, 120, 38), pontos)
    tela.blit(superficie, (x0, y0))


def desenhar_painel(tela, x0, y0, carro, estado, sprites, eh_ia, fontes):
    """Desenha a visão de um carro (jogador ou IA): pista, objetos, carro e avisos."""
    area = pygame.Rect(x0, y0, LARGURA_PAINEL, ALTURA_PAINEL)
    tela.set_clip(area)
    tela.fill(COR_CALCADA, area)

    dist = carro["dist"]
    desenhar_predios(tela, x0, y0, dist)

    # Asfalto e bordas
    pista = pygame.Rect(x0 + MARGEM_PISTA, y0, N_FAIXAS * LARGURA_FAIXA, ALTURA_PAINEL)
    tela.fill(COR_ASFALTO, pista)
    pygame.draw.rect(tela, COR_FAIXA, (pista.x - 3, y0, 3, ALTURA_PAINEL))
    pygame.draw.rect(tela, COR_FAIXA, (pista.right, y0, 3, ALTURA_PAINEL))

    # Faixas tracejadas (se movem para baixo conforme o carro avança)
    deslocamento = dist % PERIODO_TRACEJADO
    for indice in range(1, N_FAIXAS):
        x_faixa = pista.x + indice * LARGURA_FAIXA
        y = y0 - PERIODO_TRACEJADO + deslocamento
        while y < y0 + ALTURA_PAINEL:
            pygame.draw.rect(tela, COR_FAIXA, (x_faixa - 2, y, 4, 28))
            y += PERIODO_TRACEJADO

    # Largada e chegada
    desenhar_linha_horizontal(tela, pista, int(y_na_tela(0, dist, y0)), xadrez=False)
    desenhar_linha_horizontal(tela, pista, int(y_na_tela(DISTANCIA_PISTA, dist, y0)), xadrez=True)

    # Sugestão do assistente de rota (só no painel do jogador)
    if not eh_ia and estado["sugestao"] is not None and estado["fase"] == FASE_CORRENDO:
        desenhar_sugestao(tela, x0, y0, dist, estado["sugestao"], fontes)

    # Obstáculos e itens
    for indice, objeto in enumerate(estado["objetos"]):
        y = y_na_tela(objeto["dist"], dist, y0)
        if y < y0 - 60 or y > y0 + ALTURA_PAINEL + 60:
            continue

        usado = indice in carro["usados"]
        if usado and objeto["tipo"] in ("cone", "bateria"):
            continue  # o cone foi derrubado / a bateria já foi coletada

        imagem = sprites[objeto["tipo"]]
        x = x0 + centro_da_faixa(objeto["faixa"])
        tela.blit(imagem, imagem.get_rect(center=(x, y)))

        # No painel da IA, mostra o que o sensor detectou (verde) ou deixou passar (vermelho).
        if eh_ia and objeto["tipo"] != "bateria" and not usado:
            percebeu = carro["percepcao"].get(objeto["linha"])
            if percebeu is not None:
                info = TIPOS_OBJETO[objeto["tipo"]]
                caixa = pygame.Rect(0, 0, info["largura"] + 8, info["altura"] + 8)
                caixa.center = (x, y)
                pygame.draw.rect(tela, VERDE if percebeu else VERMELHO, caixa, width=2, border_radius=4)

    # Carro (com campo de visão do sensor, chama de impulso e piscada de penalidade)
    x_carro = x0 + carro["x"]
    y_carro = y0 + Y_CARRO
    if eh_ia and estado["fase"] in (FASE_CONTAGEM, FASE_CORRENDO):
        desenhar_cone_sensor(tela, x0, y0, carro["x"])

    if carro["impulso"] > 0:
        oscilacao = 6 * ((pygame.time.get_ticks() // 70) % 3)
        base_y = y_carro + CARRO_ALTURA // 2
        pygame.draw.polygon(tela, LARANJA_IA, [(x_carro - 9, base_y), (x_carro + 9, base_y), (x_carro, base_y + 20 + oscilacao)])
        pygame.draw.polygon(tela, AMARELO, [(x_carro - 4, base_y), (x_carro + 4, base_y), (x_carro, base_y + 11 + oscilacao)])

    sprite = sprites["carro_ia" if eh_ia else "carro_jogador"]
    if carro["penalidade"] > 0 and (pygame.time.get_ticks() // 120) % 2 == 0:
        sprite = sprite.copy()
        sprite.fill((170, 40, 40, 0), special_flags=pygame.BLEND_RGB_ADD)
    tela.blit(sprite, sprite.get_rect(center=(x_carro, y_carro)))

    desenhar_avisos(tela, x0, y0, estado, "ia" if eh_ia else "jogador", fontes)
    desenhar_titulo_painel(tela, x0, y0, estado, eh_ia, fontes)
    tela.set_clip(None)


def desenhar_sugestao(tela, x0, y0, dist, sugestao, fontes):
    """Destaca a faixa sugerida pelo assistente de rota. Ela pode estar errada!"""
    y = y_na_tela(sugestao["dist"], dist, y0)
    largura = LARGURA_FAIXA - 8
    marca = pygame.Surface((largura, 64), pygame.SRCALPHA)
    pygame.draw.rect(marca, (70, 225, 130, 85), marca.get_rect(), border_radius=8)
    pygame.draw.rect(marca, (70, 225, 130, 230), marca.get_rect(), width=2, border_radius=8)
    retangulo = marca.get_rect(center=(x0 + centro_da_faixa(sugestao["faixa"]), y))
    tela.blit(marca, retangulo)
    escrever(tela, fontes["mini"], "IA", (200, 255, 220), (retangulo.centerx, retangulo.y - 15), "centro")


def desenhar_avisos(tela, x0, y0, estado, lado, fontes):
    """Mensagens curtas (batida, bateria, erro da IA...) sobre o painel."""
    avisos = [a for a in estado["avisos"] if a["lado"] == lado]
    for posicao, aviso in enumerate(reversed(avisos)):
        alfa = int(255 * min(1.0, aviso["tempo"] / 0.5))
        y = y0 + Y_CARRO - 150 - posicao * 28
        escrever(tela, fontes["pequena"], aviso["texto"], aviso["cor"], (x0 + LARGURA_PAINEL // 2, y), "centro", sombra=True, alfa=alfa)


def desenhar_titulo_painel(tela, x0, y0, estado, eh_ia, fontes):
    """Faixa no topo de cada painel dizendo quem está ali e como a IA está configurada."""
    faixa = pygame.Surface((LARGURA_PAINEL, 38), pygame.SRCALPHA)
    faixa.fill((10, 12, 18, 170))
    tela.blit(faixa, (x0, y0))

    config_rodada = configuracao_do_round(estado)
    if eh_ia:
        escrever(tela, fontes["pequena"], "CARRO AUTÔNOMO (IA)", LARANJA_IA, (x0 + 10, y0 + 3))
        precisao = int((1 - config_rodada["erro_sensor"]) * 100)
        escrever(tela, fontes["mini"], f"Precisão do sensor: {precisao}%", COR_TEXTO_SECUNDARIO, (x0 + 10, y0 + 22))
    else:
        escrever(tela, fontes["pequena"], "VOCÊ", AZUL_JOGADOR, (x0 + 10, y0 + 3))
        confianca = int(config_rodada["confiabilidade_assistente"] * 100)
        escrever(tela, fontes["mini"], f"Assistente de rota (IA): confiança {confianca}%", COR_TEXTO_SECUNDARIO, (x0 + 10, y0 + 22))


# ------------------------------------------------------------------ HUD
def desenhar_hud(tela, estado, fontes):
    """Barra superior: round, placar, tempo e diferença entre os carros."""
    tela.fill(COR_FUNDO_HUD, (0, 0, LARGURA_TELA, ALTURA_HUD))

    numero = min(estado["indice_round"] + 1, TOTAL_ROUNDS)
    escrever(tela, fontes["media"], f"ROUND {numero}/{TOTAL_ROUNDS}", BRANCO, (16, 8))
    melhor = formatar_tempo(estado["melhor_tempo"]) if estado["melhor_tempo"] > 0 else "--:--.--"
    escrever(tela, fontes["mini"], f"Melhor tempo: {melhor}", COR_TEXTO_SECUNDARIO, (16, 36))

    vitorias = estado["vitorias"]
    escrever(tela, fontes["grande"], f"{vitorias['jogador']}  x  {vitorias['ia']}", BRANCO, (LARGURA_TELA // 2, 6), "centro")
    escrever(tela, fontes["mini"], "VOCÊ", AZUL_JOGADOR, (LARGURA_TELA // 2 - 30, 38), "direita")
    escrever(tela, fontes["mini"], "IA", LARANJA_IA, (LARGURA_TELA // 2 + 30, 38))

    tempo_ms = int(estado["tempo_round"] * 1000)
    escrever(tela, fontes["media"], formatar_tempo(tempo_ms), BRANCO, (LARGURA_TELA - 16, 8), "direita")
    if estado["fase"] == FASE_CORRENDO:
        diferenca = distancia_em_metros(estado["jogador"]["dist"] - estado["ia"]["dist"])
        if diferenca >= 0:
            escrever(tela, fontes["mini"], f"Você lidera por {diferenca} m", VERDE, (LARGURA_TELA - 16, 36), "direita")
        else:
            escrever(tela, fontes["mini"], f"IA lidera por {-diferenca} m", LARANJA_IA, (LARGURA_TELA - 16, 36), "direita")


def desenhar_barra_progresso(tela, x, y, largura, progresso, cor):
    """Barra de progresso da corrida (0.0 a 1.0)."""
    pygame.draw.rect(tela, (50, 54, 64), (x, y, largura, 14), border_radius=7)
    preenchido = int(largura * max(0.0, min(1.0, progresso)))
    if preenchido > 0:
        pygame.draw.rect(tela, cor, (x, y, preenchido, 14), border_radius=7)
    pygame.draw.rect(tela, (120, 126, 140), (x, y, largura, 14), width=1, border_radius=7)


def desenhar_rodape(tela, estado, fontes):
    """Barra inferior: progresso e velocidade de cada carro."""
    tela.fill(COR_FUNDO_HUD, (0, Y_RODAPE, LARGURA_TELA, ALTURA_RODAPE))

    for x0, carro, cor in ((0, estado["jogador"], AZUL_JOGADOR), (LARGURA_PAINEL, estado["ia"], LARANJA_IA)):
        desenhar_barra_progresso(tela, x0 + 16, Y_RODAPE + 13, 190, carro["dist"] / DISTANCIA_PISTA, cor)

        texto = f"{velocidade_em_kmh(carro['vel'])} km/h"
        cor_texto = COR_TEXTO_SECUNDARIO
        if carro["impulso"] > 0:
            texto += "  IMPULSO"
            cor_texto = VERDE
        elif carro["penalidade"] > 0:
            texto += "  LENTO"
            cor_texto = VERMELHO
        escrever(tela, fontes["pequena"], texto, cor_texto, (x0 + LARGURA_PAINEL - 16, Y_RODAPE + 11), "direita")

    pygame.draw.line(tela, (80, 85, 98), (LARGURA_PAINEL, Y_RODAPE), (LARGURA_PAINEL, ALTURA_TELA), 2)


# ------------------------------------------------------------------ telas e cartões
def desenhar_menu(tela, estado, fontes):
    """Tela inicial com regras e controles."""
    cartao = pygame.Rect(0, 0, 680, 430)
    cartao.center = (LARGURA_TELA // 2, ALTURA_HUD + ALTURA_PAINEL // 2)
    desenhar_cartao(tela, cartao)

    centro = cartao.centerx
    escrever(tela, fontes["titulo"], "Corrida dos PUCAmigos", BRANCO, (centro, cartao.y + 20), "centro", sombra=True)
    escrever(tela, fontes["media"], "IA no cotidiano: mobilidade inteligente", AMARELO, (centro, cartao.y + 78), "centro")

    textos = [
        "Corra contra um carro autônomo guiado por IA e vença 2 de 3 rounds.",
        "Seu assistente de rota (IA) sugere a faixa mais segura, mas ele pode errar: confira a pista antes de confiar!",
        "Pegue baterias (energia limpa) para ganhar impulso. Cones, óleo e buracos fazem você perder velocidade.",
        "As caixas verdes mostram o que o sensor da IA detectou; as vermelhas, o que ele não viu.",
    ]
    y = cartao.y + 122
    for texto in textos:
        y = escrever_paragrafo(tela, fontes["pequena"], texto, (225, 228, 235), centro, y, cartao.width - 70, 2) + 4

    escrever(tela, fontes["pequena"], "Setas ou A/D: mover   |   Cima ou W: acelerar   |   Baixo ou S: frear", AMARELO, (centro, cartao.bottom - 88), "centro")
    escrever(tela, fontes["media"], "Pressione ENTER para começar   (ESC sai)", BRANCO, (centro, cartao.bottom - 56), "centro")


def desenhar_contagem(tela, estado, fontes):
    """Contagem regressiva antes da largada."""
    centro = LARGURA_TELA // 2
    numero = max(1, math.ceil(estado["contagem"]))
    texto_round = f"Round {estado['indice_round'] + 1} de {TOTAL_ROUNDS}"
    escrever(tela, fontes["grande"], texto_round, AMARELO, (centro, 130), "centro", sombra=True)
    escrever(tela, fontes["contagem"], str(numero), BRANCO, (centro, 185), "centro", sombra=True)
    escrever(tela, fontes["pequena"], "Segure CIMA para acelerar", BRANCO, (centro, 330), "centro", sombra=True)


def desenhar_resultado_round(tela, estado, fontes):
    """Cartão exibido ao final de um round."""
    cartao = pygame.Rect(0, 0, 600, 360)
    cartao.center = (LARGURA_TELA // 2, ALTURA_HUD + ALTURA_PAINEL // 2)
    desenhar_cartao(tela, cartao)
    centro = cartao.centerx

    ganhou = estado["vencedor_round"] == "jogador"
    titulo = "Você venceu o round!" if ganhou else "A IA venceu o round"
    escrever(tela, fontes["grande"], titulo, VERDE if ganhou else LARANJA_IA, (centro, cartao.y + 24), "centro", sombra=True)

    vitorias = estado["vitorias"]
    escrever(tela, fontes["media"], f"Placar: Você {vitorias['jogador']} x {vitorias['ia']} IA", BRANCO, (centro, cartao.y + 76), "centro")

    y = cartao.y + 116
    if ganhou:
        escrever(tela, fontes["pequena"], f"Seu tempo: {formatar_tempo(estado['tempo_vitoria_ms'])}", BRANCO, (centro, y), "centro")
        y += 26
        if estado["novo_recorde"]:
            escrever(tela, fontes["pequena"], "Novo melhor tempo!", AMARELO, (centro, y), "centro")
            y += 26

    estatisticas = estado["estatisticas"]
    resumo = f"Baterias: {estatisticas['baterias']}   Batidas: {estatisticas['batidas']}   Batidas da IA: {estatisticas['batidas_ia']}"
    escrever(tela, fontes["pequena"], resumo, COR_TEXTO_SECUNDARIO, (centro, y), "centro")
    y += 36

    y = escrever_paragrafo(tela, fontes["pequena"], mensagem_assistente(estatisticas), AMARELO, centro, y, cartao.width - 60) + 6
    escrever_paragrafo(tela, fontes["pequena"], dica_do_round(estado["indice_round"]), (225, 228, 235), centro, y, cartao.width - 60)

    escrever(tela, fontes["media"], "ENTER: próximo round", BRANCO, (centro, cartao.bottom - 44), "centro")


def desenhar_resultado_partida(tela, estado, fontes):
    """Cartão exibido ao final da partida (vitória ou derrota)."""
    cartao = pygame.Rect(0, 0, 600, 360)
    cartao.center = (LARGURA_TELA // 2, ALTURA_HUD + ALTURA_PAINEL // 2)
    desenhar_cartao(tela, cartao)
    centro = cartao.centerx

    ganhou = estado["vencedor_partida"] == "jogador"
    titulo = "VITÓRIA!" if ganhou else "DERROTA"
    escrever(tela, fontes["titulo"], titulo, VERDE if ganhou else VERMELHO, (centro, cartao.y + 20), "centro", sombra=True)

    vitorias = estado["vitorias"]
    escrever(tela, fontes["grande"], f"Você {vitorias['jogador']} x {vitorias['ia']} IA", BRANCO, (centro, cartao.y + 92), "centro")

    y = cartao.y + 146
    if ganhou:
        texto = "Você venceu o carro autônomo. Usar a IA como apoio, e não como piloto automático, compensa."
    else:
        texto = "O carro autônomo levou a melhor desta vez. Tente conferir a pista e pegar mais baterias."
    y = escrever_paragrafo(tela, fontes["pequena"], texto, (225, 228, 235), centro, y, cartao.width - 60) + 6
    escrever_paragrafo(tela, fontes["pequena"], dica_do_round(estado["indice_round"]), AMARELO, centro, y, cartao.width - 60)

    escrever(tela, fontes["media"], "ENTER: jogar de novo   (ESC sai)", BRANCO, (centro, cartao.bottom - 44), "centro")


# ------------------------------------------------------------------ cena completa
def desenhar_cena(tela, estado, sprites, fontes):
    """Desenha um quadro completo do jogo, de acordo com a fase atual."""
    tela.fill(PRETO)

    desenhar_painel(tela, 0, ALTURA_HUD, estado["jogador"], estado, sprites, False, fontes)
    desenhar_painel(tela, LARGURA_PAINEL, ALTURA_HUD, estado["ia"], estado, sprites, True, fontes)
    pygame.draw.line(tela, (20, 22, 28), (LARGURA_PAINEL, ALTURA_HUD), (LARGURA_PAINEL, Y_RODAPE), 3)

    desenhar_hud(tela, estado, fontes)
    desenhar_rodape(tela, estado, fontes)

    fase = estado["fase"]
    if fase == FASE_MENU:
        desenhar_menu(tela, estado, fontes)
    elif fase == FASE_CONTAGEM:
        desenhar_contagem(tela, estado, fontes)
    elif fase == FASE_FIM_ROUND:
        desenhar_resultado_round(tela, estado, fontes)
    elif fase == FASE_FIM_PARTIDA:
        desenhar_resultado_partida(tela, estado, fontes)
