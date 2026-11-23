import random

import pygame

from src.config import (
    BONUS_IMPULSO,
    DISTANCIA_FINAL_LIVRE,
    DISTANCIA_INICIAL_OBSTACULOS,
    DISTANCIA_PISTA,
    FATOR_PENALIDADE,
    LARGURA_FAIXA,
    MARGEM_PISTA,
    N_FAIXAS,
    RODADAS,
    VEL_MAX,
)
from src.funcoes import (
    atualizar_melhor_tempo,
    calcular_velocidade,
    centro_da_faixa,
    decidir_vencedor_round,
    distancia_em_metros,
    e_obstaculo,
    escolher_faixa_livre,
    faixa_do_x,
    faixas_bloqueadas,
    formatar_tempo,
    gerar_pista,
    limitar_valor,
    limites_x_carro,
    percebeu_obstaculo,
    proximo_obstaculo,
    retangulo_no_mundo,
    sugerir_faixa,
    velocidade_em_kmh,
    velocidade_maxima,
    vencedor_da_partida,
    verificar_colisao,
)


# ------------------------------------------------------------------ utilidades
def test_limitar_valor_abaixo_do_minimo():
    """Deve retornar o limite minimo quando o valor informado for menor."""
    assert limitar_valor(-5, 0, 100) == 0


def test_limitar_valor_acima_do_maximo():
    """Deve retornar o limite maximo quando o valor informado for maior."""
    assert limitar_valor(150, 0, 100) == 100


def test_limitar_valor_dentro_do_intervalo():
    """Deve manter o valor original quando ele ja estiver no intervalo."""
    assert limitar_valor(50, 0, 100) == 50


def test_verificar_colisao_com_sobreposicao():
    """Retangulos que se sobrepoem devem colidir."""
    assert verificar_colisao(pygame.Rect(0, 0, 10, 10), pygame.Rect(5, 5, 10, 10)) is True


def test_verificar_colisao_sem_sobreposicao():
    """Retangulos separados nao devem colidir."""
    assert verificar_colisao(pygame.Rect(0, 0, 10, 10), pygame.Rect(50, 50, 10, 10)) is False


def test_formatar_tempo():
    """Deve formatar milissegundos como MM:SS.cc."""
    assert formatar_tempo(24350) == "00:24.35"
    assert formatar_tempo(65500) == "01:05.50"
    assert formatar_tempo(-10) == "00:00.00"


def test_conversoes_de_exibicao():
    """Metros e km/h sao so conversoes de unidade para mostrar na tela."""
    assert distancia_em_metros(7000) == 700
    assert velocidade_em_kmh(100) == 36


# ------------------------------------------------------------------ movimento
def test_acelerar_aumenta_a_velocidade():
    assert calcular_velocidade(100, True, False, VEL_MAX, 0.5) > 100


def test_frear_reduz_a_velocidade_sem_ficar_negativa():
    assert calcular_velocidade(100, False, True, VEL_MAX, 0.1) < 100
    assert calcular_velocidade(5, False, True, VEL_MAX, 1.0) == 0


def test_sem_acelerar_o_carro_perde_velocidade():
    assert calcular_velocidade(200, False, False, VEL_MAX, 0.5) < 200


def test_velocidade_nunca_passa_do_maximo():
    assert calcular_velocidade(VEL_MAX - 1, True, False, VEL_MAX, 5.0) == VEL_MAX


def test_velocidade_maxima_com_penalidade_e_impulso():
    assert velocidade_maxima(300, False, False) == 300
    assert velocidade_maxima(300, False, True) == 300 * FATOR_PENALIDADE
    assert velocidade_maxima(300, True, False) == 300 + BONUS_IMPULSO


def test_centro_e_faixa_do_x_sao_coerentes():
    for faixa in range(N_FAIXAS):
        assert faixa_do_x(centro_da_faixa(faixa)) == faixa


def test_faixa_do_x_fica_dentro_dos_limites():
    assert faixa_do_x(-100) == 0
    assert faixa_do_x(10_000) == N_FAIXAS - 1


def test_limites_x_carro_ficam_dentro_da_pista():
    minimo, maximo = limites_x_carro()
    assert minimo > MARGEM_PISTA
    assert maximo < MARGEM_PISTA + N_FAIXAS * LARGURA_FAIXA


def test_retangulo_no_mundo_avanca_para_cima():
    perto = retangulo_no_mundo(100, 0, 20, 20)
    longe = retangulo_no_mundo(100, 500, 20, 20)
    assert longe.y < perto.y


# ------------------------------------------------------------------ pista
def test_gerar_pista_e_reprodutivel_com_a_mesma_semente():
    a = gerar_pista(RODADAS[0], DISTANCIA_PISTA, random.Random(42))
    b = gerar_pista(RODADAS[0], DISTANCIA_PISTA, random.Random(42))
    assert a == b


def test_gerar_pista_ordenada_e_dentro_dos_limites():
    for config_rodada in RODADAS:
        objetos = gerar_pista(config_rodada, DISTANCIA_PISTA, random.Random(1))
        distancias = [obj["dist"] for obj in objetos]

        assert distancias == sorted(distancias)
        assert min(distancias) >= DISTANCIA_INICIAL_OBSTACULOS
        assert max(distancias) < DISTANCIA_PISTA - DISTANCIA_FINAL_LIVRE
        assert all(0 <= obj["faixa"] < N_FAIXAS for obj in objetos)


