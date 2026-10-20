"""Analizador semántico básico para el lenguaje educativo de CompiladorKaled.
Comprueba declaraciones, duplicados, uso de identificadores y tipos en asignaciones simples.
"""

TIPOS = {"int", "float", "string", "void"}
PALABRAS_RESERVADAS = {"if", "else", "while", "for", "return", "int", "float", "string", "void", "print"}

class AnalizadorSemantico:
    def analizar(self, tokens):
        simbolos = []
        errores = []
        declarados = {}
        valores_por_nombre = {}
        i = 0

        # Primera pasada: registrar declaraciones de variables.
        while i < len(tokens):
            valor = tokens[i].get("valor", "")
            if valor in {"int", "float", "string"} and i + 1 < len(tokens):
                siguiente = tokens[i + 1]
                if siguiente.get("tipo") == "IDENTIFICADOR":
                    nombre = siguiente["valor"]
                    pos = siguiente.get("posicion", 0)
                    if nombre in declarados:
                        errores.append({"tipo": "ERROR_SEMANTICO", "mensaje": f"La variable '{nombre}' ya fue declarada.", "posicion": pos})
                    else:
                        declarados[nombre] = valor
                        simbolos.append({"nombre": nombre, "tipo": valor, "ambito": "global", "posicion": pos})
            i += 1

        # Segunda pasada: validar usos y asignaciones sencillas.
        declaracion_indices = set()
        for j in range(len(tokens) - 1):
            if tokens[j].get("valor") in {"int", "float", "string"} and tokens[j + 1].get("tipo") == "IDENTIFICADOR":
                declaracion_indices.add(j + 1)

        for i, token in enumerate(tokens):
            if token.get("tipo") != "IDENTIFICADOR" or i in declaracion_indices:
                continue
            nombre = token.get("valor", "")
            pos = token.get("posicion", 0)
            # Nombres de funciones antes de '(' no se tratan como variables.
            if i + 1 < len(tokens) and tokens[i + 1].get("valor") == "(":
                continue
            if nombre not in declarados and nombre not in PALABRAS_RESERVADAS:
                errores.append({"tipo": "ERROR_SEMANTICO", "mensaje": f"La variable '{nombre}' se usa sin haber sido declarada.", "posicion": pos})
                continue
            if nombre in declarados and i + 1 < len(tokens) and tokens[i + 1].get("valor") == "=":
                if i + 2 < len(tokens):
                    rhs = tokens[i + 2]
                    tipo_destino = declarados[nombre]
                    tipo_origen = None
                    if rhs.get("tipo") == "CADENA":
                        tipo_origen = "string"
                    elif rhs.get("tipo") == "NUMERO":
                        tipo_origen = "float" if "." in rhs.get("valor", "") else "int"
                    elif rhs.get("tipo") == "IDENTIFICADOR":
                        tipo_origen = declarados.get(rhs.get("valor"))
                    compatible = (tipo_origen is None or tipo_destino == tipo_origen or (tipo_destino == "float" and tipo_origen == "int"))
                    if not compatible:
                        errores.append({"tipo": "ERROR_SEMANTICO", "mensaje": f"Asignación incompatible: '{nombre}' es {tipo_destino} y recibe un valor {tipo_origen}.", "posicion": pos})

        return len(errores) == 0, errores, simbolos
