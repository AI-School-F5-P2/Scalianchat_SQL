# syntax = docker/dockerfile:1.2

FROM python:3.10

# Expose port you want your app on
EXPOSE 8501

# Upgrade pip and install requirements
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy app code and set working directory
WORKDIR /app
COPY . .

# Descargar el instalador del controlador ODBC de SQL Server y ejecutar
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update

RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18



# Give permissions to the script
RUN chmod +x test_micro_azure.py


# Run the app
ENTRYPOINT ["streamlit", "run", "str_interface.py", "--server.port=8501", "--server.address=0.0.0.0"]