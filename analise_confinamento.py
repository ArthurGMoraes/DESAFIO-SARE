import sys
import pandas as pd
import numpy as np

ARQUIVO = "data/confinamento_gado_de_corte.xlsb"

entradas = pd.read_excel(ARQUIVO, sheet_name="Entradas", engine="pyxlsb")
mortes = pd.read_excel(ARQUIVO, sheet_name="Mortes", engine="pyxlsb")
trat = pd.read_excel(ARQUIVO, sheet_name="Tratamentos", engine="pyxlsb")

total_rebanho = len(entradas)


# a) TAXA DE MORTALIDADE
def taxa_mortalidade(mortes, total_rebanho):
    print("\na) TAXA DE MORTALIDADE")

    total_mortes = len(mortes)
    taxa_mortalidade = round(100 * total_mortes / total_rebanho, 2)

    print(f"Total de animais no rebanho: {total_rebanho:}")
    print(f"Total de mortes: {total_mortes:}")
    print(f"Taxa de Mortalidade: {taxa_mortalidade}%")


# b) TAXA DE MORBIDADE
def taxa_morbidade(trat, total_rebanho):
    print("\nb) TAXA DE MORBIDADE")

    # exclui tratamento padrao
    trat_clinicos = trat[trat["motivo"] != "ENTRADA PADRAO"]

    # animais tratados != numero de tratamentos
    animais_tratados = trat_clinicos["sisbov"].nunique()
    taxa_morbidade = round(100 * animais_tratados / total_rebanho, 2)

    print(f"Animais unicos tratados por motivo clinico: {animais_tratados:}")
    print(f"Taxa de Morbidade: {taxa_morbidade}%")

    return trat_clinicos


# c) PREVALÊNCIA DE DOENÇAS
def prevalencia_doencas(mortes, trat_clinicos):
    print("\nc) PREVALENCIA DE DOENCAS")

    print("\nPor causa de MORTE (motivo_morte) - 10 mais frequentes")
    print(mortes["motivo_morte"].value_counts().head(10).to_frame())

    print("\nPor motivo de TRATAMENTO (clinico) - 10 mais frequentes")
    print(trat_clinicos["motivo"].value_counts().head(10).to_frame())


# d) FATORES DE RISCO
def fatores_de_risco(entradas, mortes, trat_clinicos):
    print("\nd) FATORES DE RISCO PARA MORTES E TRATAMENTOS")

    print("\nMortalidade por Raca (minimo 30 entradas)")
    tab = pd.DataFrame({
        "Entradas": entradas["Raca"].value_counts(),
        "Mortes": mortes["raca"].value_counts(),
    }).fillna(0)
    tab["Taxa Mortalidade (%)"] = (100 * tab["Mortes"] / tab["Entradas"]).round(2)
    print(tab[tab["Entradas"] >= 30].sort_values("Taxa Mortalidade (%)", ascending=False))

    print("\nMortalidade por Categoria Animal (minimo 30 entradas)")
    tab = pd.DataFrame({
        "Entradas": entradas["Categoria Animal"].astype(str).str.strip().str.upper().value_counts(),
        "Mortes": mortes["categoria"].astype(str).str.strip().str.upper().value_counts(),
    }).fillna(0)
    tab["Taxa Mortalidade (%)"] = (100 * tab["Mortes"] / tab["Entradas"]).round(2)
    print(tab[tab["Entradas"] >= 30].sort_values("Taxa Mortalidade (%)", ascending=False))

    print("\nMortalidade por Faixa de Peso de Entrada")
    bins = [0, 150, 200, 250, 300, 350, 400, np.inf]
    labels = ["<150", "150-200", "200-250", "250-300", "300-350", "350-400", "400+"]
    entradas["faixa_peso"] = pd.cut(entradas["Peso Entrada"], bins=bins, labels=labels)
    mortes["faixa_peso"] = pd.cut(mortes["peso"], bins=bins, labels=labels)
    tab = pd.DataFrame({
        "Entradas": entradas["faixa_peso"].value_counts().sort_index(),
        "Mortes": mortes["faixa_peso"].value_counts().sort_index(),
    }).fillna(0)
    tab["Taxa Mortalidade (%)"] = (100 * tab["Mortes"] / tab["Entradas"]).round(2)
    print(tab)

    print("\nDias em confinamento ate a morte (qtd_diarias)")
    print(mortes["qtd_diarias"].describe().round(1).to_frame())

    print("\nMotivos de tratamento com maior % de evolucao para obito (minimo 10 casos)")
    tab = pd.DataFrame({
        "qtd_tratamentos": trat_clinicos["motivo"].value_counts(),
        "evoluiu_morte": trat_clinicos.groupby("motivo")["status"]
            .apply(lambda s: round(100 * (s.str.upper() == "MORTO").sum() / len(s), 2)),
    }).dropna()
    print(tab[tab["qtd_tratamentos"] >= 10].sort_values("evoluiu_morte", ascending=False).head(10))


