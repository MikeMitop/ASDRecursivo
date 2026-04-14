# Autor: Miguel Celis

gramatica = {
    'S': [['A', 'B', 'C'], ['D', 'E']],
    'A': [['dos', 'B', 'tres'], ['epsilon']],
    'B': [["B'"]],
    "B'": [['cuatro', 'C', 'cinco', "B'"], ['epsilon']],
    'C': [['seis', 'A', 'B'], ['epsilon']],
    'D': [['uno', 'A', 'E'], ['B']],
    'E': [['tres']]
}

no_terminales = {'S', 'A', 'B', "B'", 'C', 'D', 'E'}
terminales = {'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis'}
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
        raise Exception(f"Error sintáctico: ")

def S():
    if token_actual == 'cuatro':
        # CONFLICTO LL(1): 'cuatro' está en la predicción de S -> A B C y S -> D E
        raise Exception("Conflicto LL(1) en S")
    elif token_actual in {'dos', 'seis', '$'}:
        A()
        B()
        C()
    elif token_actual in {'uno', 'tres'}:
        D()
        E()
    else:
        raise Exception(f"Error sintáctico")

def A():
    if token_actual == 'dos':
        emparejar('dos')
        B()
        emparejar('tres')
    elif token_actual in {'cuatro', 'seis', '$', 'cinco', 'tres'}:
        pass # Deriva en epsilon
    else:
        raise Exception(f"Error sintáctico")

def B():
    if token_actual in {'cuatro', 'seis', '$', 'tres', 'cinco'}:
        B_prima()
    else:
        raise Exception(f"Error sintáctico")

def B_prima():
    if token_actual == 'cuatro':
        emparejar('cuatro')
        C()
        emparejar('cinco')
        B_prima()
    elif token_actual in {'seis', '$', 'tres', 'cinco'}:
        pass # Deriva en epsilon
    else:
        raise Exception(f"Error sintáctico")

def C():
    if token_actual == 'seis':
        emparejar('seis')
        A()
        B()
    elif token_actual in {'$', 'cinco'}:
        pass # Deriva en epsilon
    else:
        raise Exception(f"Error sintáctico")

def D():
    if token_actual == 'uno':
        emparejar('uno')
        A()
        E()
    elif token_actual in {'cuatro', 'tres'}:
        B()
    else:
        raise Exception(f"Error sintáctico")

def E():
    if token_actual == 'tres':
        emparejar('tres')
    else:
        raise Exception(f"Error sintáctico")

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
            print(f"Error: La cadena no fue consumida en su totalidad. Sobra '{token_actual}'.")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    analizar_cadena(['uno', 'tres'])
    analizar_cadena(['cuatro', 'cinco'])