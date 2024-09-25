# Proyecto_Final_CDD
**Francisco Tinoco, Pedro Ley, José Luis Almendarez**
***

Este proyecto tiene como objetivo el análisis de datos de las empresas tecnológicas Google, Amazon, y Apple, con un enfoque particular en el trading. Actualmente, el proyecto se encuentra en la etapa de Exploratory Data Analysis (EDA), donde se exploran patrones y características relevantes de los datos de estas tres compañías para un análisis más profundo y la futura implementación de modelos predictivos.

## Estructura del proyecto:
Proyecto_Final_CDD/
│
├── Informe escrito/
│   └── EDA_Notebook.ipynb  # Notebook con el análisis exploratorio de los datos
│
├── Experimentos/
│   └── notebooks/
│       └── models_experiments/
│           └── Model_1_Experiment.ipynb  # Aquí se incluirán los experimentos con los modelos predictivos
│           └── Model_2_Experiment.ipynb  # Otro ejemplo de experimentos con modelos
│
├── .gitignore               # Archivo gitignore para excluir archivos innecesarios del control de versiones
├── README.md                # Instrucciones y descripción del proyecto


Instalación y uso
Requisitos previos
Asegúrate de tener instalados los siguientes paquetes de Python:

numpy
pandas
matplotlib
seaborn
scikit-learn
yfinance (para descargar los datos de las acciones)
notebook (para trabajar con los archivos .ipynb)

Uso
Clona este repositorio en tu entorno local:

bash
Copiar código
git clone https://github.com/usuario/Proyecto_Final_CDD.git
cd Proyecto_Final_CDD
Ejecuta el análisis exploratorio:

Navega a la carpeta Informe escrito/ y abre el archivo EDA_Notebook.ipynb.
Ejecuta el notebook en un entorno Jupyter para explorar los datos de las compañías Google, Amazon y Apple.
Prueba los modelos experimentales:

Dentro de la carpeta Experimentos/notebooks/models_experiments/, encontrarás diferentes notebooks que contienen pruebas con modelos predictivos.
Abre y ejecuta los notebooks para ver los resultados de los experimentos y las métricas de rendimiento de cada modelo.
Datos utilizados
El proyecto utiliza datos históricos de precios de las acciones de Google, Amazon y Apple, obtenidos a través de la API de Yahoo Finance mediante el uso de la librería yfinance.

Estado del proyecto
El proyecto está en una fase de desarrollo temprana. Actualmente, se ha completado la etapa de Análisis Exploratorio de Datos (EDA) y se están preparando experimentos con diferentes modelos predictivos, como ARIMA, Redes Neuronales LSTM, y modelos de Regresión Lineal.