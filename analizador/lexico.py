# Importa el módulo de expresiones regulares para reconocer patrones en el código
import re

# Analizador Léxico: convierte el código fuente en tokens
class AnalizadorLexico:
    # Cada token tiene un nombre y una expresión regular para reconocerlo
    def __init__(self):
        self.tokens = [
            # Palabras reservadas del lenguaje
            ('PALABRA_CLAVE', r'\b(if|else|while|for|return|int|float|string|void|print)\b'),
            # Identificadores: nombres de variables y funciones
            ('IDENTIFICADOR', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            # Números: enteros o decimales
            ('NUMERO', r'\b\d+(\.\d+)?\b'),
            # Operadores aritméticos: + - * / %
            ('OPERADOR_ARITMETICO', r'[+\-*/%]'),
            # Operadores relacionales: = == != < > <= >=
            ('OPERADOR_RELACIONAL', r'[=!<>]=?'),
            # Operadores lógicos: && ||
            ('OPERADOR_LOGICO', r'&&|\|\|'),
            # Delimitadores: { } ( ) [ ] ; ,
            ('DELIMITADOR', r'[{}()\[\];,]'),
            # Comentarios de una línea: //
            ('COMENTARIO_LINEA', r'//.*'),
            # Comentarios de bloque: /* ... */
            ('COMENTARIO_BLOQUE', r'/\*.*?\*/'),
            # Cadenas de texto entre comillas
            ('CADENA', r'"[^"]*"'),
            # Espacios en blanco: se ignoran
            ('ESPACIO', r'\s+'),
            # Cualquier otro carácter: ERROR (captura @, $, #, etc.)
            ('ERROR', r'.')
        ]
    
    # Analiza el código fuente y devuelve tokens y errores
    def analizar(self, codigo):
        tokens_encontrados = []  # Lista de tokens válidos
        errores = []              # Lista de errores encontrados
        posicion = 0              # Índice actual en el código
        
        # Elimina comentarios de bloque del código antes de analizar
        codigo_sin_comentarios = re.sub(r'/\*.*?\*/', '', codigo, flags=re.DOTALL)
        
        # Recorre el código carácter por carácter
        while posicion < len(codigo_sin_comentarios):
            match = None
            
            # Prueba cada patrón de token en orden
            for token_nombre, patron in self.tokens:
                regex = re.compile(patron)
                match = regex.match(codigo_sin_comentarios, posicion)
                
                if match:
                    valor = match.group(0)  # El texto que coincide
                    
                    # Ignora espacios y comentarios de línea
                    if token_nombre != 'ESPACIO' and token_nombre != 'COMENTARIO_LINEA':
                        if token_nombre == 'ERROR':
                            # Si es ERROR, guarda el error
                            errores.append({
                                'tipo': 'ERROR_LEXICO',
                                'mensaje': f'Carácter inválido: "{valor}"',
                                'posicion': posicion
                            })
                        else:
                            # Si es un token válido, lo guarda
                            tokens_encontrados.append({
                                'tipo': token_nombre,
                                'valor': valor,
                                'posicion': posicion
                            })
                    
                    posicion = match.end()  # Avanza la posición
                    break
            
            # Si ningún patrón coincide, es un error
            if not match:
                errores.append({
                    'tipo': 'ERROR_LEXICO',
                    'mensaje': f'Carácter inválido en posición {posicion}',
                    'posicion': posicion
                })
                posicion += 1  # Avanza para evitar bucle infinito
        
        # Devuelve la lista de tokens y la lista de errores
        return tokens_encontrados, errores