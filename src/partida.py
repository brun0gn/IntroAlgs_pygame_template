# Estado e regras da partida: rounds, carros, colisões, IA rival e assistente de rota.
# Este módulo não desenha nada e não lê o teclado, então pode ser testado sem janela.
from src.config import (
    ALCANCE_ASSISTENTE,
    ALCANCE_SENSOR,
    CARRO_ALTURA,
    CARRO_LARGURA,
    DICAS_IA,
    DISTANCIA_PISTA,
    DURACAO_CONTAGEM,
    FATOR_BATIDA,
    N_FAIXAS,
    RODADAS,
    ROUNDS_PARA_VENCER,
    TIPOS_OBJETO,
    TOTAL_ROUNDS,
    VEL_LATERAL,
    VEL_LATERAL_IA,
    VEL_MAX,
    VERDE,
    VERMELHO,
    AMARELO,
)
from src.funcoes import (
    atualizar_melhor_tempo,
    calcular_velocidade,
    centro_da_faixa,
    decidir_vencedor_round,
    e_obstaculo,
    escolher_faixa_livre,
    faixa_do_x,
    faixas_bloqueadas,
    gerar_pista,
    limitar_valor,
    limites_x_carro,
    percebeu_obstaculo,
    proximo_obstaculo,
    retangulo_no_mundo,
    sugerir_faixa,
    velocidade_maxima,
    vencedor_da_partida,
    verificar_colisao,
)

FASE_MENU = "menu"
FASE_CONTAGEM = "contagem"
FASE_CORRENDO = "correndo"
FASE_FIM_ROUND = "fim_round"
FASE_FIM_PARTIDA = "fim_partida"

DURACAO_AVISO = 1.8  # segundos que cada aviso fica na tela
MAX_AVISOS_POR_LADO = 2


# ------------------------------------------------------------------ criação do estado
def criar_carro(base, coleta_itens):
    """Cria o dicionário de um carro (jogador ou IA) na faixa 1."""
    faixa_inicial = 1
    return {
        "x": centro_da_faixa(faixa_inicial),
        "dist": 0.0,  # quanto já avançou na pista
        "vel": 0.0,
        "base": base,  # velocidade máxima sem impulso nem penalidade
        "impulso": 0.0,  # segundos restantes de impulso
        "penalidade": 0.0,  # segundos restantes de penalidade
        "coleta_itens": coleta_itens,
        "usados": set(),  # índices dos objetos que já interagiram com este carro
        "faixa_alvo": faixa_inicial,  # usado só pela IA
        "percepcao": {},  # linha -> a IA detectou? (usado só pela IA)
    }


def criar_estatisticas():
    """Contadores de um round, mostrados na tela de resultado."""
    return {"baterias": 0, "batidas": 0, "batidas_ia": 0, "sugestoes": 0, "sugestoes_erradas": 0}


def criar_estado(melhor_tempo=0):
    """Cria o estado inicial do jogo (tela de menu)."""
    return {
        "fase": FASE_MENU,
        "indice_round": 0,
        "vitorias": {"jogador": 0, "ia": 0},
        "melhor_tempo": melhor_tempo,
        "tempo_round": 0.0,
        "contagem": 0.0,
        "objetos": [],
        "jogador": criar_carro(VEL_MAX, True),
        "ia": criar_carro(RODADAS[0]["vel_ia"], False),
        "sugestao": None,
        "avisos": [],
        "estatisticas": criar_estatisticas(),
        "vencedor_round": None,
        "vencedor_partida": None,
        "tempo_vitoria_ms": 0,
        "novo_recorde": False,  # o último round vencido bateu o recorde?
        "salvar_pendente": False,  # avisa o loop principal que é preciso gravar o recorde
    }


def configuracao_do_round(estado):
    """Retorna o dicionário de configuração do round atual."""
    return RODADAS[min(estado["indice_round"], TOTAL_ROUNDS - 1)]


