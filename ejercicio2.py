# Definición de la gramática y símbolos
gramatica_ej1 = {
    'S': [['A', 'uno', 'B', 'C', "S'"]],
    "S'": [['dos', "S'"], ['epsilon']],
    'A': [['B', 'C', 'D', "A'"], ["A'"]],
    "A'": [['tres', "A'"], ['epsilon']],
    'B': [['D', 'cuatro', 'C', 'tres'], ['epsilon']],
    'C': [['cinco', 'D', 'B'], ['epsilon']],
    'D': [['seis'], ['epsilon']]
}

no_terminales = {'S', "S'", 'A', "A'", 'B', 'C', 'D'}
terminales = {'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis'}
simbolo_inicial = 'S'
memo_primeros = {}
memo_siguientes = {}
predicciones = {}

def get_primeros(simbolo, visitados=None):
    if visitados is None:
        visitados = set()
        
    # Casos base
    if simbolo in memo_primeros:
        return memo_primeros[simbolo]
    if simbolo in terminales or simbolo == 'epsilon':
        return {simbolo}
    
    if simbolo in visitados:
        return set()
        
    visitados.add(simbolo)
    resultado = set()
    
    for produccion in gramatica_ej1[simbolo]:
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

    # Casos base
    if simbolo in memo_siguientes:
        return memo_siguientes[simbolo]
    if simbolo in visitados:
        return set()

    visitados.add(simbolo)
    resultado = set()

    if simbolo == simbolo_inicial:
        resultado.add('$')

    for nt, producciones in gramatica_ej1.items():
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

for nt, producciones in gramatica_ej1.items():
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