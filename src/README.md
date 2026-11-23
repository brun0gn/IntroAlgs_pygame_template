# Código-fonte (`src`)

Esta pasta contém os módulos principais do jogo.

## Arquivos

- `jogo.py`: loop principal, eventos e leitura do teclado.
- `partida.py`: estado da partida (fases, rounds, carros, colisões, IA rival e assistente de rota). Não desenha nada.
- `funcoes.py`: funções pequenas de lógica (física, geração da pista, decisões da IA, regras). É o que mais é testado.
- `desenho.py`: pistas, HUD, menu e telas de resultado.
- `sprites.py`: sprites desenhados por código e a função `pegar_sprite()` (recorte de spritesheet, do template).
- `dados.py`: leitura e gravação do recorde (melhor tempo).
- `config.py`: constantes globais (tela, cores, física, rodadas, caminhos).

## Fluxo de um quadro

1. `jogo.py` lê eventos e teclas (`ler_comandos`).
2. `partida.atualizar_estado` move os carros, trata colisões e verifica a chegada.
3. `desenho.desenhar_cena` desenha o estado atual.

## Dica de evolução

Quando o projeto crescer, mantenha módulos pequenos e separados por responsabilidade. Regras do jogo vão em `funcoes.py`/`partida.py` (testáveis), e tudo que usa a tela vai em `desenho.py`.