# ------------------------------------------------------------------ fluxo da partida
def iniciar_partida(estado, rng):
    """Zera o placar e começa o round 1."""
    estado["vitorias"] = {"jogador": 0, "ia": 0}
    estado["indice_round"] = 0
    estado["vencedor_partida"] = None
    preparar_round(estado, rng)


def preparar_round(estado, rng):
    """Gera uma pista nova, reposiciona os carros e inicia a contagem regressiva."""
    config_rodada = configuracao_do_round(estado)

    estado["objetos"] = gerar_pista(config_rodada, DISTANCIA_PISTA, rng)
    estado["jogador"] = criar_carro(VEL_MAX, True)
    estado["ia"] = criar_carro(config_rodada["vel_ia"], False)  # a IA ignora as baterias
    estado["sugestao"] = None
    estado["avisos"] = []
    estado["estatisticas"] = criar_estatisticas()
    estado["tempo_round"] = 0.0
    estado["vencedor_round"] = None
    estado["novo_recorde"] = False
    estado["contagem"] = DURACAO_CONTAGEM
    estado["fase"] = FASE_CONTAGEM


def avancar_fase(estado, rng):
    """Ação da tecla ENTER: começa a partida, o próximo round ou reinicia o jogo."""
    fase = estado["fase"]

    if fase in (FASE_MENU, FASE_FIM_PARTIDA):
        iniciar_partida(estado, rng)
    elif fase == FASE_FIM_ROUND:
        estado["indice_round"] += 1
        preparar_round(estado, rng)


def encerrar_round(estado, vencedor):
    """Registra o resultado do round e decide se a partida acabou."""
    estado["vencedor_round"] = vencedor
    estado["vitorias"][vencedor] += 1

    if vencedor == "jogador":
        tempo_ms = int(estado["tempo_round"] * 1000)
        estado["tempo_vitoria_ms"] = tempo_ms
        melhor, bateu = atualizar_melhor_tempo(estado["melhor_tempo"], tempo_ms)
        estado["melhor_tempo"] = melhor
        estado["novo_recorde"] = bateu
        estado["salvar_pendente"] = bateu

    estado["vencedor_partida"] = vencedor_da_partida(
        estado["vitorias"]["jogador"], estado["vitorias"]["ia"], ROUNDS_PARA_VENCER
    )
    if estado["vencedor_partida"] is None:
        estado["fase"] = FASE_FIM_ROUND
    else:
        estado["fase"] = FASE_FIM_PARTIDA


# ------------------------------------------------------------------ avisos na tela
def adicionar_aviso(estado, lado, texto, cor):
    """Cria uma mensagem curta que aparece sobre o painel do jogador ou da IA."""
    mesmos_lado = [a for a in estado["avisos"] if a["lado"] == lado]
    if len(mesmos_lado) >= MAX_AVISOS_POR_LADO:
        estado["avisos"].remove(mesmos_lado[0])  # descarta o aviso mais antigo
    estado["avisos"].append({"lado": lado, "texto": texto, "cor": cor, "tempo": DURACAO_AVISO})


def atualizar_avisos(estado, dt):
    """Diminui o tempo dos avisos e remove os que já expiraram."""
    for aviso in estado["avisos"]:
        aviso["tempo"] -= dt
    estado["avisos"] = [a for a in estado["avisos"] if a["tempo"] > 0]


# ------------------------------------------------------------------ movimento dos carros
def avancar_carro(carro, acelerando, freando, dt):
    """Atualiza velocidade, distância percorrida e temporizadores de um carro."""
    vel_max = velocidade_maxima(carro["base"], carro["impulso"] > 0, carro["penalidade"] > 0)
    carro["vel"] = calcular_velocidade(carro["vel"], acelerando, freando, vel_max, dt)
    carro["dist"] += carro["vel"] * dt
    carro["impulso"] = max(0.0, carro["impulso"] - dt)
    carro["penalidade"] = max(0.0, carro["penalidade"] - dt)


