# Autor: Miguel Celis

gramatica = {
    'S': [['B', 'uno'], ['dos', 'C'], ['epsilon']],
    'A': [['S', 'tres', 'B', 'C'], ['cuatro'], ['epsilon']],
    'B': [['A', 'cinco', 'C', 'seis'], ['epsilon']],
    'C': [['siete', 'B'], ['epsilon']]
}

no_terminales = {'S', 'A', 'B', 'C'}
terminales = {'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete'}
simbolo_inicial = 'S'

memo_primeros = {}
memo_siguientes = {}
predicciones = {}

def get_primeros(simbolo, visitados=None):
    if visitados is None:
        visitados = set()
        
    if simbolo in memo_primeros:
        return memo_primeros[simbolo]
    if simbolo in terminales or simbolo == 'epsilon':
        return {simbolo}
    
    if simbolo in visitados:
        return set()
        
    visitados.add(simbolo)
    resultado = set()
    
    for produccion in gramatica[simbolo]:
        for s in produccion:
            primeros_s = get_primeros(s, visitados.copy())
            resultado.update(primeros_s - {'epsilon'})
            if 'epsilon' not in primeros_s:
                break
        else:
            resultado.add('epsilon')
            
    memo_primeros[simbolo] = resultado
    return resultado

def primeros_de_cadena(cadena):
    resultado = set()
    if not cadena: 
        return {'epsilon'}
    for simbolo in cadena:
        primeros_s = get_primeros(simbolo)
        resultado.update(primeros_s - {'epsilon'})
        if 'epsilon' not in primeros_s:
            return resultado
    resultado.add('epsilon')
    return resultado

def get_siguientes(simbolo, visitados=None):
    if visitados is None:
        visitados = set()
    if simbolo in memo_siguientes:
        return memo_siguientes[simbolo]
    if simbolo in visitados:
        return set()

    visitados.add(simbolo)
    resultado = set()

    if simbolo == simbolo_inicial:
        resultado.add('$')

    for nt, producciones in gramatica.items():
        for produccion in producciones:
            for i, s in enumerate(produccion):
                if s == simbolo:
                    resto_derecha = produccion[i+1:]
                    primeros_resto = primeros_de_cadena(resto_derecha)
                    
                    resultado.update(primeros_resto - {'epsilon'})

                    if 'epsilon' in primeros_resto:
                        if nt != simbolo: 
                            resultado.update(get_siguientes(nt, visitados.copy()))

    memo_siguientes[simbolo] = resultado
    return resultado

for nt in no_terminales:
    get_primeros(nt)

for nt in no_terminales:
    get_siguientes(nt)

for nt, producciones in gramatica.items():
    for produccion in producciones:
        regla_texto = f"{nt} -> {' '.join(produccion)}"
        primeros_produccion = primeros_de_cadena(produccion)
        
        conjunto_prediccion = primeros_produccion - {'epsilon'}
        
        if 'epsilon' in primeros_produccion:
            conjunto_prediccion.update(memo_siguientes[nt])
            
        predicciones[regla_texto] = conjunto_prediccion

print("Primeros:")
for nt in no_terminales:
    print(f"Primero({nt}) = {memo_primeros[nt]}")

print("\nSiguientes:")
for nt in no_terminales:
    print(f"Siguiente({nt}) = {memo_siguientes[nt]}")

print("\nPredicciones:")
for regla, prediccion in predicciones.items():
    print(f"Predicción({regla}) = {prediccion}")



# IMPLEMENTACIÓN DEL ANALIZADOR SINTÁCTICO DESCENDENTE RECURSIVO (ASDR)


tokens_entrada = []
token_actual = ""
indice_token = 0

def obtener_siguiente_token():
    global indice_token
    if indice_token < len(tokens_entrada):
        token = tokens_entrada[indice_token]
        indice_token += 1
        return token
    return "$"

def emparejar(token_esperado):
    global token_actual
    if token_actual == token_esperado:
        token_actual = obtener_siguiente_token()
    else:
        raise Exception(f"Error sintáctico: Se esperaba '{token_esperado}', pero se encontró '{token_actual}'")

def S():
    # CONFLICTO: 'dos' y 'tres' pertenecen a más de un conjunto de predicción para S
    if token_actual in {'dos', 'tres'}:
        raise Exception(f"Conflicto LL(1) en S: El token '{token_actual}' pertenece a múltiples reglas.")
    elif token_actual in {'uno', 'cuatro', 'cinco'}:
        B()
        emparejar('uno')
    elif token_actual == '$':
        pass # Deriva en epsilon
    else:
        raise Exception(f"Error sintáctico en S con el token '{token_actual}'")

def A():
    # CONFLICTO: 'cuatro' y 'cinco' pertenecen a más de un conjunto de predicción para A
    if token_actual in {'cuatro', 'cinco'}:
        raise Exception(f"Conflicto LL(1) en A: El token '{token_actual}' pertenece a múltiples reglas.")
    elif token_actual in {'uno', 'dos', 'tres'}:
        S()
        emparejar('tres')
        B()
        C()
    else:
        raise Exception(f"Error sintáctico en A con el token '{token_actual}'")

def B():
    # CONFLICTO: 'uno', 'tres' y 'cinco' pertenecen a más de un conjunto de predicción para B
    if token_actual in {'uno', 'tres', 'cinco'}:
        raise Exception(f"Conflicto LL(1) en B: El token '{token_actual}' pertenece a múltiples reglas.")
    elif token_actual in {'dos', 'cuatro'}:
        A()
        emparejar('cinco')
        C()
        emparejar('seis')
    elif token_actual in {'siete', '$', 'seis'}:
        pass # Deriva en epsilon
    else:
        raise Exception(f"Error sintáctico en B con el token '{token_actual}'")

def C():
    # El no terminal C es el único que no presenta conflictos LL(1)
    if token_actual == 'siete':
        emparejar('siete')
        B()
    elif token_actual in {'$', 'tres', 'cinco', 'seis'}:
        pass # Deriva en epsilon
    else:
        raise Exception(f"Error sintáctico en C con el token '{token_actual}'")

def analizar_cadena(cadena_tokens):
    global tokens_entrada, token_actual, indice_token
    tokens_entrada = cadena_tokens
    indice_token = 0
    token_actual = obtener_siguiente_token()
    
    try:
        S()
        if token_actual == '$':
            print("Cadena VÁLIDA sintácticamente.")
        else:
            print(f"Error sintáctico")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    # Prueba 1: Cadena vacía (deriva S -> epsilon). Debería ser VÁLIDA.
    analizar_cadena([])
    
    # Prueba 2: Fuerza el conflicto en S enviando 'dos'.
    analizar_cadena(['dos', 'siete'])
    
    # Prueba 3: Fuerza un error de ruta intentando procesar una regla que desencadena un conflicto en A.
    analizar_cadena(['cuatro', 'cinco', 'seis', 'uno'])

    