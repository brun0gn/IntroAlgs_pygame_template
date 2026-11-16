# Proposta Inicial do Jogo

Este documento deve ser preenchido pelo grupo na etapa inicial do projeto.

A proposta deve apresentar uma ideia simples, clara e viável para ser desenvolvida com **Python e Pygame** dentro do prazo disponível. Consulte o enunciado publicado no Canvas para conhecer o eixo temático e as orientações vigentes.

## 1. Nome provisório do jogo

Informe o nome provisório do jogo.

**Nome: **

> Corrida dos PUCAmigos

## 2. Integrantes do grupo

- Nome 1: Joaquim de Assis Santana
- Nome 2: Bruno Gonçalves Belo
- Nome 3: Rafael Andrade Claudino
- Nome 4: Heitor Leonardo Leal

## 3. Tema escolhido

Indique qual tema específico o grupo escolheu **dentro do eixo temático definido no enunciado**.

**Tema:**

> Corrida e mobilidade urbana.

**Como esse tema se relaciona com o jogo?** Explique brevemente (2 a 4 linhas) como ele aparecerá nos objetivos, nas regras ou nos desafios, e não apenas nas imagens ou no cenário.

> A corrida acontece em uma cidade, e o jogador precisa escolher bem o caminho: coletar itens de energia limpa (ex.: bateria) dá velocidade extra, enquanto poças de óleo e poluição atrapalham. O inimigo ignora esses itens, então o tema aparece nas regras e nas decisões do jogo, não só no cenário.

## 4. Tipo de jogo

Indique o estilo do jogo. Exemplos: desviar de obstáculos, coleta de itens, labirinto, perguntas e respostas, memória, Pong, Snake, Breakout, corrida ou sobrevivência simples.

**Tipo escolhido:**

> Corrida 2D com visão de cima, em formato de duelo contra um oponente controlado pelo computador.

## 5. Descrição geral do jogo

Explique, em poucas linhas, como o jogo funcionará. O que aparece na tela? O que o jogador controla? O que ele precisa fazer e quais desafios encontrará?

**Descrição:**

> O jogador e o inimigo correm lado a lado em uma pista com obstáculos e itens. O jogador controla o carro, desvia dos obstáculos e coleta itens de impulso para chegar à linha de chegada antes do inimigo. A partida tem 3 rounds, e a cada round a pista fica um pouco mais difícil (mais obstáculos e inimigo mais rápido).

## 6. Objetivo do jogador

Descreva o objetivo principal. Por exemplo: coletar itens, sobreviver por determinado tempo, chegar ao final de um percurso ou completar desafios.

**Objetivo:**

> Vencer o inimigo em pelo menos 2 dos 3 rounds, cruzando a linha de chegada na frente dele.

## 7. Regras principais

Liste até cinco regras que expliquem o funcionamento do jogo. Exemplos: o jogador começa com três vidas; acertos somam pontos; colisões retiram vidas.

- Regra 1: A partida tem 3 rounds, e vence o round quem cruzar a linha de chegada primeiro.
- Regra 2: Bater em um obstáculo reduz a velocidade do jogador por alguns segundos.
- Regra 3: Coletar um item de impulso aumenta a velocidade temporariamente.
- Regra 4: O inimigo corre sozinho, com velocidade que aumenta a cada round.
- Regra 5: Cada round vencido vale 1 ponto, e o jogador que chegar a 2 pontos vence a partida.

## 8. Condição de vitória

Explique como o jogador vence ou conclui a partida. Exemplos: alcançar uma pontuação, finalizar uma fase ou completar todas as tarefas.

**Condição de vitória:**

> Vencer 2 dos 3 rounds contra o inimigo.

## 9. Condição de derrota ou encerramento

Explique quando a partida termina ou como o jogador perde. Exemplos: esgotar as vidas, acabar o tempo ou atingir o limite de erros.

**Condição de derrota ou encerramento:**

> O jogador perde se o inimigo vencer 2 rounds. A partida também termina após o 3º round, com a tela de resultado e a opção de jogar de novo.

## 10. Elementos previstos no jogo

Descreva brevemente os elementos mais importantes, sem precisar detalhar a implementação.

- **Personagem ou elemento principal: carro do jogador.**
- **Obstáculos ou desafios: cones, poças de óleo e buracos na pista; carro inimigo competindo.**
- **Itens ou objetos de interação (se houver): baterias/itens de impulso que dão velocidade extra.**
- **Pontuação, vidas, tempo ou progresso: placar de rounds (0 a 2), barra de progresso da corrida e cronômetro do round.**

## 11. Controles previstos

Informe como o jogador vai interagir com o jogo (por exemplo, setas para movimentar, espaço para agir ou mouse para selecionar).

**Controles:**

> Setas (ou A/D) para mover o carro para os lados e acelerar/frear; Enter para iniciar o round e reiniciar a partida; Esc para sair.

## 12. Principais dificuldades esperadas

Cite até três dificuldades que o grupo espera enfrentar. Exemplos: movimentação, colisões, controle de tempo, testes ou uso do GitHub.

- Dificuldade 1: Detectar colisões com obstáculos e itens.
- Dificuldade 2: Fazer o inimigo correr de forma justa e equilibrar a dificuldade entre os rounds.
- Dificuldade 3: Organizar o trabalho em grupo no GitHub, evitando conflitos entre os códigos.

## 13. Escopo mínimo para a entrega final

Descreva a **versão mais simples que já seria jogável**, com as interações e regras essenciais. Evite planejar funcionalidades demais.

**Escopo mínimo:**

> Uma pista simples com rolagem, o carro do jogador com movimento lateral, um inimigo com velocidade própria, alguns obstáculos, a linha de chegada, o placar dos 3 rounds e as telas de vitória e derrota. Tudo com formas e imagens simples.

## 14. Possíveis melhorias, caso haja tempo

Liste até três funcionalidades extras para implementar somente depois que a versão mínima estiver funcionando. Exemplos: sons, fases, ranking, animações ou menu inicial.

- Melhoria 1: Sons (motor, colisão, vitória) e música de fundo.
- Melhoria 2: Menu inicial com escolha de dificuldade.
- Melhoria 3: Pistas diferentes em cada round, com cenários e animações.
