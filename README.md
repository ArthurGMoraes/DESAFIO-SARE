# Análise de Dados — Confinamento de Gado de Corte

Script em Python para responder às questões a), b), c), d) e f) do desafio,
a partir da base `confinamento_gado_de_corte.xlsb` (abas `Entradas`, `Mortes`
e `Tratamentos`).

## Como rodar

### Requisitos

```bash
pip install pandas pyxlsb numpy
```

### Execução

Usando arquivo padrão: 
```bash
python analise_confinamento.py
```

Usando outro arquivo: 
```bash
python analise_confinamento.py novo_caminho.xlsb
```

Os resultados são impressos diretamente no terminal. Para redirecionar para um arquivo adicionar "> nome_do_arquivo.txt" ao final do comando.

## O que é analisado

**a) Taxa de Mortalidade**
Total de registros na aba `Mortes` dividido pelo total de animais na aba
`Entradas`.

**b) Taxa de Morbidade**
Animais únicos (por `sisbov`) que receberam algum tratamento na aba
`Tratamentos`, **excluindo** o motivo `ENTRADA PADRAO`.

**c) Prevalência de doenças**
As 10 causas de morte mais frequentes (`motivo_morte`, aba `Mortes`) e os
10 motivos de tratamento clínico mais frequentes (`motivo`, aba
`Tratamentos`, já excluindo `ENTRADA PADRAO`).

**d) Fatores de risco**
Cruzamentos para identificar o que mais influencia mortes/tratamentos:
- Taxa de mortalidade por raça (`Raca`)
- Taxa de mortalidade por categoria animal (`Categoria Animal`)
- Taxa de mortalidade por faixa de peso de entrada (`Peso Entrada`)
- Distribuição de dias em confinamento até a morte (`qtd_diarias`)
- Motivos de tratamento com maior percentual de evolução para óbito

Nos cruzamentos por grupo (raça, categoria), grupos com menos de 30 animais
são descartados para evitar taxas distorcidas por amostra pequena.

**f) Fornecedor de maior risco sanitário**
Mortes e tratamentos são ligados ao fornecedor de origem do animal
(`Produtor Origem`) via join pelo identificador único `sisbov`. São
calculadas duas taxas por fornecedor, mortalidade e morbidade, porque não
apontam necessariamente para o mesmo fornecedor: mortalidade é um evento raro
e mais sujeito a ruído estatístico, enquanto morbidade tem mais observações e
captura sinal de doença mais cedo. Só fornecedores com 30+ animais entregues
entram no ranking.

## Por que e) e g) não são analisados aqui

As perguntas e) *("Quais ações poderiam ser sugeridas para a melhoria dos
índices sanitários?")* e g) *("Quais outras informações poderiam ser
relevantes para coleta e análise?")* não correspondem a métricas calculáveis
a partir dos dados e portanto são desenvolvidas no documento com as respostas do desafio.