# Matrix OEE (Overall Equipment Effectiveness) 🏭📊

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![HTML/CSS](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)

Sistema integral para el cálculo, monitoreo y visualización del indicador **OEE (Overall Equipment Effectiveness)** de maquinaria industrial. Desarrollado como parte del ecosistema Matrix Flow, ayuda a identificar cuellos de botella y mejorar la eficiencia en la producción.

## 🚀 Características Principales

- **Dashboard Interactivo**: Visualización en tiempo real de la disponibilidad, rendimiento y calidad.
- **Cálculo Automático**: Algoritmos para procesar tiempos de parada, producción teórica y real.
- **Reportes y Gráficos**: Análisis detallados mediante componentes visuales (HTML/JS/CSS).
- **Backend Ligero**: API y servidor web implementados con Flask (Python).
- **Manual Integrado**: Documentación detallada del funcionamiento y fórmulas del OEE.

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python 3, Flask, Werkzeug, Jinja2
- **Frontend**: HTML5, CSS3, JavaScript Vainilla
- **Integración**: Requests, urllib3 para comunicación con otros módulos

## 📂 Estructura del Proyecto

```text
Sistema-OEE-/
├── dashboard_demo/       # Interfaz gráfica y assets del dashboard (HTML/JS/CSS)
├── matrix_oee_manual/    # Lógica central (Flask App), scripts de base de datos y logs
└── requirements.txt      # Dependencias del proyecto
```

## 🚀 Instalación y Ejecución Local

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/MAYK2/Sistema-OEE-.git
   cd Sistema-OEE-
   ```

2. **Crear y activar el entorno virtual**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # En Linux/Mac
   # venv\Scripts\activate   # En Windows
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación**
   ```bash
   cd matrix_oee_manual
   python run.py
   ```

---
**Desarrollado para formar parte del ecosistema Matrix Flow.**
