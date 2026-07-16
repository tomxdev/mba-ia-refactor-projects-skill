"""Validação central de produto — fonte única de verdade (criar e atualizar)."""

CATEGORIAS_VALIDAS = [
    "informatica",
    "moveis",
    "vestuario",
    "geral",
    "eletronicos",
    "livros",
]


def validate_produto(dados, checar_categoria=True):
    """Retorna (campos_normalizados, erro). Se erro != None, campos é None."""
    if not dados:
        return None, "Dados inválidos"
    for campo in ("nome", "preco", "estoque"):
        if campo not in dados:
            return None, f"{campo.capitalize()} é obrigatório"

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", "geral")

    if preco < 0:
        return None, "Preço não pode ser negativo"
    if estoque < 0:
        return None, "Estoque não pode ser negativo"
    if len(nome) < 2:
        return None, "Nome muito curto"
    if len(nome) > 200:
        return None, "Nome muito longo"
    if checar_categoria and categoria not in CATEGORIAS_VALIDAS:
        return None, "Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS)

    return {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "estoque": estoque,
        "categoria": categoria,
    }, None