def mover_jogador(jogador, comandos, dt):
    """Aplica os comandos do jogador (acelerar, frear e mover para os lados)."""
    avancar_carro(jogador, comandos["acelerar"], comandos["frear"], dt)

    direcao = int(comandos["direita"]) - int(comandos["esquerda"])
    x_minimo, x_maximo = limites_x_carro()
    jogador["x"] = limitar_valor(jogador["x"] + direcao * VEL_LATERAL * dt, x_minimo, x_maximo)


def mover_ia(estado, dt, rng):
    """Carro autônomo: lê a pista com o sensor, escolhe uma faixa livre e acelera sozinho."""
    ia = estado["ia"]
    config_rodada = configuracao_do_round(estado)

    obstaculo = proximo_obstaculo(estado["objetos"], ia["dist"], ALCANCE_SENSOR)
    if obstaculo is not None:
        linha = obstaculo["linha"]

        # O sensor "decide" uma única vez se percebeu cada linha de obstáculos.
        if linha not in ia["percepcao"]:
            ia["percepcao"][linha] = percebeu_obstaculo(config_rodada["erro_sensor"], rng)

        if ia["percepcao"][linha]:
            bloqueadas = faixas_bloqueadas(estado["objetos"], linha)
            ia["faixa_alvo"] = escolher_faixa_livre(ia["faixa_alvo"], bloqueadas, N_FAIXAS)

    # Move-se suavemente em direção ao centro da faixa escolhida.
    passo = VEL_LATERAL_IA * dt
    diferenca = centro_da_faixa(ia["faixa_alvo"]) - ia["x"]
    ia["x"] += limitar_valor(diferenca, -passo, passo)

    avancar_carro(ia, True, False, dt)


# ------------------------------------------------------------------ colisões
def processar_colisoes(carro, objetos):
    """Verifica colisões do carro com a pista. Retorna a lista de objetos atingidos."""
    atingidos = []
    retangulo_carro = retangulo_no_mundo(carro["x"], carro["dist"], CARRO_LARGURA, CARRO_ALTURA)

    for indice, objeto in enumerate(objetos):
        if indice in carro["usados"]:
            continue
        if abs(objeto["dist"] - carro["dist"]) > 100:  # longe demais: nem testa
            continue

        info = TIPOS_OBJETO[objeto["tipo"]]
        if info["categoria"] == "item" and not carro["coleta_itens"]:
            continue

        x_objeto = centro_da_faixa(objeto["faixa"])
        retangulo_objeto = retangulo_no_mundo(x_objeto, objeto["dist"], info["largura"], info["altura"])
        if not verificar_colisao(retangulo_carro, retangulo_objeto):
            continue

        carro["usados"].add(indice)
        atingidos.append(objeto)

        if info["categoria"] == "obstaculo":
            # A batida reduz a velocidade na hora e limita a máxima por alguns segundos.
            carro["vel"] = min(carro["vel"], carro["base"] * FATOR_BATIDA)
            carro["penalidade"] = max(carro["penalidade"], info["penalidade"])
        else:
            carro["impulso"] = info["impulso"]

    return atingidos


def registrar_colisoes_jogador(estado, atingidos):
    """Atualiza estatísticas e avisos depois que o jogador atinge objetos."""
    for objeto in atingidos:
        if e_obstaculo(objeto):
            estado["estatisticas"]["batidas"] += 1
            adicionar_aviso(estado, "jogador", "Batida! Velocidade reduzida", VERMELHO)
        else:
            estado["estatisticas"]["baterias"] += 1
            adicionar_aviso(estado, "jogador", "Bateria! Impulso de energia limpa", VERDE)


