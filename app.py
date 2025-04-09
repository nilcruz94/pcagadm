from flask import Flask, render_template, request

app = Flask(__name__)

# Tabela com aumento de 3,93% de 2024 já aplicado
# Valores originais da tabela (antes do reajuste de 2024):
# I – Fundamental: 2.476,28; 2.600,09; 2.730,10; 2.866,60; 3.009,93; 3.160,43; 3.318,45
# II – Ensino Médio ou Técnico: 2.730,10; 2.866,60; 3.009,93; 3.160,43; 3.318,45; 3.484,37
# III – Graduação: 2.948,51; 3.095,93; 3.250,73; 3.413,26; 3.583,93; 3.763,12
# IV – Pós-Graduação Lato Sensu: 3.184,39; 3.343,61; 3.510,79; 3.686,33; 3.870,64; 4.064,17
# V – Pós-Graduação Stricto-Sensu (Mestrado): 3.439,14; 3.611,09; 3.791,65; 3.981,23; 4.180,29; 4.389,31
# VI – Doutorado: 3.714,27; 3.899,98; 4.094,98; 4.299,73; 4.514,72; 4.740,45
# Aplicando um reajuste de 3,93% (multiplicador 1,0393) em cada valor:

tabela = {
    "I": {
        "G": 2573.60,  # 2.476,28 * 1,0393
        "F": 2702.27,  # 2.600,09 * 1,0393
        "E": 2837.39,  # 2.730,10 * 1,0393
        "D": 2979.26,  # 2.866,60 * 1,0393
        "C": 3128.22,  # 3.009,93 * 1,0393
        "B": 3284.64,  # 3.160,43 * 1,0393
        "A": 3448.87   # 3.318,45 * 1,0393
    },
    "II": {
        "F": 2837.39,  # 2.730,10 * 1,0393
        "E": 2979.26,  # 2.866,60 * 1,0393
        "D": 3128.22,  # 3.009,93 * 1,0393
        "C": 3284.64,  # 3.160,43 * 1,0393
        "B": 3448.87,  # 3.318,45 * 1,0393
        "A": 3621.31   # 3.484,37 * 1,0393 (aprox.)
    },
    "III": {
        "F": 3064.39,  # 2.948,51 * 1,0393 (aprox.)
        "E": 3217.60,  # 3.095,93 * 1,0393 (aprox.)
        "D": 3378.48,  # 3.250,73 * 1,0393 (aprox.)
        "C": 3547.40,  # 3.413,26 * 1,0393 (aprox.)
        "B": 3724.78,  # 3.583,93 * 1,0393 (aprox.)
        "A": 3910.01   # 3.763,12 * 1,0393 (aprox.)
    },
    "IV": {
        "F": 3309.54,  # 3.184,39 * 1,0393 (aprox.)
        "E": 3475.01,  # 3.343,61 * 1,0393 (aprox.)
        "D": 3648.76,  # 3.510,79 * 1,0393 (aprox.)
        "C": 3831.20,  # 3.686,33 * 1,0393 (aprox.)
        "B": 4022.76,  # 3.870,64 * 1,0393 (aprox.)
        "A": 4223.89   # 4.064,17 * 1,0393 (aprox.)
    },
    "V": {
        "F": 3574.30,  # 3.439,14 * 1,0393 (aprox.)
        "E": 3752.99,  # 3.611,09 * 1,0393 (aprox.)
        "D": 3940.66,  # 3.791,65 * 1,0393 (aprox.)
        "C": 4137.69,  # 3.981,23 * 1,0393 (aprox.)
        "B": 4344.58,  # 4.180,29 * 1,0393 (aprox.)
        "A": 4561.81   # 4.389,31 * 1,0393 (aprox.)
    },
    "VI": {
        "F": 3860.24,  # 3.714,27 * 1,0393 (aprox.)
        "E": 4053.25,  # 3.899,98 * 1,0393 (aprox.)
        "D": 4255.91,  # 4.094,98 * 1,0393 (aprox.)
        "C": 4468.71,  # 4.299,73 * 1,0393 (aprox.)
        "B": 4692.15,  # 4.514,72 * 1,0393 (aprox.)
        "A": 4926.75   # 4.740,45 * 1,0393 (aprox.)
    }
}

# Anos mínimos de carreira para cada Classe
classe_anos = {
    "G": 0,
    "F": 5,
    "E": 10,
    "D": 15,
    "C": 20,
    "B": 25,
    "A": 30
}

# Descrição dos níveis correspondentes
nivel_descricao = {
    "I": "Ensino Fundamental",
    "II": "Ensino Médio",
    "III": "Graduação",
    "IV": "Pós-Graduação Lato Sensu",
    "V": "Mestrado (Stricto Sensu)",
    "VI": "Doutorado (Stricto Sensu)"
}

def calcular_verocard(salario_total):
    """
    Calcula o desconto do benefício Verocard conforme faixas salariais:
      - Até R$ 3.699,40: desconto 0% (benefício integral de R$ 740,00).
      - De R$ 3.699,41 a R$ 4.587,24: desconto de 50%.
      - De R$ 4.587,25 a R$ 5.999,99: desconto de 63,5%.
      - Acima de R$ 6.000,00: desconto de 100% (benefício zerado).
    """
    beneficio = 740.00
    if salario_total <= 3699.40:
        return 0, beneficio
    elif 3699.41 <= salario_total <= 4587.24:
        return 50, beneficio * 0.5
    elif 4587.25 <= salario_total <= 5999.99:
        return 63.5, beneficio * (1 - 0.635)
    else:
        return 100, 0.00

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None

    if request.method == 'POST':
        nivel = request.form['nivel']
        classe = request.form['classe']
        quinquenios = int(request.form['quinquenios'])

        # Obtém o valor do dissídio extra (projetado), se informado; senão, 0.
        dissidio_extra_raw = request.form.get('dissidio_extra', '').replace(',', '.')
        dissidio_extra = float(dissidio_extra_raw) if dissidio_extra_raw else 0.0

        salario_base = tabela.get(nivel, {}).get(classe)

        if salario_base:
            # Calcula o valor do acréscimo do dissídio
            incremento_dissidio = salario_base * (dissidio_extra / 100)
            # Aplica o acréscimo ao salário base (que já considera o reajuste de 3,93% de 2024)
            salario_base_ajustado = salario_base + incremento_dissidio

            adicional = salario_base_ajustado * 0.05 * quinquenios
            tem_sexta_parte = quinquenios >= 4
            sexta_parte_valor = salario_base_ajustado * (1/6) if tem_sexta_parte else 0
            salario_total = salario_base_ajustado + adicional + sexta_parte_valor

            # Cálculo do Verocard
            desconto_perc, valor_liquido = calcular_verocard(salario_total)

            resultado = {
                "nivel": nivel,
                "nivel_descricao": nivel_descricao.get(nivel, ""),
                "classe": classe,
                "quinquenios": quinquenios,
                "anos_classe": classe_anos[classe],
                "dissidio_extra": dissidio_extra if dissidio_extra > 0 else None,
                "incremento_dissidio": f"R$ {incremento_dissidio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if dissidio_extra > 0 else None,
                "salario_base": f"R$ {salario_base_ajustado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "adicional": f"R$ {adicional:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "sexta_parte": f"R$ {sexta_parte_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if tem_sexta_parte else None,
                "salario_total": salario_total,
                "salario_total_formatado": f"R$ {salario_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "verocard_desconto": desconto_perc,
                "verocard_valor": f"R$ {valor_liquido:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            }

    return render_template('index.html', resultado=resultado)

if __name__ == '__main__':
    app.run(debug=True)
