# Corrida dos PUCAmigos

Projeto final da disciplina de Introdução a Algoritmos/Programação, desenvolvido com Python e Pygame.

**Tema:** Inteligência Artificial no Cotidiano: Aplicações e Uso Responsável.
**Recorte do grupo:** mobilidade inteligente, com carros autônomos e assistentes de rota.

> **Status: Entrega 2 (versão parcial executável).** O jogo já abre, roda e pode ser jogado do início ao fim (3 rounds, vitória e derrota). O que ainda falta está na seção [Próximos passos](#próximos-passos).

## Integrantes do grupo

- Joaquim de Assis Santana
- Bruno Gonçalves Belo
- Heitor Leonardo Leal
- Rafael Andrad Claudino

## Descrição do jogo

Corrida 2D com visão de cima, em **tela dividida**: à esquerda fica a pista do jogador, à direita a pista do **carro autônomo (IA)**. As duas pistas têm exatamente os mesmos obstáculos e baterias. A partida tem 3 rounds, e a cada round a pista fica mais difícil.

O tema de IA aparece nas regras, e não só no cenário:

- **O rival é um carro autônomo com sensor imperfeito.** Ele detecta obstáculos dentro de um alcance e desvia sozinho, mas às vezes o sensor falha e ele bate. No painel dele, caixas **verdes** mostram o que foi detectado e caixas **vermelhas** mostram o que o sensor não viu.
- **O jogador tem um assistente de rota (IA).** Ele destaca em verde a faixa que sugere para a próxima fileira de obstáculos, mas pode errar (e a confiança dele cai a cada round). Quem segue a sugestão sem olhar a pista se dá mal. É a lição de **confiabilidade e análise crítica**: a IA ajuda, mas a decisão final é de quem dirige.
- **Baterias** (energia limpa) dão impulso de velocidade. Cones, poças de óleo e buracos fazem o carro perder velocidade. A IA rival ignora as baterias.

## Objetivo do jogador

Vencer o carro autônomo em **2 dos 3 rounds**, cruzando a linha de chegada antes dele.

## Regras do jogo

- Cada round é uma corrida de 700 m. Vence o round quem cruzar a linha de chegada primeiro.
- Bater em um obstáculo reduz a velocidade na hora e limita a velocidade máxima por alguns segundos.
- Pegar uma bateria dá velocidade extra por 2,5 segundos.
- A cada round a IA fica mais rápida e o sensor dela mais preciso, mas a pista fica mais cheia e o assistente de rota menos confiável.
- Cada round vencido vale 1 ponto. Quem chegar a 2 pontos vence a partida.
- Ao fim de cada round aparecem o resultado, as estatísticas (baterias, batidas, erros do assistente) e uma dica de uso responsável de IA.
- O **melhor tempo** de um round vencido é gravado em `data/recorde.txt`.

## Controles

- Seta esquerda / **A**: mover para a esquerda
- Seta direita / **D**: mover para a direita
- Seta para cima / **W**: acelerar
- Seta para baixo / **S**: frear
- **Enter**: começar a partida, avançar para o próximo round e jogar de novo
- **Esc**: sair do jogo

## Como executar o projeto

```bash
git clone LINK_DO_REPOSITORIO
cd NOME_DA_PASTA
pip install -r requirements.txt
python main.py
```

> **Sobre o `pygame-ce`:** o `requirements.txt` usa o `pygame-ce` (Community Edition) no lugar do `pygame`, porque o `pygame` comum não tem versão pronta para Python 3.14 e a instalação falha ao compilar. O `pygame-ce` é compatível e o código continua com `import pygame`. Não instale os dois ao mesmo tempo no mesmo ambiente.

## Como executar os testes

```bash
python -m pytest
```

## Estrutura do projeto

- `main.py`: ponto de entrada da aplicação.
- `src/`: código-fonte principal do jogo.
  - `jogo.py`: loop principal (eventos, atualização e desenho) e leitura do teclado.
  - `partida.py`: estado da partida, rounds, colisões, IA rival e assistente de rota (sem desenho).
  - `funcoes.py`: funções de lógica pequenas e testáveis (física, geração da pista, decisões da IA, regras).
  - `desenho.py`: tudo o que aparece na tela (pistas, HUD, menu e resultados).
  - `sprites.py`: sprites desenhados por código (carros, cone, óleo, buraco, bateria).
  - `dados.py`: leitura e gravação do recorde em arquivo.
  - `config.py`: constantes (tela, física, rodadas e caminhos).
- `assets/`: imagens, fontes e sons (por enquanto o jogo usa só formas desenhadas por código).
- `data/`: arquivos persistentes (recorde).
- `tests/`: testes unitários com `pytest`.
- `docs/`: documentação do projeto, incluindo a proposta.

## O que já funciona (Entrega 2)

- Janela do Pygame, loop principal e tela inicial com regras.
- Corrida completa em tela dividida, com controle do carro, aceleração, freio e movimento lateral.
- Obstáculos, baterias, penalidade de velocidade e impulso.
- Carro autônomo rival com sensor que pode falhar, e assistente de rota que pode errar (mecânica temática).
- Placar de rounds, cronômetro, barra de progresso, velocidade e diferença entre os carros.
- Vitória, derrota e opção de jogar de novo; recorde de melhor tempo salvo em arquivo.
- Testes automatizados para a lógica (`pytest`).

## Próximos passos

- Sons (motor, batida, vitória) e música.
- Menu com escolha de dificuldade.
- Pistas diferentes em cada round, com cenários e animações.
- Ajustar o equilíbrio da dificuldade com mais testes de jogo.

## Decisões técnicas

- O código usa **funções e dicionários** (sem classes), como visto na disciplina. A lógica da partida fica separada do desenho, o que permite testar as regras sem abrir janela.
- O movimento usa o tempo de cada quadro (`dt`), então a velocidade do jogo não depende do FPS.
- O "mundo" é uma pista vertical: cada carro tem uma distância percorrida, e a tela mostra os objetos em relação a ela.
- Pista, rival e assistente usam sorteio (`random`). Os testes passam sementes fixas para ter resultados repetíveis.
- Os sprites são formas simples desenhadas por código, conforme o escopo da proposta. `assets/imagens/spritesheet.bmp` e `pegar_sprite()` vêm do template e ficam disponíveis para quando o grupo quiser trocar por imagens.
