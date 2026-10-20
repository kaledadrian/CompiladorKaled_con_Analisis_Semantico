class AnalizadorSintactico:
    
    # Inicializa las variables que usará el analizador: tokens, posición, errores y árbol
    def __init__(self):
        self.tokens = []
        self.posicion = 0
        self.errores = []
        self.arbol = []
    
    # Método principal: recibe los tokens del léxico, analiza la estructura y retorna (éxito, errores, árbol)
    def analizar(self, tokens):
        self.tokens = tokens
        self.posicion = 0
        self.errores = []
        self.arbol = []
        
        if not tokens:
            self.errores.append({
                'tipo': 'ERROR_SINTACTICO',
                'mensaje': 'No hay código para analizar',
                'posicion': 0
            })
            return False, self.errores, self.arbol
        
        try:
            self.programa()
            
            if self.posicion < len(self.tokens):
                token_actual = self.tokens[self.posicion]
                self.errores.append({
                    'tipo': 'ERROR_SINTACTICO',
                    'mensaje': f'Token inesperado: {token_actual["valor"]}',
                    'posicion': token_actual['posicion']
                })
            
            exitoso = len(self.errores) == 0
            
            if exitoso:
                self.arbol.append({
                    'tipo': 'PROGRAMA',
                    'valor': 'Análisis sintáctico exitoso',
                    'hijos': self.arbol.copy()
                })
            
            return exitoso, self.errores, self.arbol
            
        except Exception as e:
            self.errores.append({
                'tipo': 'ERROR_SINTACTICO',
                'mensaje': str(e),
                'posicion': self.posicion if self.posicion < len(self.tokens) else 0
            })
            return False, self.errores, self.arbol
    
    # Recorre todos los tokens y decide si son función, variable o construcción inválida
    def programa(self):
        while self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            
            if self.es_declaracion_funcion():
                self.declaracion_funcion()
            elif self.es_declaracion_variable():
                self.declaracion_variable()
            else:
                self.errores.append({
                    'tipo': 'ERROR_SINTACTICO',
                    'mensaje': f'Construcción inválida: {token_actual["valor"]}',
                    'posicion': token_actual['posicion']
                })
                self.posicion += 1
    
    # Verifica si el token actual es una función: tipo + identificador + (
    def es_declaracion_funcion(self):
        if self.posicion < len(self.tokens) - 2:
            token1 = self.tokens[self.posicion]
            token2 = self.tokens[self.posicion + 1]
            token3 = self.tokens[self.posicion + 2] if self.posicion + 2 < len(self.tokens) else None
            
            tipos_validos = ['int', 'float', 'string', 'void']
            
            if (token1['tipo'] == 'PALABRA_CLAVE' and token1['valor'] in tipos_validos and
                token2['tipo'] == 'IDENTIFICADOR' and
                token3 and token3['tipo'] == 'DELIMITADOR' and token3['valor'] == '('):
                return True
        return False
    
    # Analiza la función: guarda tipo, valida que se llame "main", analiza parámetros y cuerpo
    def declaracion_funcion(self):
        tipo_token = self.tokens[self.posicion]
        nodo_funcion = {
            'tipo': 'DECLARACION_FUNCION',
            'valor': f'Tipo: {tipo_token["valor"]}',
            'hijos': []
        }
        self.arbol.append(nodo_funcion)
        self.posicion += 1
        
        if self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            if token_actual['tipo'] == 'IDENTIFICADOR':
                nombre_funcion = token_actual['valor']
                
                if nombre_funcion != 'main':
                    self.errores.append({
                        'tipo': 'ERROR_SINTACTICO',
                        'mensaje': f'Se esperaba "main", se encontró: "{nombre_funcion}"',
                        'posicion': token_actual['posicion']
                    })
                
                nodo_funcion['hijos'].append({
                    'tipo': 'IDENTIFICADOR',
                    'valor': token_actual['valor'],
                    'hijos': []
                })
                self.posicion += 1
            else:
                self.errores.append({
                    'tipo': 'ERROR_SINTACTICO',
                    'mensaje': f'Se esperaba nombre de función, se encontró: {token_actual["valor"]}',
                    'posicion': token_actual['posicion']
                })
                return
        
        if self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == '(':
                nodo_funcion['hijos'].append({
                    'tipo': 'PARAMETROS',
                    'valor': 'Parámetros de función',
                    'hijos': []
                })
                self.posicion += 1
                self.parametros()
                
                if self.posicion < len(self.tokens):
                    token_actual = self.tokens[self.posicion]
                    if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == ')':
                        self.posicion += 1
                    else:
                        self.errores.append({
                            'tipo': 'ERROR_SINTACTICO',
                            'mensaje': f'Se esperaba ), se encontró: {token_actual["valor"]}',
                            'posicion': token_actual['posicion']
                        })
                        return
                else:
                    self.errores.append({
                        'tipo': 'ERROR_SINTACTICO',
                        'mensaje': 'Se esperaba ) para cerrar los parámetros',
                        'posicion': len(self.tokens) - 1
                    })
                    return
            else:
                self.errores.append({
                    'tipo': 'ERROR_SINTACTICO',
                    'mensaje': f'Se esperaba (, se encontró: {token_actual["valor"]}',
                    'posicion': token_actual['posicion']
                })
                return
        
        if self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == '{':
                nodo_funcion['hijos'].append({
                    'tipo': 'BLOQUE',
                    'valor': 'Cuerpo de función',
                    'hijos': []
                })
                self.posicion += 1
                self.bloque()
                
                if self.posicion < len(self.tokens):
                    token_actual = self.tokens[self.posicion]
                    if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == '}':
                        self.posicion += 1
                    else:
                        self.errores.append({
                            'tipo': 'ERROR_SINTACTICO',
                            'mensaje': f'Se esperaba }}, se encontró: {token_actual["valor"]}',
                            'posicion': token_actual['posicion']
                        })
                else:
                    self.errores.append({
                        'tipo': 'ERROR_SINTACTICO',
                        'mensaje': 'Se esperaba } para cerrar la función',
                        'posicion': len(self.tokens) - 1
                    })
            else:
                self.errores.append({
                    'tipo': 'ERROR_SINTACTICO',
                    'mensaje': f'Se esperaba {{, se encontró: {token_actual["valor"]}',
                    'posicion': token_actual['posicion']
                })
    
    # Analiza los parámetros de la función, reconoce identificadores y comas
    def parametros(self):
        if self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == ')':
                return
        
        while self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == ')':
                break
            elif token_actual['tipo'] == 'IDENTIFICADOR':
                nodo_param = self.arbol[-1]['hijos'][-1]
                nodo_param['hijos'].append({
                    'tipo': 'PARAMETRO',
                    'valor': token_actual['valor'],
                    'hijos': []
                })
                self.posicion += 1
                if self.posicion < len(self.tokens):
                    token_actual = self.tokens[self.posicion]
                    if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == ',':
                        self.posicion += 1
            else:
                self.posicion += 1
    
    # Verifica si el token actual es variable: tipo + identificador
    def es_declaracion_variable(self):
        if self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            tipos_validos = ['int', 'float', 'string']
            
            if token_actual['tipo'] == 'PALABRA_CLAVE' and token_actual['valor'] in tipos_validos:
                if self.posicion + 1 < len(self.tokens):
                    siguiente = self.tokens[self.posicion + 1]
                    return siguiente['tipo'] == 'IDENTIFICADOR'
        return False
    
    # Analiza variable: guarda tipo, identificador, salta asignación y verifica punto y coma
    def declaracion_variable(self):
        tipo_token = self.tokens[self.posicion]
        nodo = {
            'tipo': 'DECLARACION_VARIABLE',
            'valor': f'Tipo: {tipo_token["valor"]}',
            'hijos': []
        }
        self.arbol.append(nodo)
        self.posicion += 1
        
        if self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            if token_actual['tipo'] == 'IDENTIFICADOR':
                nodo['hijos'].append({
                    'tipo': 'IDENTIFICADOR',
                    'valor': token_actual['valor'],
                    'hijos': []
                })
                self.posicion += 1
            else:
                self.errores.append({
                    'tipo': 'ERROR_SINTACTICO',
                    'mensaje': f'Se esperaba identificador, se encontró: {token_actual["valor"]}',
                    'posicion': token_actual['posicion']
                })
                return
        
        if self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            if token_actual['tipo'] == 'OPERADOR_RELACIONAL' and token_actual['valor'] == '=':
                self.posicion += 1
                while self.posicion < len(self.tokens):
                    token_actual = self.tokens[self.posicion]
                    if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == ';':
                        break
                    if token_actual['tipo'] == 'PALABRA_CLAVE':
                        break
                    self.posicion += 1
        
        if self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == ';':
                nodo['hijos'].append({
                    'tipo': 'DELIMITADOR',
                    'valor': ';',
                    'hijos': []
                })
                self.posicion += 1
            else:
                self.errores.append({
                    'tipo': 'ERROR_SINTACTICO',
                    'mensaje': f'Se esperaba ;, se encontró: {token_actual["valor"]}',
                    'posicion': token_actual['posicion']
                })
        else:
            self.errores.append({
                'tipo': 'ERROR_SINTACTICO',
                'mensaje': 'Se esperaba ; al final de la declaración',
                'posicion': len(self.tokens) - 1
            })
    
    # Verifica si el token actual es una sentencia: if, while, for, return, print
    def es_sentencia(self):
        if self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            sentencias = ['if', 'while', 'for', 'return', 'print']
            return token_actual['tipo'] == 'PALABRA_CLAVE' and token_actual['valor'] in sentencias
        return False
    
    # Analiza la sentencia, la agrega al bloque padre y llama al método específico según el tipo
    def sentencia(self):
        if self.posicion >= len(self.tokens):
            return
        
        token_actual = self.tokens[self.posicion]
        tipo = token_actual['valor']
        
        nodo_sentencia = {
            'tipo': 'SENTENCIA',
            'valor': tipo,
            'hijos': []
        }
        
        bloque_padre = None
        for nodo in reversed(self.arbol):
            if nodo['tipo'] == 'BLOQUE':
                bloque_padre = nodo
                break
        
        if bloque_padre is not None:
            bloque_padre['hijos'].append(nodo_sentencia)
        else:
            self.arbol.append(nodo_sentencia)
        
        self.posicion += 1
        
        if tipo == 'if':
            self.sentencia_if(nodo_sentencia)
        elif tipo == 'while':
            self.sentencia_while(nodo_sentencia)
        elif tipo == 'for':
            self.sentencia_for(nodo_sentencia)
        elif tipo == 'return':
            self.sentencia_return(nodo_sentencia)
        elif tipo == 'print':
            self.sentencia_print(nodo_sentencia)
    
    # Analiza if: verifica (condicion) y luego los bloques { ... } y opcionalmente else { ... }
    def sentencia_if(self, nodo):
        if self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == '(':
                self.posicion += 1
                while self.posicion < len(self.tokens):
                    token_actual = self.tokens[self.posicion]
                    if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == ')':
                        self.posicion += 1
                        break
                    self.posicion += 1
            else:
                self.errores.append({
                    'tipo': 'ERROR_SINTACTICO',
                    'mensaje': f'Se esperaba (, se encontró: {token_actual["valor"]}',
                    'posicion': token_actual['posicion']
                })
                return
        
        if self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == '{':
                self.posicion += 1
                self.bloque()
                if self.posicion < len(self.tokens):
                    token_actual = self.tokens[self.posicion]
                    if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == '}':
                        self.posicion += 1
                    else:
                        self.errores.append({
                            'tipo': 'ERROR_SINTACTICO',
                            'mensaje': f'Se esperaba }}, se encontró: {token_actual["valor"]}',
                            'posicion': token_actual['posicion']
                        })
            else:
                self.errores.append({
                    'tipo': 'ERROR_SINTACTICO',
                    'mensaje': f'Se esperaba {{, se encontró: {token_actual["valor"]}',
                    'posicion': token_actual['posicion']
                })
                return
        
        if self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            if token_actual['tipo'] == 'PALABRA_CLAVE' and token_actual['valor'] == 'else':
                self.posicion += 1
                if self.posicion < len(self.tokens):
                    token_actual = self.tokens[self.posicion]
                    if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == '{':
                        self.posicion += 1
                        self.bloque()
                        if self.posicion < len(self.tokens):
                            token_actual = self.tokens[self.posicion]
                            if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == '}':
                                self.posicion += 1
                            else:
                                self.errores.append({
                                    'tipo': 'ERROR_SINTACTICO',
                                    'mensaje': f'Se esperaba }}, se encontró: {token_actual["valor"]}',
                                    'posicion': token_actual['posicion']
                                })
                    else:
                        self.errores.append({
                            'tipo': 'ERROR_SINTACTICO',
                            'mensaje': f'Se esperaba {{, se encontró: {token_actual["valor"]}',
                            'posicion': token_actual['posicion']
                        })
    
    # Analiza while: verifica (condicion) y luego el bloque { ... }
    def sentencia_while(self, nodo):
        if self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == '(':
                self.posicion += 1
                while self.posicion < len(self.tokens):
                    token_actual = self.tokens[self.posicion]
                    if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == ')':
                        self.posicion += 1
                        break
                    self.posicion += 1
            else:
                self.errores.append({
                    'tipo': 'ERROR_SINTACTICO',
                    'mensaje': f'Se esperaba (, se encontró: {token_actual["valor"]}',
                    'posicion': token_actual['posicion']
                })
                return
        
        if self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == '{':
                self.posicion += 1
                self.bloque()
                if self.posicion < len(self.tokens):
                    token_actual = self.tokens[self.posicion]
                    if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == '}':
                        self.posicion += 1
                    else:
                        self.errores.append({
                            'tipo': 'ERROR_SINTACTICO',
                            'mensaje': f'Se esperaba }}, se encontró: {token_actual["valor"]}',
                            'posicion': token_actual['posicion']
                        })
            else:
                self.errores.append({
                    'tipo': 'ERROR_SINTACTICO',
                    'mensaje': f'Se esperaba {{, se encontró: {token_actual["valor"]}',
                    'posicion': token_actual['posicion']
                })
    
    # Analiza for: verifica (inicio; condicion; incremento) y luego el bloque { ... }
    def sentencia_for(self, nodo):
        if self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == '(':
                self.posicion += 1
                while self.posicion < len(self.tokens):
                    token_actual = self.tokens[self.posicion]
                    if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == ')':
                        self.posicion += 1
                        break
                    self.posicion += 1
            else:
                self.errores.append({
                    'tipo': 'ERROR_SINTACTICO',
                    'mensaje': f'Se esperaba (, se encontró: {token_actual["valor"]}',
                    'posicion': token_actual['posicion']
                })
                return
        
        if self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == '{':
                self.posicion += 1
                self.bloque()
                if self.posicion < len(self.tokens):
                    token_actual = self.tokens[self.posicion]
                    if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == '}':
                        self.posicion += 1
                    else:
                        self.errores.append({
                            'tipo': 'ERROR_SINTACTICO',
                            'mensaje': f'Se esperaba }}, se encontró: {token_actual["valor"]}',
                            'posicion': token_actual['posicion']
                        })
            else:
                self.errores.append({
                    'tipo': 'ERROR_SINTACTICO',
                    'mensaje': f'Se esperaba {{, se encontró: {token_actual["valor"]}',
                    'posicion': token_actual['posicion']
                })
    
    # Analiza return: guarda el valor de retorno y verifica punto y coma
    def sentencia_return(self, nodo):
        if self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            if token_actual['tipo'] in ['NUMERO', 'IDENTIFICADOR', 'CADENA']:
                nodo['hijos'].append({
                    'tipo': token_actual['tipo'],
                    'valor': token_actual['valor'],
                    'hijos': []
                })
                self.posicion += 1
        
        if self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == ';':
                nodo['hijos'].append({
                    'tipo': 'DELIMITADOR',
                    'valor': ';',
                    'hijos': []
                })
                self.posicion += 1
            else:
                self.errores.append({
                    'tipo': 'ERROR_SINTACTICO',
                    'mensaje': f'Se esperaba ;, se encontró: {token_actual["valor"]}',
                    'posicion': token_actual['posicion']
                })
    
    # Analiza print: lee la expresión entre paréntesis y verifica punto y coma
    def sentencia_print(self, nodo):
        if self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == '(':
                self.posicion += 1
                
                expresion = []
                while self.posicion < len(self.tokens):
                    token_actual = self.tokens[self.posicion]
                    if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == ')':
                        break
                    expresion.append(token_actual)
                    self.posicion += 1
                
                if expresion:
                    nodo_expresion = {
                        'tipo': 'EXPRESION',
                        'valor': ' '.join([t['valor'] for t in expresion]),
                        'hijos': []
                    }
                    nodo['hijos'].append(nodo_expresion)
                    
                    for token in expresion:
                        nodo_expresion['hijos'].append({
                            'tipo': token['tipo'],
                            'valor': token['valor'],
                            'hijos': []
                        })
                
                if self.posicion < len(self.tokens):
                    token_actual = self.tokens[self.posicion]
                    if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == ')':
                        self.posicion += 1
                    else:
                        self.errores.append({
                            'tipo': 'ERROR_SINTACTICO',
                            'mensaje': f'Se esperaba ), se encontró: {token_actual["valor"]}',
                            'posicion': token_actual['posicion']
                        })
                        return
                else:
                    self.errores.append({
                        'tipo': 'ERROR_SINTACTICO',
                        'mensaje': 'Se esperaba ) en print',
                        'posicion': len(self.tokens) - 1
                    })
                    return
            else:
                self.errores.append({
                    'tipo': 'ERROR_SINTACTICO',
                    'mensaje': f'Se esperaba (, se encontró: {token_actual["valor"]}',
                    'posicion': token_actual['posicion']
                })
                return
        
        if self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == ';':
                nodo['hijos'].append({
                    'tipo': 'DELIMITADOR',
                    'valor': ';',
                    'hijos': []
                })
                self.posicion += 1
            else:
                self.errores.append({
                    'tipo': 'ERROR_SINTACTICO',
                    'mensaje': f'Se esperaba ;, se encontró: {token_actual["valor"]}',
                    'posicion': token_actual['posicion']
                })
    
    # Analiza un bloque de código: mientras no encuentre }, analiza variables o sentencias
    def bloque(self):
        while self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            
            if token_actual['tipo'] == 'DELIMITADOR' and token_actual['valor'] == '}':
                break
            
            if self.es_declaracion_variable():
                self.declaracion_variable()
            elif self.es_sentencia():
                self.sentencia()
            else:
                self.posicion += 1