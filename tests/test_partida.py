import random

from src import partida
from src.config import DISTANCIA_PISTA, DURACAO_CONTAGEM, RODADAS, ROUNDS_PARA_VENCER

PARADO = {"esquerda": False, "direita": False, "acelerar": False, "frear": False}
ACELERANDO = {"esquerda": False, "direita": False, "acelerar": True, "frear": False}


def _estado_correndo(objetos=None, melhor_tempo=0):
    """Cria um estado já em plena corrida, com uma pista controlada pelo teste."""
    rng = random.Random(1)
    estado = partida.criar_estado(melhor_tempo)
    partida.iniciar_partida(estado, rng)
    estado["fase"] = partida.FASE_CORRENDO
    estado["objetos"] = objetos if objetos is not None else []
    return estado, rng


# ------------------------------------------------------------------ fluxo de fases
def test_jogo_comeca_no_menu_com_o_recorde_carregado():
    estado = partida.criar_estado(24350)
    assert estado["fase"] == partida.FASE_MENU
    assert estado["melhor_tempo"] == 24350
    assert estado["vitorias"] == {"jogador": 0, "ia": 0}


def test_enter_no_menu_inicia_a_contagem_com_pista_gerada():
    estado = partida.criar_estado()
    partida.avancar_fase(estado, random.Random(1))

    assert estado["fase"] == partida.FASE_CONTAGEM
    assert len(estado["objetos"]) > 0
    assert estado["indice_round"] == 0


def test_contagem_termina_e_a_corrida_comeca():
    estado = partida.criar_estado()
    rng = random.Random(1)
    partida.avancar_fase(estado, rng)

    partida.atualizar_estado(estado, DURACAO_CONTAGEM - 0.5, PARADO, rng)
    assert estado["fase"] == partida.FASE_CONTAGEM

    partida.atualizar_estado(estado, 1.0, PARADO, rng)
    assert estado["fase"] == partida.FASE_CORRENDO


def test_carros_nao_andam_durante_a_contagem():
    estado = partida.criar_estado()
    rng = random.Random(1)
    partida.avancar_fase(estado, rng)
    partida.atualizar_estado(estado, 0.5, ACELERANDO, rng)

    assert estado["jogador"]["dist"] == 0
    assert estado["ia"]["dist"] == 0


# ------------------------------------------------------------------ movimento
def test_jogador_avanca_ao_acelerar():
    estado, rng = _estado_correndo()
    for _ in range(60):
        partida.atualizar_estado(estado, 1 / 60, ACELERANDO, rng)

    assert estado["jogador"]["dist"] > 0
    assert estado["jogador"]["vel"] > 0


def test_jogador_move_para_os_lados_e_fica_na_pista():
    estado, rng = _estado_correndo()
    x_inicial = estado["jogador"]["x"]
    esquerda = dict(PARADO, esquerda=True)

    partida.atualizar_estado(estado, 0.2, esquerda, rng)
    assert estado["jogador"]["x"] < x_inicial

    for _ in range(200):  # segura a tecla por muito tempo: nao pode sair da pista
        partida.atualizar_estado(estado, 0.05, esquerda, rng)
    assert estado["jogador"]["x"] > 0


# ------------------------------------------------------------------ colisoes
def test_bater_em_obstaculo_reduz_velocidade_e_aplica_penalidade():
    cone = {"tipo": "cone", "faixa": 1, "dist": 30, "linha": 0}
    estado, rng = _estado_correndo([cone])
    estado["jogador"]["vel"] = 300

    partida.atualizar_estado(estado, 1 / 60, ACELERANDO, rng)

    assert estado["jogador"]["vel"] < 150
    assert estado["jogador"]["penalidade"] > 0
    assert estado["estatisticas"]["batidas"] == 1


def test_mesmo_obstaculo_so_bate_uma_vez():
    cone = {"tipo": "cone", "faixa": 1, "dist": 30, "linha": 0}
    estado, rng = _estado_correndo([cone])

    for _ in range(10):
        partida.atualizar_estado(estado, 1 / 60, ACELERANDO, rng)

    assert estado["estatisticas"]["batidas"] == 1


def test_obstaculo_em_outra_faixa_nao_atinge_o_jogador():
    cone = {"tipo": "cone", "faixa": 3, "dist": 30, "linha": 0}
    estado, rng = _estado_correndo([cone])

    for _ in range(10):
        partida.atualizar_estado(estado, 1 / 60, ACELERANDO, rng)

    assert estado["estatisticas"]["batidas"] == 0


