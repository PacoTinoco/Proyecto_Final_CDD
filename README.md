# Proyecto_Final_CDD
**Francisco Tinoco, Pedro Ley, José Luis Almendarez**
***

Este proyecto tiene como objetivo el análisis de datos de las empresas tecnológicas Google, Amazon, y Apple, con un enfoque particular en el trading.
En el proceso probamos diferentes modelos como xgboost, Arima y random forest que no fue el que mejor resultado nos dió pero si el que se nos facilitó más a la hora de implementación.
Nuestros datos decidimos tomarlos del año 2015 hasta el año actual 2024 recopilados de yahoo finance como datos diarios.

## Estructura del proyecto:
Encontrarás una carpeta DATA que contiene los datos que usamos para Amazon y Google en forma de csv.
Dentro de la carpeta INFORME ESCRITO viene un notebook con los EDAS de cada empresa tecnológica que usamos, contiene la introducción al proyecto, los antecedentes, los objetivos, el planteamiento del problema, el desarrollo de la solución y después el respectivo análisis de los diferentes dfs, como sus distribuciones y  algunas gráficas de los ultimos años en base al cierre de la acción.
Después dentro de otra carpeta MODEL EXPERIMENTS encontrarás los notebooks con los diferentes modelos que probamos a nuestros datos y elcual decidimos usar al final fue un random forest, que fue orquestado con prefect después.
Dentro de nuestra carpeta SOURCE 
Por útlimo tenemos nuestro TRAINING PIPELINE que se encuentra el flujo de entrenamiento cargado con prefect 


## Objetivo General:

Desarrollar una plataforma web que permita a los usuarios realizar operaciones de trading a través de su broker, integrando modelos de predicción de precios basados en diferentes estrategias, para optimizar la toma de decisiones en su actividad diaria de trading. También esto es importante no solo hacer la parte del modelado sino también la parte de llevarlo a producción.

***
Ejecuta el análisis exploratorio:
Navega a la carpeta Informe escrito/ y abre el archivo informe_escrito.ipynb.
Ejecuta el notebook en un entorno Jupyter para explorar los datos de las compañías Google, Amazon y Apple.


Prueba los modelos experimentales:

Dentro de la carpeta /models_experiments/, encontrarás diferentes notebooks que contienen pruebas con modelos predictivos.
Abre y ejecuta los notebooks para ver los resultados de los experimentos y las métricas de rendimiento de cada modelo.


Datos utilizados:

El proyecto utiliza datos históricos de precios de las acciones de Google, Amazon y Apple, obtenidos a través de la API de Yahoo Finance mediante el uso de la librería yfinance.
Nuestro dataset tiene columnas como:

- Open: Precio de apertura de la acción.
- High: Precio máximo alcanzado durante el intervalo.
- Low: Precio mínimo alcanzado durante el intervalo.
- Close: Precio de cierre de la acción.
- Volume: Número de acciones negociadas.


Trading-Algoritmo-Template-main: 


En esta carpeta estan las 3 apis necesarias para correr el modelo, gestionar el flujo de las 'requests' 
e interactuar con la aplicación. Ademas de las imagenes de docker y el respectivo docker-compose para poder correr el producto como un conjunto.
 