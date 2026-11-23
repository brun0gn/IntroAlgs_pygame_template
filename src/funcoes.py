# Funções de lógica do jogo (sem desenho na tela), para facilitar os testes.
import pygame

from src.config import (
    ACELERACAO,
    ATRITO,
    BONUS_IMPULSO,
    CARRO_LARGURA,
    DISTANCIA_FINAL_LIVRE,
    DISTANCIA_INICIAL_OBSTACULOS,
    FATOR_PENALIDADE,
    FREIO,
    LARGURA_FAIXA,
    MARGEM_PISTA,
    N_FAIXAS,
    PX_POR_METRO,
    TIPOS_OBJETO,
    TIPOS_OBSTACULO,
    TOLERANCIA_LINHA,
)


# ------------------------------------------------------------------ utilidades gerais
def limitar_valor(valor, minimo, maximo):
    """Mantém um valor dentro do intervalo [minimo, maximo]."""
    if valor < minimo:
        return minimo
    if valor > maximo:
        return maximo
    return valor


def verificar_colisao(retangulo_1, retangulo_2):
    """Verifica sobreposição entre dois retângulos do Pygame."""
    return retangulo_1.colliderect(retangulo_2)


def formatar_tempo(milissegundos):
    """Converte milissegundos para o formato MM:SS.cc (ex.: 00:24.35)."""
    milissegundos = max(0, int(milissegundos))
    minutos = milissegundos // 60000
    segundos = (milissegundos % 60000) / 1000
    return f"{minutos:02d}:{segundos:05.2f}"


def distancia_em_metros(distancia):
    """Converte a distância do mundo (pixels) para metros, só para exibição."""
    return int(distancia / PX_POR_METRO)


def velocidade_em_kmh(velocidade):
    """Converte a velocidade (pixels por segundo) para km/h, só para exibição."""
    return int(velocidade / PX_POR_METRO * 3.6)


# ------------------------------------------------------------------ movimento
def velocidade_maxima(base, com_impulso, com_penalidade):
    """Calcula a velocidade máxima atual considerando penalidade e impulso."""
    velocidade = base
    if com_penalidade:
        velocidade = base * FATOR_PENALIDADE
    if com_impulso:
        velocidade += BONUS_IMPULSO
    return velocidade


def calcular_velocidade(velocidade, acelerando, freando, vel_max, dt):
    """Atualiza a velocidade do carro em um intervalo de tempo dt (segundos)."""
    if freando:
        velocidade -= FREIO * dt
    elif acelerando:
        velocidade += ACELERACAO * dt
    else:
        velocidade -= ATRITO * dt  # sem acelerar, o carro vai perdendo velocidade
    return limitar_valor(velocidade, 0, vel_max)


def centro_da_faixa(faixa):
    """Posição X (dentro do painel) do centro de uma faixa da pista."""
    return MARGEM_PISTA + faixa * LARGURA_FAIXA + LARGURA_FAIXA / 2