# f) FORNECEDOR DE MAIOR RISCO SANITÁRIO
def fornecedor_maior_risco(entradas, mortes, trat_clinicos):
    print("\nf) FORNECEDOR DE MAIOR RISCO SANITARIO")

    MIN_ANIMAIS = 30  # amostra mínima para taxa ser considerada confiável

    # animal tratado -> fornecedor por sisbov
    mapa_fornecedor = entradas.dropna(subset=["SISBOV"]).drop_duplicates("SISBOV") \
        .set_index("SISBOV")["Produtor Origem"]
    trat_clinicos = trat_clinicos.copy()
    trat_clinicos["fornecedor"] = trat_clinicos["sisbov"].map(mapa_fornecedor)

    tab_fornecedor = pd.DataFrame({
        "Total Entradas": entradas.groupby("Produtor Origem").size(),
        "Mortes": mortes.groupby("produtor_origem").size(),
        "Animais Tratados": trat_clinicos.groupby("fornecedor")["sisbov"].nunique(),
    }).fillna(0)

    tab_fornecedor.index = tab_fornecedor.index.astype(int)

    tab_fornecedor["Taxa Mortalidade (%)"] = (100 * tab_fornecedor["Mortes"] / tab_fornecedor["Total Entradas"]).round(2)
    tab_fornecedor["Taxa Morbidade (%)"] = (100 * tab_fornecedor["Animais Tratados"] / tab_fornecedor["Total Entradas"]).round(2)

    tab_relevante = tab_fornecedor[tab_fornecedor["Total Entradas"] >= MIN_ANIMAIS]

    print(f"(considerando apenas fornecedores com >= {MIN_ANIMAIS} animais entregues)\n")

    print("Top 10 por Taxa de Mortalidade")
    print(tab_relevante.sort_values("Taxa Mortalidade (%)", ascending=False).head(10))

    print("\nTop 10 por Taxa de Morbidade")
    print(tab_relevante.sort_values("Taxa Morbidade (%)", ascending=False).head(10))

    pior_mortalidade = tab_relevante["Taxa Mortalidade (%)"].idxmax()
    pior_morbidade = tab_relevante["Taxa Morbidade (%)"].idxmax()
    print(f"\nMaior risco por MORTALIDADE: fornecedor '{pior_mortalidade}' "
        f"({tab_relevante.loc[pior_mortalidade, 'Taxa Mortalidade (%)']}%)")
    print(f"Maior risco por MORBIDADE: fornecedor '{pior_morbidade}' "
        f"({tab_relevante.loc[pior_morbidade, 'Taxa Morbidade (%)']}%)")


def main():
    arquivo = sys.argv[1] if len(sys.argv) > 1 else ARQUIVO
    print(f"Usando arquivo: {arquivo}")
 
    pd.set_option("display.width", 140)
    pd.set_option("display.max_columns", 20)
 
    entradas = pd.read_excel(arquivo, sheet_name="Entradas", engine="pyxlsb")
    mortes = pd.read_excel(arquivo, sheet_name="Mortes", engine="pyxlsb")
    trat = pd.read_excel(arquivo, sheet_name="Tratamentos", engine="pyxlsb")
 
    total_rebanho = len(entradas)
 
    taxa_mortalidade(mortes, total_rebanho)
    trat_clinicos = taxa_morbidade(trat, total_rebanho)
    prevalencia_doencas(mortes, trat_clinicos)
    fatores_de_risco(entradas, mortes, trat_clinicos)
    fornecedor_maior_risco(entradas, mortes, trat_clinicos)
 
 
if __name__ == "__main__":
    main()