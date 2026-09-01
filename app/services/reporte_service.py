"""
Servicio de Reportes - LibroVivo
Generacion de reportes en PDF
"""
from datetime import datetime, timedelta
from io import BytesIO
from app.config import Config
from app.models.prestamo import Prestamo
from app.models.multa import Multa
from app.models.usuario import Usuario
from app.models.libro import Libro


def generar_reporte_prestamos(fecha_inicio=None, fecha_fin=None, formato='pdf'):
    """
    Genera un reporte de prestamos
    
    Args:
        fecha_inicio: Fecha inicial (opcional)
        fecha_fin: Fecha final (opcional)
        formato: 'pdf' o 'html'
    
    Returns:
        bytes: Contenido del reporte
    """
    # Obtener datos
    sql = """
        SELECT p.*, 
               l.titulo as libro_titulo,
               u.nombre as usuario_nombre, u.apellido as usuario_apellido,
               b.nombre as bibliotecario_nombre
        FROM prestamos p
        JOIN ejemplares e ON p.ejemplar_id = e.id
        JOIN libros l ON e.libro_id = l.id
        JOIN usuarios u ON p.usuario_id = u.id
        JOIN usuarios b ON p.bibliotecario_id = b.id
        WHERE 1=1
    """
    params = []
    
    if fecha_inicio:
        sql += " AND p.fecha_prestamo >= %s"
        params.append(fecha_inicio)
    
    if fecha_fin:
        sql += " AND p.fecha_prestamo <= %s"
        params.append(fecha_fin)
    
    sql += " ORDER BY p.fecha_prestamo DESC"
    
    from app.database import ejecutar_consulta
    prestamos = ejecutar_consulta(sql, tuple(params) if params else None, fetchall=True) or []
    
    # Generar PDF
    if formato == 'pdf':
        return generar_pdf_prestamos(prestamos, fecha_inicio, fecha_fin)
    
    return prestamos


def generar_reporte_morosos():
    """
    Genera un reporte de usuarios morosos
    
    Returns:
        bytes: Contenido del PDF
    """
    morosos = Multa.top_morosos(50)
    return generar_pdf_morosos(morosos)


def generar_reporte_inventario():
    """
    Genera un reporte de inventario de libros
    
    Returns:
        bytes: Contenido del PDF
    """
    libros = Libro.listar_todos(activo=True, por_pagina=1000)
    return generar_pdf_inventario(libros)


def generar_pdf_prestamos(prestamos, fecha_inicio=None, fecha_fin=None):
    """
    Genera un PDF con el reporte de prestamos
    
    Args:
        prestamos: Lista de prestamos
        fecha_inicio: Fecha inicial
        fecha_fin: Fecha final
    
    Returns:
        bytes: Contenido del PDF
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#FF6B35'),
            spaceAfter=30
        )
        
        # Titulo
        elements.append(Paragraph("LibroVivo - Reporte de Prestamos", title_style))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Periodo
        periodo = "Periodo completo"
        if fecha_inicio and fecha_fin:
            periodo = f"Del {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}"
        elif fecha_inicio:
            periodo = f"Desde el {fecha_inicio.strftime('%d/%m/%Y')}"
        elif fecha_fin:
            periodo = f"Hasta el {fecha_fin.strftime('%d/%m/%Y')}"
        
        elements.append(Paragraph(f"<b>Periodo:</b> {periodo}", styles['Normal']))
        elements.append(Paragraph(f"<b>Fecha de generacion:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Tabla de datos
        data = [['ID', 'Libro', 'Usuario', 'Fecha Prestamo', 'Fecha Devolucion', 'Estado']]
        
        for p in prestamos:
            data.append([
                str(p['id']),
                p['libro_titulo'][:30],
                f"{p['usuario_nombre']} {p['usuario_apellido']}",
                p['fecha_prestamo'].strftime('%d/%m/%Y') if p['fecha_prestamo'] else '',
                p['fecha_devolucion_prevista'].strftime('%d/%m/%Y') if p['fecha_devolucion_prevista'] else '',
                p['estado']
            ])
        
        table = Table(data, colWidths=[0.5*inch, 2*inch, 1.5*inch, 1.2*inch, 1.2*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B35')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(table)
        
        # Totales
        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph(f"<b>Total de prestamos:</b> {len(prestamos)}", styles['Normal']))
        
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        
        return pdf
        
    except ImportError:
        # Si reportlab no esta instalado, retornar HTML
        return generar_html_prestamos(prestamos, fecha_inicio, fecha_fin)


def generar_pdf_morosos(morosos):
    """Genera PDF de morosos"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#E07A5F'),
            spaceAfter=30
        )
        
        elements.append(Paragraph("LibroVivo - Reporte de Morosos", title_style))
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph(f"<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
        elements.append(Spacer(1, 0.3 * inch))
        
        data = [['Usuario', 'Email', 'Multas Pendientes', 'Total Deuda']]
        
        for m in morosos:
            data.append([
                f"{m['nombre']} {m['apellido']}",
                m['email'],
                str(m['total_multas']),
                f"${m['total_deuda']:,.0f}"
            ])
        
        table = Table(data, colWidths=[2*inch, 2.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E07A5F')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        doc.build(elements)
        return buffer.getvalue()
        
    except ImportError:
        return None


def generar_pdf_inventario(libros):
    """Genera PDF de inventario"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#FFD23F'),
            spaceAfter=30
        )
        
        elements.append(Paragraph("LibroVivo - Inventario de Libros", title_style))
        elements.append(Spacer(1, 0.3 * inch))
        
        data = [['ID', 'Titulo', 'ISBN', 'Categoria', 'Ejemplares', 'Disponibles']]
        
        for l in libros:
            data.append([
                str(l['id']),
                l['titulo'][:40],
                l['isbn'] or '',
                l['categoria_nombre'] or '',
                str(l.get('total_ejemplares', 0)),
                str(l.get('ejemplares_disponibles', 0))
            ])
        
        table = Table(data, colWidths=[0.5*inch, 2.5*inch, 1.2*inch, 1.5*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFD23F')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        doc.build(elements)
        return buffer.getvalue()
        
    except ImportError:
        return None


def generar_html_prestamos(prestamos, fecha_inicio=None, fecha_fin=None):
    """Genera HTML como alternativa si reportlab no esta disponible"""
    html = """
    <html>
    <head>
        <title>Reporte de Prestamos - LibroVivo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #FF6B35; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th { background-color: #FF6B35; color: white; padding: 10px; }
            td { border: 1px solid #ddd; padding: 8px; text-align: center; }
            tr:nth-child(even) { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>LibroVivo - Reporte de Prestamos</h1>
        <p><b>Total:</b> """ + str(len(prestamos)) + """ prestamos</p>
        <table>
            <tr>
                <th>ID</th>
                <th>Libro</th>
                <th>Usuario</th>
                <th>Fecha Prestamo</th>
                <th>Fecha Devolucion</th>
                <th>Estado</th>
            </tr>
    """
    
    for p in prestamos:
        html += f"""
            <tr>
                <td>{p['id']}</td>
                <td>{p['libro_titulo']}</td>
                <td>{p['usuario_nombre']} {p['usuario_apellido']}</td>
                <td>{p['fecha_prestamo'].strftime('%d/%m/%Y') if p['fecha_prestamo'] else ''}</td>
                <td>{p['fecha_devolucion_prevista'].strftime('%d/%m/%Y') if p['fecha_devolucion_prevista'] else ''}</td>
                <td>{p['estado']}</td>
            </tr>
        """
    
    html += "</table></body></html>"
    return html.encode('utf-8')