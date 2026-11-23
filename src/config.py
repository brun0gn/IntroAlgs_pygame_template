# Configurações centrais do jogo (tela, cores, física, rodadas e caminhos de arquivos).
import os

# Pasta raiz do projeto: assim o jogo funciona mesmo se for executado de outra pasta.
PASTA_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- tela
LARGURA_TELA = 800
ALTURA_TELA = 600
FPS = 60

TITULO_JOGO = "Corrida dos PUCAmigos"

# ---------------------------------------------------------------- cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (212, 212, 212)
CINZA_ESCURO = (60, 63, 70)
AZUL_JOGADOR = (45, 125, 235)
LARANJA_IA = (240, 140, 40)
VERDE = (60, 200, 110)
VERMELHO = (225, 70, 70)
AMARELO = (250, 205, 60)
COR_ASFALTO = (62, 64, 70)
COR_CALCADA = (150, 150, 145)
COR_FAIXA = (235, 235, 235)
COR_FUNDO_HUD = (28, 30, 38)
COR_PAINEL = (14, 16, 22, 215)  # com transparência (RGBA)

# Cores dos prédios que passam ao lado da pista (ambiente urbano).
CORES_PREDIOS = [(96, 108, 128), (122, 96, 96), (92, 120, 108), (128, 118, 84), (104, 92, 128)]
# (altura, índice da cor) – o padrão se repete conforme a pista avança.
PADRAO_PREDIOS = [(70, 0), (110, 1), (90, 2), (60, 3), (120, 4), (80, 1), (100, 0), (65, 2)]
ESPACO_PREDIOS = 140  # distância (em pixels do mundo) entre um prédio e o próximo

# ---------------------------------------------------------------- layout
ALTURA_HUD = 60
ALTURA_RODAPE = 40
ALTURA_PAINEL = ALTURA_TELA - ALTURA_HUD - ALTURA_RODAPE
LARGURA_PAINEL = LARGURA_TELA // 2
Y_CARRO = 390  # posição vertical do carro dentro do painel

# ---------------------------------------------------------------- pista
N_FAIXAS = 4
LARGURA_FAIXA = 76
MARGEM_PISTA = (LARGURA_PAINEL - N_FAIXAS * LARGURA_FAIXA) // 2
CARRO_LARGURA = 34
CARRO_ALTURA = 60

PX_POR_METRO = 10  # só para exibir distância/velocidade de forma amigável
DISTANCIA_PISTA = 7000  # tamanho de cada corrida (em pixels do mundo)
DISTANCIA_INICIAL_OBSTACULOS = 700  # trecho livre logo após a largada
DISTANCIA_FINAL_LIVRE = 500  # trecho livre antes da linha de chegada

# ---------------------------------------------------------------- física (px/s)
VEL_MAX = 320
ACELERACAO = 200
FREIO = 420
ATRITO = 90
VEL_LATERAL = 240
VEL_LATERAL_IA = 210

BONUS_IMPULSO = 110  # velocidade extra ao pegar uma bateria
DURACAO_IMPULSO = 2.5  # segundos
FATOR_PENALIDADE = 0.55  # fração da velocidade máxima enquanto está penalizado
FATOR_BATIDA = 0.35  # fração da velocidade máxima mantida logo após a batida

# ---------------------------------------------------------------- objetos da pista
# Cada tipo é um dicionário com as regras e o tamanho do objeto.
TIPOS_OBJETO = {
    "cone": {"categoria": "obstaculo", "largura": 30, "altura": 30, "penalidade": 1.2},
    "oleo": {"categoria": "obstaculo", "largura": 56, "altura": 40, "penalidade": 1.8},
    "buraco": {"categoria": "obstaculo", "largura": 50, "altura": 36, "penalidade": 2.2},
    "bateria": {"categoria": "item", "largura": 26, "altura": 36, "impulso": DURACAO_IMPULSO},
}
TIPOS_OBSTACULO = [nome for nome, info in TIPOS_OBJETO.items() if info["categoria"] == "obstaculo"]

# ---------------------------------------------------------------- IA do jogo
ALCANCE_SENSOR = 360  # até onde o carro autônomo "enxerga" à frente
ALCANCE_ASSISTENTE = 380  # até onde o assistente de rota analisa a pista
TOLERANCIA_LINHA = 40  # quanto um obstáculo ainda conta como "próximo" depois de passar

# ---------------------------------------------------------------- rodadas
# A dificuldade aumenta a cada round: IA mais rápida e sensor melhor, mas
# pista mais cheia e assistente de rota menos confiável.
RODADAS = [
    {
        "vel_ia": 255,
        "erro_sensor": 0.35,  # chance de o sensor da IA não perceber uma fileira de obstáculos
        "confiabilidade_assistente": 0.85,  # chance de a sugestão de rota estar correta
        "max_obstaculos_linha": 1,
        "espaco_linhas": 330,
        "chance_bateria": 0.30,
    },
    {
        "vel_ia": 285,
        "erro_sensor": 0.22,
        "confiabilidade_assistente": 0.75,
        "max_obstaculos_linha": 2,
        "espaco_linhas": 290,
        "chance_bateria": 0.28,
    },
    {
        "vel_ia": 310,
        "erro_sensor": 0.12,
        "confiabilidade_assistente": 0.65,
        "max_obstaculos_linha": 2,
        "espaco_linhas": 260,
        "chance_bateria": 0.25,
    },
]
TOTAL_ROUNDS = len(RODADAS)
ROUNDS_PARA_VENCER = TOTAL_ROUNDS // 2 + 1
DURACAO_CONTAGEM = 3.0  # segundos antes da largada

# ---------------------------------------------------------------- textos educativos
DICAS_IA = [
    "A IA pode errar. Use a sugestão como apoio e confira a informação antes de decidir.",
    "Sensores e câmeras falham com chuva, sombra ou sujeira: a supervisão humana continua importante.",
    "Quem usa o sistema continua responsável pela decisão final, mesmo com ajuda da IA.",
]

# ---------------------------------------------------------------- arquivos
# O recorde guarda o melhor tempo (em milissegundos) de um round vencido pelo jogador.
CAMINHO_RECORDE = os.path.join(PASTA_PROJETO, "data", "recorde.txt")
CAMINHO_SPRITES = os.path.join(PASTA_PROJETO, "assets", "imagens", "spritesheet.bmp")