def faixa_do_x(x):
    """Descobre em qual faixa (0 a N_FAIXAS-1) uma posição X está."""
    faixa = int((x - MARGEM_PISTA) // LARGURA_FAIXA)
    return limitar_valor(faixa, 0, N_FAIXAS - 1)


def limites_x_carro():
    """Menor e maior X permitidos para o centro do carro (ele não sai da pista)."""
    folga = 2
    minimo = MARGEM_PISTA + CARRO_LARGURA / 2 + folga
    maximo = MARGEM_PISTA + N_FAIXAS * LARGURA_FAIXA - CARRO_LARGURA / 2 - folga
    return minimo, maximo


def retangulo_no_mundo(x, dist, largura, altura):
    """Retângulo de colisão de um objeto. No mundo, avançar na pista é subir no eixo Y."""
    return pygame.Rect(int(x - largura / 2), int(-dist - altura / 2), largura, altura)


# ------------------------------------------------------------------ pista e objetos
def e_obstaculo(objeto):
    """Indica se o objeto da pista é um obstáculo (e não um item)."""
    return TIPOS_OBJETO[objeto["tipo"]]["categoria"] == "obstaculo"


def gerar_pista(config_rodada, distancia_pista, rng):
    """Gera a lista de objetos (obstáculos e baterias) de um round, em ordem de distância.

    Os objetos nascem em "linhas". Cada linha tem de 1 a max_obstaculos_linha
    obstáculos e sempre deixa pelo menos duas faixas livres, então a pista nunca
    fica bloqueada.
    """
    objetos = []
    linha = 0
    distancia = DISTANCIA_INICIAL_OBSTACULOS

    while distancia < distancia_pista - DISTANCIA_FINAL_LIVRE:
        faixas = list(range(N_FAIXAS))
        rng.shuffle(faixas)

        quantidade = rng.randint(1, config_rodada["max_obstaculos_linha"])
        for faixa in faixas[:quantidade]:
            tipo = rng.choice(TIPOS_OBSTACULO)
            objetos.append({"tipo": tipo, "faixa": faixa, "dist": distancia, "linha": linha})

        # A bateria aparece em uma faixa livre da mesma linha.
        if rng.random() < config_rodada["chance_bateria"]:
            objetos.append(
                {"tipo": "bateria", "faixa": faixas[quantidade], "dist": distancia, "linha": linha}
            )

        distancia += config_rodada["espaco_linhas"]
        linha += 1

    return objetos


def proximo_obstaculo(objetos, dist_ref, alcance):
    """Retorna o obstáculo mais próximo à frente (dentro do alcance) ou None."""
    for objeto in objetos:  # a lista está ordenada por distância
        if not e_obstaculo(objeto):
            continue
        diferenca = objeto["dist"] - dist_ref
        if diferenca > alcance:
            break
        if diferenca > -TOLERANCIA_LINHA:
            return objeto
    return None


def faixas_bloqueadas(objetos, linha):
    """Conjunto de faixas ocupadas por obstáculos em uma linha da pista."""
    return {obj["faixa"] for obj in objetos if obj["linha"] == linha and e_obstaculo(obj)}


def escolher_faixa_livre(faixa_atual, bloqueadas, n_faixas):
    """Escolhe a faixa livre mais próxima da faixa atual (a própria, se estiver livre)."""
    if faixa_atual not in bloqueadas:
        return faixa_atual

    for distancia in range(1, n_faixas):
        for candidata in (faixa_atual - distancia, faixa_atual + distancia):
            if 0 <= candidata < n_faixas and candidata not in bloqueadas:
                return candidata

    return faixa_atual  # nenhuma faixa livre (não deve acontecer)


# ------------------------------------------------------------------ "inteligência" do jogo
def percebeu_obstaculo(erro_sensor, rng):
    """Simula o sensor da IA: retorna False quando ele falha em detectar os obstáculos."""
    return rng.random() >= erro_sensor


def sugerir_faixa(faixa_atual, bloqueadas, n_faixas, confiabilidade, rng):
    """Simula o assistente de rota (IA). Retorna (faixa sugerida, sugestão está correta?).

    Com probabilidade igual à confiabilidade, sugere uma faixa livre. Caso
    contrário, "alucina" e sugere uma faixa que está bloqueada.
    """
    faixa_certa = escolher_faixa_livre(faixa_atual, bloqueadas, n_faixas)

    if not bloqueadas or rng.random() < confiabilidade:
        return faixa_certa, True

    return rng.choice(sorted(bloqueadas)), False


# ------------------------------------------------------------------ regras de round e partida
def decidir_vencedor_round(dist_jogador, dist_ia, distancia_pista):
    """Retorna "jogador", "ia" ou None (ninguém cruzou a linha de chegada ainda)."""
    jogador_chegou = dist_jogador >= distancia_pista
    ia_chegou = dist_ia >= distancia_pista

    if jogador_chegou and ia_chegou:
        # Cruzaram no mesmo instante: vence quem foi mais longe.
        return "jogador" if dist_jogador >= dist_ia else "ia"
    if jogador_chegou:
        return "jogador"
    if ia_chegou:
        return "ia"
    return None


def vencedor_da_partida(vitorias_jogador, vitorias_ia, rounds_para_vencer):
    """Retorna "jogador", "ia" ou None se a partida ainda não terminou."""
    if vitorias_jogador >= rounds_para_vencer:
        return "jogador"
    if vitorias_ia >= rounds_para_vencer:
        return "ia"
    return None


def atualizar_melhor_tempo(melhor_ms, tempo_ms):
    """Compara um tempo com o recorde (0 = ainda não há recorde).

    Retorna (novo_recorde, bateu_recorde).
    """
    if melhor_ms <= 0 or tempo_ms < melhor_ms:
        return tempo_ms, True
    return melhor_ms, False
