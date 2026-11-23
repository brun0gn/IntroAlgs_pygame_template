from src.dados import carregar_recorde, salvar_recorde


def test_salvar_e_carregar_recorde(tmp_path):
    caminho = tmp_path / "recorde.txt"

    assert salvar_recorde(str(caminho), 24350) is True
    assert carregar_recorde(str(caminho)) == 24350


def test_carregar_recorde_de_arquivo_inexistente_retorna_zero(tmp_path):
    assert carregar_recorde(str(tmp_path / "nao_existe.txt")) == 0


def test_carregar_recorde_de_arquivo_vazio_retorna_zero(tmp_path):
    caminho = tmp_path / "recorde.txt"
    caminho.write_text("", encoding="utf-8")

    assert carregar_recorde(str(caminho)) == 0


def test_carregar_recorde_de_conteudo_invalido_retorna_zero(tmp_path):
    caminho = tmp_path / "recorde.txt"
    caminho.write_text("abc", encoding="utf-8")

    assert carregar_recorde(str(caminho)) == 0


def test_salvar_recorde_cria_a_pasta_se_ela_nao_existir(tmp_path):
    caminho = tmp_path / "nova_pasta" / "recorde.txt"

    assert salvar_recorde(str(caminho), 1500) is True
    assert carregar_recorde(str(caminho)) == 1500
