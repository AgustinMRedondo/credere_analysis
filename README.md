# Predicción de Activos Distressed en el Mercado Inmobiliario de Panamá

Este proyecto utiliza análisis de datos y machine learning para estudiar el mercado inmobiliario en Panamá, con un enfoque en identificar activos "distressed" (en riesgo de devaluación significativa). Utilizando modelos de series temporales y un clasificador de machine learning, proyectamos precios futuros y determinamos la probabilidad de que un activo esté en distress. 

## Tabla de Contenidos
- [Descripción del Proyecto](#descripción-del-proyecto)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Metodología](#metodología)
- [Limitaciones](#limitaciones)
- [Contribuciones](#contribuciones)

## Descripción del Proyecto

El proyecto se centra en analizar las variaciones de precios en el mercado inmobiliario de Panamá y determinar la probabilidad de que un activo esté distressed en el futuro cercano. Utilizando datos históricos de precios por metro cuadrado obtenidos de properstar.es, creamos un conjunto de datos que incluye diferentes zonas y tipologías de propiedades. Con el modelo de series temporales Prophet, se proyectan precios hasta el año 2028, lo cual permite identificar tendencias y potenciales puntos de inflexión en el mercado. Posteriormente, un clasificador Random Forest predice la probabilidad de distress de un activo a partir de datos básicos independientes, brindando una herramienta precisa y valiosa para inversores y profesionales del sector.

## Uso

1. Interfaz de Usuario: Al ejecutar la aplicación, puedes acceder a una interfaz en localhost que permite ingresar datos básicos de una propiedad (precio, zona y tipo).
2. Predicciones: Tras ingresar los datos, el modelo predice la probabilidad de que el activo esté distressed y proporciona una visualización de los precios proyectados, así como un análisis de punto de inflexión en la probabilidad de distress.

## Estructura del proyecto 

	•	deploy_model.py: Archivo principal de Streamlit que ejecuta la aplicación y muestra la interfaz.
	•	ml.py: Contiene la función ml, la cual gestiona el procesamiento de los datos de entrada y realiza las predicciones.
	•	models/: Directorio que incluye el modelo entrenado Random Forest y el modelo Prophet.
	•	encoders/: Contiene el codificador necesario para procesar las variables categóricas.

## Metodología

1. Recopilación de Datos: Utilizamos datos históricos de precios desde 2021 a 2024 extraídos de properstar.es para analizar el precio por metro cuadrado en diferentes zonas de Panamá.

2. Proyección de Precios: Aplicamos el modelo Prophet para proyectar precios hasta el 2028, con el fin de comprender cómo pueden evolucionar las tendencias del mercado en los próximos años.

3. Clasificación de Distress: Generamos un indicador de distress mediante la comparación entre el precio actual y las proyecciones futuras. Este indicador tiene en cuenta la tipología de la propiedad y la zona, asignando puntuaciones de distress para crear un perfil de riesgo.

4. Modelo Predictivo: Entrenamos un clasificador Random Forest con estos datos procesados, permitiendo predecir si un activo estará distressed en función de sus características.

5. Punto de Inflexión: La aplicación calcula un rango de precios entre -10,000 y +10,000 USD en torno al precio del activo, con el objetivo de encontrar el punto de inflexión en el cual la probabilidad de distress baja del 90%.

## Limitaciones

	•	La precisión del modelo depende en gran medida de la calidad y consistencia de los datos de entrenamiento.
	•	Los datos recopilados no han sido verificados por entidades reguladas, lo cual podría impactar la fiabilidad del modelo para decisiones de inversión.



