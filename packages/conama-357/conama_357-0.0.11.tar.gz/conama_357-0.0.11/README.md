# Resolução CONAMA 357-05

[![🐍 Publish Python distributions to PyPI](https://github.com/gaemapiracicaba/norma_res_conama_357-05/actions/workflows/publish-to-pypi.yml/badge.svg)](https://github.com/gaemapiracicaba/norma_res_conama_357-05/actions/workflows/publish-to-pypi.yml) <br>
[![🐍 Publish Python distributions to TestPyPI](https://github.com/gaemapiracicaba/norma_res_conama_357-05/actions/workflows/publish-to-test-pypi.yml/badge.svg)](https://github.com/gaemapiracicaba/norma_res_conama_357-05/actions/workflows/publish-to-test-pypi.yml)

<br>

Por meio da [Resolução CONAMA nº 357](https://www.icmbio.gov.br/cepsul/images/stories/legislacao/Resolucao/2005/res_conama_357_2005_classificacao_corpos_agua_rtfcda_altrd_res_393_2007_397_2008_410_2009_430_2011.pdf), de 17.03.2005, que *"dispõe sobre a classificação dos corpos de água e diretrizes ambientais para o seu enquadramento, bem como estabelece as condições e padrões de lançamento de efluentes, e dá outras providências"*, são apresentados os padrões de qualidade de águas interiores.

A Resolução sofreu algumas alterações, por exemplo pela Resolução CONAMA 430, que revogou o artigo 24, que trata de lançamento de efluentes em curso d´água (corpo receptor).

<br>

**Padrão de Qualidade em Águas Doces**

- Artigo 14: Curso d'água Classe 1
- Artigo 15: Curso d'água Classe 2
- Artigo 16: Curso d'água Classe 3
- Artigo 17: Curso d'água Classe 4

<br>

**Padrão de Qualidade em Águas Salinas**

- ...

<br>

**Padrão de Qualidade em Águas Salobras**

- ...

<br>

**Padrão de Lançamento**

- Artigo 34: Padrão de Lançamento

----

### Objetivo

O projeto objetiva disponibilizar os parâmetros de qualidade em formato tabular, adequado para utilização em análises computacionais.

<br>

----

### Como Instalar?

<br>

```bash
pip3 install conama-357 --upgrade
```

<br>

----

### Como Usar?

<br>

```python
from normas import conama_357

# Get Table
df_357, list_classes = conama_357.get_parameters()

# Filter Data by "Classe"
df_357, list_parametros = conama_357.filter_by_classe(df_357, classe='Classe 2')

# Filter Data by "Parâmetro"
dict_357 = conama_357.filter_by_parameters(df_357, parametro='Oxigênio Dissolvido')
print(dict_357)

# Filter Data by "Parâmetro", quando tem condições distintas!
dict_357 = conama_357.filter_by_parameters(df_357, parametro='Fósforo Total', condicao=1)
print(dict_357)
```

<br>

-----

### Testes

Caso queira testar, segue um [*Google Colab*](https://colab.research.google.com/drive/1pImzgGr7pQF5TkbA3WOSC-0qqFuojwiK?usp=sharing).

<br>

-----

### *TODO*

1. Compilar: Padrão de Qualidade para Classe 1, em Águas Doces onde ocorre pesca ou cultivo de organismo para fins de consumo intensivo (Artigo 14)
2. Compilar: Padrão de Qualidade para Classe 1, em Águas Salinas (Artigo 18)
3. Compilar: Padrão de Qualidade para Classe 2, em Águas Salinas (Artigo 19)
4. Compilar: Padrão de Qualidade para Classe 3, em Águas Salinas (Artigo 20)
5. Compilar: Padrão de Qualidade para Classe 1, em Águas Salobras (Artigo 21)
6. Compilar: Padrão de Qualidade para Classe 2, em Águas Salobras (Artigo 22)
7. Compilar: Padrão de Qualidade para Classe 3, em Águas Salobras (Artigo 23)