def test_gerar_pista_nunca_bloqueia_a_pista_inteira():
    """Toda linha deve ter pelo menos duas faixas livres de obstaculos."""
    for semente in range(20):
        for config_rodada in RODADAS:
            objetos = gerar_pista(config_rodada, DISTANCIA_PISTA, random.Random(semente))
            linhas = {obj["linha"] for obj in objetos}
            for linha in linhas:
                bloqueadas = faixas_bloqueadas(objetos, linha)
                assert 1 <= len(bloqueadas) <= config_rodada["max_obstaculos_linha"]
                assert N_FAIXAS - len(bloqueadas) >= 2


def test_bateria_nao_fica_na_mesma_faixa_de_obstaculo():
    for semente in range(20):
        objetos = gerar_pista(RODADAS[0], DISTANCIA_PISTA, random.Random(semente))
        for obj in objetos:
            if not e_obstaculo(obj):
                assert obj["faixa"] not in faixas_bloqueadas(objetos, obj["linha"])


def _pista_exemplo():
    return [
        {"tipo": "bateria", "faixa": 0, "dist": 400, "linha": 0},
        {"tipo": "cone", "faixa": 1, "dist": 400, "linha": 0},
        {"tipo": "buraco", "faixa": 3, "dist": 400, "linha": 0},
        {"tipo": "oleo", "faixa": 2, "dist": 800, "linha": 1},
    ]


def test_proximo_obstaculo_ignora_baterias_e_respeita_alcance():
    objetos = _pista_exemplo()
    assert proximo_obstaculo(objetos, 100, 400)["linha"] == 0
    assert proximo_obstaculo(objetos, 100, 100) is None  # fora do alcance
    assert proximo_obstaculo(objetos, 500, 400)["linha"] == 1  # a linha 0 ja passou


def test_faixas_bloqueadas_nao_inclui_bateria():
    assert faixas_bloqueadas(_pista_exemplo(), 0) == {1, 3}


def test_escolher_faixa_livre_mantem_faixa_se_estiver_livre():
    assert escolher_faixa_livre(2, {1, 3}, N_FAIXAS) == 2


def test_escolher_faixa_livre_vai_para_a_mais_proxima():
    assert escolher_faixa_livre(1, {1, 3}, N_FAIXAS) == 0
    assert escolher_faixa_livre(3, {3, 2}, N_FAIXAS) == 1


def test_escolher_faixa_livre_sem_saida_mantem_a_faixa():
    assert escolher_faixa_livre(1, {0, 1, 2, 3}, N_FAIXAS) == 1


# ------------------------------------------------------------------ "IA" do jogo
def test_sensor_perfeito_sempre_percebe():
    rng = random.Random(0)
    assert all(percebeu_obstaculo(0.0, rng) for _ in range(50))


def test_sensor_totalmente_falho_nunca_percebe():
    rng = random.Random(0)
    assert not any(percebeu_obstaculo(1.0, rng) for _ in range(50))


def test_assistente_confiavel_sugere_faixa_livre():
    faixa, correta = sugerir_faixa(1, {1, 3}, N_FAIXAS, 1.0, random.Random(0))
    assert correta is True
    assert faixa not in {1, 3}


def test_assistente_que_erra_sugere_faixa_bloqueada():
    faixa, correta = sugerir_faixa(1, {1, 3}, N_FAIXAS, 0.0, random.Random(0))
    assert correta is False
    assert faixa in {1, 3}


def test_assistente_sem_obstaculos_nao_erra():
    faixa, correta = sugerir_faixa(2, set(), N_FAIXAS, 0.0, random.Random(0))
    assert (faixa, correta) == (2, True)


# ------------------------------------------------------------------ regras de round e partida
def test_decidir_vencedor_round():
    assert decidir_vencedor_round(100, 200, DISTANCIA_PISTA) is None
    assert decidir_vencedor_round(DISTANCIA_PISTA, 200, DISTANCIA_PISTA) == "jogador"
    assert decidir_vencedor_round(200, DISTANCIA_PISTA + 1, DISTANCIA_PISTA) == "ia"


def test_decidir_vencedor_round_com_chegada_simultanea():
    assert decidir_vencedor_round(DISTANCIA_PISTA + 5, DISTANCIA_PISTA + 1, DISTANCIA_PISTA) == "jogador"
    assert decidir_vencedor_round(DISTANCIA_PISTA + 1, DISTANCIA_PISTA + 5, DISTANCIA_PISTA) == "ia"


def test_vencedor_da_partida():
    assert vencedor_da_partida(1, 1, 2) is None
    assert vencedor_da_partida(2, 0, 2) == "jogador"
    assert vencedor_da_partida(1, 2, 2) == "ia"


def test_atualizar_melhor_tempo():
    assert atualizar_melhor_tempo(0, 25000) == (25000, True)  # primeiro tempo registrado
    assert atualizar_melhor_tempo(25000, 24000) == (24000, True)
    assert atualizar_melhor_tempo(25000, 26000) == (25000, False)
