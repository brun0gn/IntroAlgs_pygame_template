from collections import defaultdict

import pygame

from src import partida
from src.jogo import ler_comandos, montar_titulo_janela


def _teclas(*pressionadas):
    """Simula o resultado de pygame.key.get_pressed() com apenas algumas teclas ativas."""
    teclas = defaultdict(bool)
    for tecla in pressionadas:
        teclas[tecla] = True
    return teclas


def test_setas_e_wasd_geram_os_mesmos_comandos():
    assert ler_comandos(_teclas(pygame.K_LEFT))["esquerda"] is True
    assert ler_comandos(_teclas(pygame.K_a))["esquerda"] is True
    assert ler_comandos(_teclas(pygame.K_RIGHT))["direita"] is True
    assert ler_comandos(_teclas(pygame.K_d))["direita"] is True
    assert ler_comandos(_teclas(pygame.K_UP))["acelerar"] is True
    assert ler_comandos(_teclas(pygame.K_w))["acelerar"] is True
    assert ler_comandos(_teclas(pygame.K_DOWN))["frear"] is True
    assert ler_comandos(_teclas(pygame.K_s))["frear"] is True


def test_sem_teclas_nenhum_comando_fica_ativo():
    assert not any(ler_comandos(_teclas()).values())


def test_titulo_da_janela_mostra_round_e_placar():
    estado = partida.criar_estado()
    assert montar_titulo_janela(estado) == "Corrida dos PUCAmigos"

    estado["fase"] = partida.FASE_CORRENDO
    estado["indice_round"] = 1
    estado["vitorias"] = {"jogador": 1, "ia": 0}
    titulo = montar_titulo_janela(estado)
    assert "Round 2/3" in titulo
    assert "Você 1 x 0 IA" in titulo