def test_bateria_da_impulso_ao_jogador_mas_a_ia_ignora():
    bateria = {"tipo": "bateria", "faixa": 1, "dist": 20, "linha": 0}
    estado, rng = _estado_correndo([bateria])
    estado["jogador"]["vel"] = 100
    estado["ia"]["vel"] = 100
    estado["ia"]["dist"] = 20  # a IA passa pela mesma bateria, na mesma faixa

    partida.atualizar_estado(estado, 1 / 60, ACELERANDO, rng)

    assert estado["jogador"]["impulso"] > 0
    assert estado["estatisticas"]["baterias"] == 1
    assert estado["ia"]["impulso"] == 0


# ------------------------------------------------------------------ IA rival
def _linha_com_cone_na_faixa_da_ia():
    return [{"tipo": "cone", "faixa": 1, "dist": 200, "linha": 0}]


def test_ia_com_sensor_perfeito_troca_de_faixa(monkeypatch):
    monkeypatch.setitem(RODADAS[0], "erro_sensor", 0.0)
    estado, rng = _estado_correndo(_linha_com_cone_na_faixa_da_ia())

    partida.mover_ia(estado, 1 / 60, rng)

    assert estado["ia"]["faixa_alvo"] != 1
    assert estado["ia"]["percepcao"][0] is True


def test_ia_com_sensor_falho_nao_percebe_e_continua_na_faixa(monkeypatch):
    monkeypatch.setitem(RODADAS[0], "erro_sensor", 1.0)
    estado, rng = _estado_correndo(_linha_com_cone_na_faixa_da_ia())

    partida.mover_ia(estado, 1 / 60, rng)

    assert estado["ia"]["faixa_alvo"] == 1
    assert estado["ia"]["percepcao"][0] is False


def test_ia_cega_bate_e_gera_aviso_de_falha_do_sensor(monkeypatch):
    monkeypatch.setitem(RODADAS[0], "erro_sensor", 1.0)
    estado, rng = _estado_correndo(_linha_com_cone_na_faixa_da_ia())
    estado["ia"]["dist"] = 190
    estado["ia"]["vel"] = 200

    partida.atualizar_estado(estado, 1 / 60, PARADO, rng)

    assert estado["estatisticas"]["batidas_ia"] == 1
    assert any("não detectou" in aviso["texto"] for aviso in estado["avisos"])


# ------------------------------------------------------------------ assistente de rota
def test_assistente_sugere_faixa_livre_quando_confiavel(monkeypatch):
    monkeypatch.setitem(RODADAS[0], "confiabilidade_assistente", 1.0)
    estado, rng = _estado_correndo(_linha_com_cone_na_faixa_da_ia())

    partida.atualizar_assistente(estado, rng)

    sugestao = estado["sugestao"]
    assert sugestao["faixa"] != 1
    assert sugestao["correta"] is True
    assert estado["estatisticas"]["sugestoes"] == 1
    assert estado["estatisticas"]["sugestoes_erradas"] == 0


def test_assistente_com_erro_sugere_a_faixa_do_obstaculo_e_conta_o_erro(monkeypatch):
    monkeypatch.setitem(RODADAS[0], "confiabilidade_assistente", 0.0)
    estado, rng = _estado_correndo(_linha_com_cone_na_faixa_da_ia())

    partida.atualizar_assistente(estado, rng)

    assert estado["sugestao"]["faixa"] == 1
    assert estado["sugestao"]["correta"] is False
    assert estado["estatisticas"]["sugestoes_erradas"] == 1


def test_assistente_nao_refaz_a_sugestao_para_a_mesma_linha():
    estado, rng = _estado_correndo(_linha_com_cone_na_faixa_da_ia())

    partida.atualizar_assistente(estado, rng)
    partida.atualizar_assistente(estado, rng)

    assert estado["estatisticas"]["sugestoes"] == 1


def test_mensagem_do_assistente_depende_dos_erros():
    assert partida.mensagem_assistente({"sugestoes": 0, "sugestoes_erradas": 0}) == ""
    assert "acertou" in partida.mensagem_assistente({"sugestoes": 8, "sugestoes_erradas": 0})
    assert "errou 2 de 8" in partida.mensagem_assistente({"sugestoes": 8, "sugestoes_erradas": 2})


