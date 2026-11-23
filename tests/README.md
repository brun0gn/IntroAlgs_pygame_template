# Testes

Esta pasta contem testes automatizados do projeto.

## Arquivos

- `test_logica.py`: funcoes puras de `src/funcoes.py` (fisica, geracao da pista, decisoes da IA, regras de round e partida).
- `test_partida.py`: fluxo da partida em `src/partida.py` (fases, colisoes, IA rival, assistente de rota, fim de round e de partida), sem abrir janela.
- `test_dados.py`: leitura e gravacao do recorde em `src/dados.py`.
- `test_jogo.py`: conversao de teclas em comandos e titulo da janela.

## Como executar

```bash
python -m pytest
```

## Boas praticas

- Crie testes para toda regra de pontuacao, vidas e condicoes de fim de jogo.
- Prefira funcoes pequenas e testaveis no modulo `src/funcoes.py`.
- Para testar sorteios, use `random.Random(semente)` ou valores extremos (0.0 e 1.0), assim o resultado e sempre o mesmo.
