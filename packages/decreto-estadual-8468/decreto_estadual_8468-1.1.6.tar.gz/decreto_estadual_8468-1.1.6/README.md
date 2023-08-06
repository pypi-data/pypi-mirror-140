# Decreto Estadual 8.468/1976

[![Publish Python 🐍 distributions 📦 to PyPI](https://github.com/gaemapiracicaba/norma_dec_8468-76/actions/workflows/publish-to-pypi.yml/badge.svg)](https://github.com/gaemapiracicaba/norma_dec_8468-76/actions/workflows/publish-to-pypi.yml)<br>
[![Publish Python 🐍 distributions 📦 to TestPyPI](https://github.com/gaemapiracicaba/norma_dec_8468-76/actions/workflows/publish-to-test-pypi.yml/badge.svg)](https://github.com/gaemapiracicaba/norma_dec_8468-76/actions/workflows/publish-to-test-pypi.yml)

<br>

Por meio do [Decreto Estadual 8.468](https://www.cetesb.sp.gov.br/Institucional/documentos/Dec8468.pdf), de 08.09.1976, que *"aprova o Regulamento da Lei n° 997, de 31 de maio de 1976, que dispõe sobre a prevenção e o controle da poluição do meio ambiente"*, são apresentados os padrões de qualidade de águas interiores e padrões de lançamento de efluentes.

A lei sofreu diversas alterações, sendo a última pelo Decreto Estadual 54.487/09.

<br>

**Padrão de Qualidade**

- Artigo 10: Cursos d'água Classe 1
- Artigo 11: Cursos d'água Classe 2
- Artigo 12: Cursos d'água Classe 3
- Artigo 13: Cursos d'água Classe 4

<br>

**Padrão de Lançamento**

- Artigo 18: Lançamento em curso d'água (corpo receptor)
- Artigo 19-A: Lançamento na Rede de Esgoto

<br>

----

### Objetivo

<br>

O projeto objetiva disponibilizar os parâmetros de qualidade em formato adequado para utilização em análises computacionais.

<br>

----

### Como Instalar?

<br>

```bash
pip3 install decreto-estadual-8468 --upgrade
```

<br>

----

### Como usar?

<br>

Para obter as informações da tabela, basta ajustar os parâmetros *classe* e o *parametro*.

```python
from normas import decreto_estadual_8468

# Get Table
df_8468, list_classes = decreto_estadual_8468.get_parameters()

# Filter Data by "Classe"
df_8468, list_parametros = decreto_estadual_8468.filter_by_classe(df_8468, classe='Classe 2')

# Filter Data by "Parâmetros"
dict_8468 = decreto_estadual_8468.filter_by_parameters(df_8468, parametro='Oxigênio Dissolvido')
print(dict_8468)
```

<br>

O resultado será um dicionário (*OrderedDict*) contendo as seguintes informações:

```python
{
 'tipo_padrao': 'qualidade',
 'padrao_qualidade': 'Classe 2',
 'parametro_descricao': 'Oxigênio Dissolvido',
 'parametro_sigla': 'OD',
 'valor_minimo_permitido': 5.0,
 'valor_maximo_permitido': nan,
 'unidade': 'mg/l ',
 'norma_referencia': 'Inciso V, Art. 11',
 'norma_texto': 'Oxigênio Dissolvido (OD), em qualquer amostra, não inferior a 5 mg/l (cinco miligramas por litro)'
}
 ```

<br>

Há mais uma função escrita para melhor compreender como fazer a avaliação do parâmetro. Isso pois existem parâmetros que busca-se minimizar a quantidade presente no ambiente (ex. poluentes), enquanto para outros parâmetros busca-se maximizar a quantidade presente no ambiente (ex. oxigênio dissolvido).

```python
# Set Tipo
decreto_estadual_8468.set_type_desconformidade(dict_8468)
```

<br>

O resultado é uma *string*, que pode ser de quatro tipos diferentes:

- **acima>desconforme**, só há desconformidade se estiver acima do *valor_maximo_permitido* (ex.: chumbo, fósforo, DBO. Quanto menos, melhor);
- **abaixo>desconforme**, só há desconformidade se estiver abaixo do *valor_minimo_permitido* (ex.: oxigênio dissolvido. Quanto mais, melhor);
- **abaixo_acima>desconforme**, qualquer coisa abaixo ou acima dos *valor_minimo_permitido* e *valor_maximo_permitido*, respectivamente, gera desconformidade (ex.: pH, de é adequado estar entre 6 e 9);
- **erro**, caso nenhuma das situações anteriores ocorrer (improvável!). Seria erro na tabulação ou no código.

<br>

Por fim, é possível avaliar um valor, confrontando o valor com o padrão de qualidade.
O resultado será uma *string*: **conforme** ou **desconforme**!

```python
# Avaliar
valor=10
evaluate_result(valor, dict_8468)
```
<br>

----

### Testes

<br>

Caso queira testar, segue um [*Google Colab*](https://colab.research.google.com/drive/1QZjsB6i8w_BAyMm3z4CB0_liSYOFQpdy?usp=sharing).

<br>

----

### *TODO*

1. <strike>Tabular Parâmetros de Lançamento (Art. 18 e 19)</strike>
2. <strike>Desenvolver função que teste um dado valor de um parâmetro, para uma classe de rio. Faz-se isso considerando o resultado de *set_type_desconformidade(dict_8468)*</strike>
3. <strike>Usar o resultado em OrderedDict</strike>
4. <strike>Remover *prints* do *evaluate_result*.</strike>
5. Desenvolver funções para usar os padrões de lançamento!