# ------------------------------------------------------------------ fim de round e de partida
def test_jogador_cruza_a_chegada_e_vence_o_round():
    estado, rng = _estado_correndo(melhor_tempo=0)
    estado["jogador"]["dist"] = DISTANCIA_PISTA - 1
    estado["jogador"]["vel"] = 200
    estado["tempo_round"] = 20.0

    partida.atualizar_estado(estado, 0.1, ACELERANDO, rng)

    assert estado["vencedor_round"] == "jogador"
    assert estado["vitorias"] == {"jogador": 1, "ia": 0}
    assert estado["fase"] == partida.FASE_FIM_ROUND
    assert estado["novo_recorde"] is True
    assert estado["salvar_pendente"] is True
    assert estado["melhor_tempo"] == estado["tempo_vitoria_ms"] > 0


def test_tempo_pior_que_o_recorde_nao_o_substitui():
    estado, rng = _estado_correndo(melhor_tempo=1000)
    estado["jogador"]["dist"] = DISTANCIA_PISTA
    estado["tempo_round"] = 30.0

    partida.atualizar_estado(estado, 0.1, ACELERANDO, rng)

    assert estado["melhor_tempo"] == 1000
    assert estado["novo_recorde"] is False
    assert estado["salvar_pendente"] is False


def test_ia_vence_o_round_quando_chega_primeiro():
    estado, rng = _estado_correndo()
    estado["ia"]["dist"] = DISTANCIA_PISTA

    partida.atualizar_estado(estado, 0.1, PARADO, rng)

    assert estado["vencedor_round"] == "ia"
    assert estado["vitorias"] == {"jogador": 0, "ia": 1}
    assert estado["fase"] == partida.FASE_FIM_ROUND


def test_enter_no_fim_do_round_comeca_o_proximo_com_pista_nova():
    estado, rng = _estado_correndo()
    estado["ia"]["dist"] = DISTANCIA_PISTA
    partida.atualizar_estado(estado, 0.1, PARADO, rng)

    partida.avancar_fase(estado, rng)

    assert estado["indice_round"] == 1
    assert estado["fase"] == partida.FASE_CONTAGEM
    assert estado["jogador"]["dist"] == 0
    assert estado["vitorias"] == {"jogador": 0, "ia": 1}  # o placar e mantido


def test_partida_termina_quando_alguem_vence_dois_rounds():
    estado, rng = _estado_correndo()
    estado["vitorias"]["jogador"] = ROUNDS_PARA_VENCER - 1
    estado["jogador"]["dist"] = DISTANCIA_PISTA

    partida.atualizar_estado(estado, 0.1, ACELERANDO, rng)

    assert estado["vencedor_partida"] == "jogador"
    assert estado["fase"] == partida.FASE_FIM_PARTIDA


def test_derrota_quando_a_ia_vence_dois_rounds():
    estado, rng = _estado_correndo()
    estado["vitorias"]["ia"] = ROUNDS_PARA_VENCER - 1
    estado["ia"]["dist"] = DISTANCIA_PISTA

    partida.atualizar_estado(estado, 0.1, PARADO, rng)

    assert estado["vencedor_partida"] == "ia"
    assert estado["fase"] == partida.FASE_FIM_PARTIDA


def test_enter_no_fim_da_partida_reinicia_tudo():
    estado, rng = _estado_correndo()
    estado["vitorias"]["ia"] = ROUNDS_PARA_VENCER - 1
    estado["indice_round"] = 2
    estado["ia"]["dist"] = DISTANCIA_PISTA
    partida.atualizar_estado(estado, 0.1, PARADO, rng)

    partida.avancar_fase(estado, rng)

    assert estado["fase"] == partida.FASE_CONTAGEM
    assert estado["indice_round"] == 0
    assert estado["vitorias"] == {"jogador": 0, "ia": 0}
    assert estado["vencedor_partida"] is None


def test_jogador_parado_sempre_perde_o_round():
    """A IA corre sozinha e chega ao fim da pista em tempo razoavel."""
    for indice in range(len(RODADAS)):
        estado = partida.criar_estado()
        rng = random.Random(indice)
        estado["indice_round"] = indice
        partida.preparar_round(estado, rng)

        quadros = 0
        while estado["fase"] in (partida.FASE_CONTAGEM, partida.FASE_CORRENDO):
            partida.atualizar_estado(estado, 1 / 60, PARADO, rng)
            quadros += 1
            assert quadros < 60 * 120  # no maximo 2 minutos

        assert estado["vencedor_round"] == "ia"
