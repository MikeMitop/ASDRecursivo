# Autor: Miguel Celis

gramatica = {
    'S': [['A', 'B', 'C', "S'"]],
    "S'": [['uno', "S'"], ['epsilon']],
    'A': [['dos', 'B', 'C'], ['epsilon']],
    'B': [['C', 'tres'], ['epsilon']],
    'C': [['cuatro', 'B'], ['epsilon']]
}

no_terminales = {'S', "S'", 'A', 'B', 'C'}
terminales = {'uno', 'dos', 'tres', 'cuatro'}
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
    # S solo tiene una regla, por lo que acepta cualquier token de su conjunto de predicción
    if token_actual in {'dos', 'cuatro', 'tres', 'uno', '$'}:
        A()
        B()
        C()
        S_prima()
    else:
        raise Exception(f"Error sintáctico en S con el token '{token_actual}'")

def S_prima():
    if token_actual == 'uno':
        emparejar('uno')
        S_prima()
    elif token_actual == '$':
        pass # Deriva en epsilon
    else:
        raise Exception(f"Error sintáctico en S' con el token '{token_actual}'")

def A():
    if token_actual == 'dos':
        emparejar('dos')
        B()
        C()
    elif token_actual in {'cuatro', 'tres', 'uno', '$'}:
        pass # Deriva en epsilon
    else:
        raise Exception(f"Error sintáctico en A con el token '{token_actual}'")

def B():
    # CONFLICTO: 'cuatro' y 'tres' pertenecen tanto a la regla B -> C tres como a B -> epsilon
    if token_actual in {'cuatro', 'tres'}:
        raise Exception(f"Conflicto LL(1) en B: El token '{token_actual}' pertenece a múltiples reglas.")
    elif token_actual in {'uno', '$'}:
        pass # Deriva en epsilon
    else:
        raise Exception(f"Error sintáctico en B con el token '{token_actual}'")

def C():
    # CONFLICTO: 'cuatro' pertenece tanto a la regla C -> cuatro B como a C -> epsilon
    if token_actual == 'cuatro':
        raise Exception(f"Conflicto LL(1) en C: El token '{token_actual}' pertenece a múltiples reglas.")
    elif token_actual in {'tres', 'uno', '$'}:
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
            print(f"Cadena {cadena_tokens} VÁLIDA sintácticamente.")
        else:
            print("Error sintáctico")
    except Exception as e:
        print(f"Error con {cadena_tokens}: {e}")

if __name__ == "__main__":
    # Prueba 1: Cadena vacía (todos los no terminales derivan a epsilon). Debería ser VÁLIDA.
    analizar_cadena([])
    
    # Prueba 2: Fuerza el conflicto en B enviando un 'tres'.
    analizar_cadena(['tres', 'uno'])
    
    # Prueba 3: Fuerza el conflicto en C enviando un 'cuatro'.
    analizar_cadena(['dos', 'cuatro'])