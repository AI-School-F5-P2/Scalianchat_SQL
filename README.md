# ChatBot EvaSQL

## Planteamiento

🔍 Acceder y comprender la información de una base de datos SQL puede ser desafiante para aquellos sin experiencia técnica. Sin embargo, los modelos de lenguaje avanzados y las nuevas tecnologías de Inteligencia Artificial disponibles en la nube, nos permiten crear herramientas para solventar esta situación. 

💡 Por eso, nuestro ChatBot EvaSQL, tiene como objetivo facilitar el acceso a la información y la interpretación de los datos mediante la generación de consultas SQL y gráficos interactivos a partir de lenguaje natural. Todo esto se realiza a través de una interfaz amigable que simplifica la interacción con la base de datos, permitiendo a los usuarios realizar consultas y obtener respuestas de manera rápida y eficiente.

## Características Principales

- **Interfaz Intuitiva**: Conversa con el ChatBot como lo harías con un amigo, sin necesidad de comandos complicados.
- **Traducción a SQL**: Transforma consultas en lenguaje natural a consultas SQL comprensibles para la base de datos.
- **Generación de Gráficos**: Crea gráficos interactivos a partir de los resultados de las consultas para una visualización clara de los datos.
- **Soporte Multilingüe**: Accede al ChatBot en tu idioma preferido para una experiencia personalizada.
- **Servicio de Voz**: Formula consultas y recibe respuestas utilizando tu voz.
- **Versión Dockerizada**: Despliega el ChatBot fácilmente en cualquier entorno gracias a su versión dockerizada.
- **Despliegue en Azure**: Accede al ChatBot desde cualquier dispositivo autorizado mediante un enlace o código QR.

## Paso a Paso de Cómo Usarlo

1. Clona o descarga el repositorio desde [GitHub](https://github.com/AI-School-F5-P2/Scalianchat_SQL.git).
2. Instala las dependencias necesarias utilizando `pip install -r requirements.txt`.
3. Ejecuta el script `str_interface.py` para iniciar la interfaz en Streamlit del ChatBot.
4. Interactúa con el ChatBot escribiendo tus consultas en lenguaje natural o activando el micrófono para hablar.
5. Visualiza los resultados de las consultas en forma de texto y/o gráficos interactivos.

## Descripción de los Archivos

- **data_cleaning.ipynb**: Notebook para la limpieza de datos del dataset original.
- **azure_db.py**: Script para la creación de tablas en Azure SQL Database y carga de datos.
- **json_emb_files_generator.ipynb**: Notebook para la generación de documentos JSON para Azure AI Search.
- **rag_openai.py**: Configuración de llamadas a la API de Azure OpenAI.
- **str_interface.py**: Programa principal e interfaz en Streamlit.
- **README.md**: Documentación detallada sobre el proyecto.

## Autores

[Karla Lamus Oliveros](https://www.linkedin.com/in/karla-lamus/)

[Miguel Mendoza Espinoza](https://www.linkedin.com/in/miguelmendozaespinoza9a010114a/)

[Sandra Gómez S.](https://www.linkedin.com/in/sandragomezs/)

[Ana Gómez Giraldo](https://www.linkedin.com/in/ana-milena-gomez-giraldo/?locale=es_ES)


## Agradecimientos

Agradecemos especialmente a Scalian y Factoría F5 por su apoyo y acompañamiento durante el desarrollo de este proyecto.
