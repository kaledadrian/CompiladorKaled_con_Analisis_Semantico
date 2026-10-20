# Importa las funciones necesarias de Django para renderizar plantillas y responder JSON
from django.shortcuts import render
from django.http import JsonResponse

# Importa los analizadores léxico y sintáctico que creamos
from .lexico import AnalizadorLexico
from .sintactico import AnalizadorSintactico
from .semantico import AnalizadorSemantico


# Vista de la página principal: muestra el formulario para ingresar código
def index(request):
    return render(request, "analizador/index.html")


# Vista principal: recibe el código, lo analiza y devuelve los resultados
def analizar(request):
    # Solo procesa si la petición es POST (cuando el usuario hace clic en "Analizar")
    if request.method == "POST":

        # Obtiene el código enviado desde el formulario, si está vacío usa cadena vacía
        codigo = request.POST.get("codigo", "")

        # Crea el analizador léxico, analiza el código y obtiene tokens y errores
        analizador_lexico = AnalizadorLexico()
        tokens, errores_lexicos = analizador_lexico.analizar(codigo)

        # Crea el analizador sintáctico, analiza los tokens y obtiene resultado, errores sintácticos y el árbol sintáctico
        analizador_sintactico = AnalizadorSintactico()
        exitoso_sintactico, errores_sintacticos, arbol = analizador_sintactico.analizar(
            tokens
        )

        # Ejecuta el análisis semántico solamente cuando las fases anteriores no detectan errores.
        if not errores_lexicos and exitoso_sintactico:
            analizador_semantico = AnalizadorSemantico()
            exitoso_semantico, errores_semanticos, tabla_simbolos = analizador_semantico.analizar(tokens)
        else:
            exitoso_semantico, errores_semanticos, tabla_simbolos = False, [], []

        # Reúne los errores de las tres fases.
        todos_los_errores = errores_lexicos + errores_sintacticos + errores_semanticos
        exitoso = len(todos_los_errores) == 0 and exitoso_sintactico and exitoso_semantico

        # Crea un diccionario con todos los datos para enviar a la plantilla
        resultado = {
            "exitoso": exitoso,  # True si todo está bien
            "tokens": tokens,  # Lista de tokens encontrados
            "errores": todos_los_errores,  # Todos los errores combinados
            "arbol": arbol,  # Árbol sintáctico generado
            "cantidad_tokens": len(tokens),  # Número de tokens
            "cantidad_errores": len(todos_los_errores),  # Número total de errores
            "codigo": codigo,  # Código fuente original
            "exitoso_semantico": exitoso_semantico,
            "errores_semanticos": errores_semanticos,
            "tabla_simbolos": tabla_simbolos,
        }

        # Si la petición es AJAX (desde JavaScript), devuelve JSON Si no, renderiza la plantilla de resultados
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(resultado)

        return render(request, "analizador/resultado.html", resultado)

    # Si la petición no es POST, muestra la página principal
    return render(request, "analizador/index.html")
