# LibroVivo - Sistema de Gestion Bibliotecaria

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)

Sistema web para la gestion de bibliotecas escolares desarrollado con Python, Flask y MySQL.

## Caracteristicas

- **Roles de usuario**: Administrador, Bibliotecario y Estudiante
- **Gestion de libros**: CRUD completo con clasificacion Dewey
- **Ejemplares**: Control de copias, codigos de barras, "solo lectura en sala"
- **Prestamos**: Flujo en 3 pasos, devoluciones, renovaciones (max 3)
- **Multas**: Calculo automatico $500/dia (max $7.000 COP)
- **Reservas**: Maximo 2 activas, 3 dias de vigencia
- **Resenas**: Calificacion 1-5 estrellas, moderacion por admin
- **Reportes**: PDF con ReportLab (prestamos, morosos, inventario)
- **Notificaciones**: Recordatorios de vencimiento, reservas disponibles

## Tecnologias

- **Backend**: Python 3.10+, Flask
- **Base de datos**: MySQL (XAMPP)
- **Frontend**: HTML5, Bootstrap 5, CSS3
- **Seguridad**: bcrypt para contrasenas, sesiones Flask
- **Reportes**: ReportLab para PDF

## Instalacion

### 1. Requisitos previos

- Python 3.10 o superior
- XAMPP con MySQL activo
- pip (gestor de paquetes Python)

### 2. Clonar o descargar el proyecto

```bash
cd /ruta/deseada
# Extraer el proyecto librovivo/