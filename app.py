from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Tabela com aumento de 3,93% de 2024 já aplicado
tabela = {
    "I": {
        "G": 2573.60,
        "F": 2702.27,
        "E": 2837.39,
        "D": 2979.26,
        "C": 3128.22,
        "B": 3284.64,
        "A": 3448.87
    },
    "II": {
        "F": 2837.39,
        "E": 2979.26,
        "D": 3128.22,
        "C": 3284.64,
        "B": 3448.87,
        "A": 3621.31
    },
    "III": {
        "F": 3064.39,
        "E": 3217.60,
        "D": 3378.48,
        "C": 3547.40,
        "B": 3724.78,
        "A": 3910.01
    },
    "IV": {
        "F": 3309.54,
        "E": 3475.01,
        "D": 3648.76,
        "C": 3831.20,
        "B": 4022.76,
        "A": 4223.89
    },
    "V": {
        "F": 3574.30,
        "E": 3752.99,
        "D": 3940.66,
        "C": 4137.69,
        "B": 4344.58,
        "A": 4561.81
    },
    "VI": {
        "F": 3860.24,
        "E": 4053.25,
        "D": 4255.91,
        "C": 4468.71,
        "B": 4692.15,
        "A": 4926.75
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
    beneficio = 740.00
    if salario_total <= 3699.40:
        return 0, beneficio
    elif 3699.41 <= salario_total <= 4587.24:
        return 50, beneficio * 0.5
    elif 4587.25 <= salario_total <= 5999.99:
        return 63.5, beneficio * (1 - 0.635)
    else:
        return 100, 0.00

def analisar_poder_compra(salario_total):
    ipca_percent = 4.83  
    salario_minimo = 1518.00  
    salario_real = salario_total / (1 + ipca_percent / 100)
    qtd_minimos_nominal = salario_total / salario_minimo
    qtd_minimos_real = salario_real / salario_minimo
    return {
        "ipca_percent": ipca_percent,
        "salario_minimo": salario_minimo,
        "salario_real": salario_real,
        "qtd_minimos_nominal": qtd_minimos_nominal,
        "qtd_minimos_real": qtd_minimos_real
    }

def calcular_ir(salario_bruto):
    DESCONTO_SIMPLIFICADO = 564.80
    base_ir = salario_bruto - DESCONTO_SIMPLIFICADO
    if base_ir <= 2824.00:
        return 0.0
    elif base_ir <= 2826.65:
        return (base_ir * 0.075) - 169.44
    elif base_ir <= 3751.05:
        return (base_ir * 0.15) - 381.44
    elif base_ir <= 4664.68:
        return (base_ir * 0.225) - 662.77
    else:
        return (base_ir * 0.275) - 896.00

def brl_format(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def simular(nivel, classe, quinquenios, dissidio_extra, vale_transporte):
    # Se a classe for "G", use sempre o valor de "I" para essa classe
    if classe == "G":
        salario_base = tabela.get(nivel, {}).get(classe)
        if salario_base is None:
            salario_base = tabela["I"]["G"]
    else:
        salario_base = tabela.get(nivel, {}).get(classe)

    if salario_base is None:
        return {"error": "Combinação de nível e classe inválida."}

    incremento_dissidio = salario_base * (dissidio_extra / 100)
    salario_base_ajustado = salario_base + incremento_dissidio
    adicional = salario_base_ajustado * 0.05 * quinquenios
    tem_sexta_parte = (quinquenios >= 4)
    sexta_parte_valor = salario_base_ajustado * (1/6) if tem_sexta_parte else 0
    salario_total = salario_base_ajustado + adicional + sexta_parte_valor
    vt_valor = salario_base_ajustado * 0.05 if vale_transporte == 'sim' else 0
    verocard_desconto, verocard_valor_liq = calcular_verocard(salario_total)
    fgprev_valor = salario_total * 0.14
    salario_liquido_fgprev = salario_total - fgprev_valor
    ir_valor = calcular_ir(salario_total)
    salario_liquido_final = salario_liquido_fgprev - ir_valor - vt_valor
    analise = analisar_poder_compra(salario_total)
    return {
        "salario_base_ajustado": salario_base_ajustado,
        "incremento_dissidio": incremento_dissidio,
        "salario_bruto": salario_total,
        "salario_bruto_formatado": brl_format(salario_total),
        "fgprev_valor": fgprev_valor,
        "fgprev_valor_formatado": brl_format(fgprev_valor),
        "ir_valor": ir_valor,
        "ir_valor_formatado": brl_format(ir_valor),
        "vt_valor": vt_valor,
        "vt_valor_formatado": brl_format(vt_valor),
        "salario_liquido_final": salario_liquido_final,
        "salario_liquido_final_formatado": brl_format(salario_liquido_final),
        "verocard_desconto": verocard_desconto,
        "verocard_valor": brl_format(verocard_valor_liq),
        "analise_poder_compra": analise
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    if request.method == 'POST':
        nivel = request.form['nivel']
        classe = request.form['classe']
        quinquenios = int(request.form.get('quinquenios', 0))
        dissidio_extra_raw = request.form.get('dissidio_extra', '').replace(',', '.')
        dissidio_extra = float(dissidio_extra_raw) if dissidio_extra_raw else 0.0
        vale_transporte = request.form.get('vale_transporte', 'nao').lower()
        
        resultado = simular(nivel, classe, quinquenios, dissidio_extra, vale_transporte)
    return render_template('index.html', resultado=resultado)

@app.route('/simulate', methods=['GET'])
def simulate():
    nivel = request.args.get('nivel')
    classe = request.args.get('classe')
    quinquenios = int(request.args.get('quinquenios', 0))
    dissidio_extra = float(request.args.get('dissidio_extra', 0))
    vale_transporte = request.args.get('vale_transporte', 'nao').lower()
    resultado = simular(nivel, classe, quinquenios, dissidio_extra, vale_transporte)
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True)