def registrar_colisoes_ia(estado, atingidos):
    """Atualiza estatísticas e avisos depois que a IA atinge obstáculos."""
    for objeto in atingidos:
        estado["estatisticas"]["batidas_ia"] += 1
        if estado["ia"]["percepcao"].get(objeto["linha"], False):
            adicionar_aviso(estado, "ia", "IA errou a manobra", AMARELO)
        else:
            adicionar_aviso(estado, "ia", "IA não detectou o obstáculo!", VERMELHO)


# ------------------------------------------------------------------ assistente de rota (IA)
def atualizar_assistente(estado, rng):
    """Calcula a sugestão de faixa do assistente de rota para a próxima linha de obstáculos."""
    jogador = estado["jogador"]
    config_rodada = configuracao_do_round(estado)

    obstaculo = proximo_obstaculo(estado["objetos"], jogador["dist"], ALCANCE_ASSISTENTE)
    if obstaculo is None:
        estado["sugestao"] = None
        return

    sugestao = estado["sugestao"]
    if sugestao is not None and sugestao["linha"] == obstaculo["linha"]:
        return  # mantém a sugestão já feita para essa linha (não "pisca" a cada quadro)

    # A linha anterior acabou de passar: se o assistente errou, avisa o jogador.
    if sugestao is not None and not sugestao["correta"]:
        adicionar_aviso(estado, "jogador", "O assistente errou! Confira a pista", AMARELO)

    bloqueadas = faixas_bloqueadas(estado["objetos"], obstaculo["linha"])
    faixa, correta = sugerir_faixa(
        faixa_do_x(jogador["x"]),
        bloqueadas,
        N_FAIXAS,
        config_rodada["confiabilidade_assistente"],
        rng,
    )
    estado["sugestao"] = {
        "linha": obstaculo["linha"],
        "dist": obstaculo["dist"],
        "faixa": faixa,
        "correta": correta,
    }
    estado["estatisticas"]["sugestoes"] += 1
    if not correta:
        estado["estatisticas"]["sugestoes_erradas"] += 1


# ------------------------------------------------------------------ atualização por quadro
def atualizar_corrida(estado, dt, comandos, rng):
    """Um passo da corrida: move os carros, trata colisões e verifica a chegada."""
    estado["tempo_round"] += dt

    mover_jogador(estado["jogador"], comandos, dt)
    mover_ia(estado, dt, rng)

    registrar_colisoes_jogador(estado, processar_colisoes(estado["jogador"], estado["objetos"]))
    registrar_colisoes_ia(estado, processar_colisoes(estado["ia"], estado["objetos"]))
    atualizar_assistente(estado, rng)

    vencedor = decidir_vencedor_round(
        estado["jogador"]["dist"], estado["ia"]["dist"], DISTANCIA_PISTA
    )
    if vencedor is not None:
        encerrar_round(estado, vencedor)


def atualizar_estado(estado, dt, comandos, rng):
    """Atualiza o jogo conforme a fase atual. Chamado uma vez por quadro."""
    atualizar_avisos(estado, dt)

    if estado["fase"] == FASE_CONTAGEM:
        estado["contagem"] -= dt
        if estado["contagem"] <= 0:
            estado["fase"] = FASE_CORRENDO
            adicionar_aviso(estado, "jogador", "VAI!", VERDE)
    elif estado["fase"] == FASE_CORRENDO:
        atualizar_corrida(estado, dt, comandos, rng)


# ------------------------------------------------------------------ textos do resultado
def mensagem_assistente(estatisticas):
    """Frase sobre o desempenho do assistente de rota no round (parte educativa)."""
    total = estatisticas["sugestoes"]
    erradas = estatisticas["sugestoes_erradas"]

    if total == 0:
        return ""
    if erradas == 0:
        return f"O assistente acertou as {total} sugestões, mas continue conferindo a pista!"
    return f"O assistente errou {erradas} de {total} sugestões. Confiar sem conferir custa tempo."


def dica_do_round(indice_round):
    """Escolhe uma dica de uso responsável de IA de acordo com o round."""
    return DICAS_IA[indice_round % len(DICAS_IA)]
