SYSTEM_MESSAGE_CHART_INTENTION = """

- Your job is to determine if the user is asking for a chart.

- Your answer MUST be a single word: True or False.

Examples:

User: "Could you provide me with a chart showing the total assets of institutions in California?"
Assistant: True

User: "Bitte könnten Sie mir ein Diagramm erstellen, das die Gesamtaktiva der in Kalifornien ansässigen Institutionen zeigt?"
Assitant: True

User: "¿Cuáles son los activos totales del Banco de California?"
Assistant: False

User: "¿Qué institución financiera tenía los activos totales más altos en el año 2020?"
Assistant: False

User: "Qual è stato il valore medio totale dei titoli per le banche dello stato del Wisconsin tra il 2015 e il 2020?"
Assistant: False

User: Grafica ¿cómo ha variado el valor total de los títulos a lo largo del tiempo para las instituciones financieras 
de la ciudad de Nueva York?
Assistant: True

"""