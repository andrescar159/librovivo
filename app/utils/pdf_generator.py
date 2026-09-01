"""
Generador de PDFs - LibroVivo
Wrapper para facilitar la generacion de documentos PDF
"""
from io import BytesIO
from datetime import datetime


def generar_pdf_simple(titulo, subtitulo, datos, columnas, anchos=None):
    """
    Genera un PDF simple con tabla de datos
    
    Args:
        titulo: Titulo del documento
        subtitulo: Subtitulo o descripcion
        datos: Lista de diccionarios con los datos
        columnas: Lista de tuplas (clave, encabezado) 
                  ej: [('nombre', 'Nombre'), ('email', 'Correo')]
        anchos: Lista de anchos de columnas (opcional)
    
    Returns:
        bytes: Contenido del PDF
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        styles = getSampleStyleSheet()
        
        # Titulo
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#FF6B35'),
            spaceAfter=20
        )
        elements.append(Paragraph(f"LibroVivo - {titulo}", title_style))
        
        # Subtitulo
        if subtitulo:
            elements.append(Paragraph(f"<b>{subtitulo}</b>", styles['Normal']))
        
        elements.append(Paragraph(
            f"<i>Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}</i>",
            styles['Normal']
        ))
        elements.append(Spacer(1, 20))
        
        # Tabla
        if datos:
            # Encabezados
            headers = [col[1] for col in columnas]
            data = [headers]
            
            # Filas
            for item in datos:
                row = []
                for col in columnas:
                    valor = item.get(col[0], '')
                    if valor is None:
                        valor = ''
                    row.append(str(valor))
                data.append(row)
            
            # Crear tabla
            if anchos:
                table = Table(data, colWidths=anchos)
            else:
                table = Table(data)
            
            # Estilo
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B35')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ]))
            
            elements.append(table)
        else:
            elements.append(Paragraph("<i>No hay datos para mostrar</i>", styles['Normal']))
        
        # Total
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"<b>Total de registros:</b> {len(datos)}", styles['Normal']))
        
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        
        return pdf
        
    except ImportError:
        # Si reportlab no esta instalado
        return None


def generar_pdf_tarjeta_prestamo(prestamo):
    """
    Genera una tarjeta/ticket de prestamo
    
    Args:
        prestamo: Datos del prestamo
    
    Returns:
        bytes: Contenido del PDF
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A6
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A6)
        elements = []
        
        styles = getSampleStyleSheet()
        
        # Titulo
        title_style = ParagraphStyle(
            'TicketTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#FF6B35'),
            alignment=1,  # Centrado
            spaceAfter=15
        )
        elements.append(Paragraph("LIBROVIVO", title_style))
        elements.append(Paragraph("<b>Comprobante de Prestamo</b>", styles['Normal']))
        elements.append(Spacer(1, 15))
        
        # Datos
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=8
        )
        
        elements.append(Paragraph(f"<b>Libro:</b> {prestamo.get('libro_titulo', '')}", info_style))
        elements.append(Paragraph(f"<b>Usuario:</b> {prestamo.get('usuario_nombre', '')} {prestamo.get('usuario_apellido', '')}", info_style))
        elements.append(Paragraph(f"<b>Fecha prestamo:</b> {prestamo.get('fecha_prestamo', '')}", info_style))
        elements.append(Paragraph(f"<b>Fecha devolucion:</b> {prestamo.get('fecha_devolucion_prevista', '')}", info_style))
        elements.append(Paragraph(f"<b>Bibliotecario:</b> {prestamo.get('bibliotecario_nombre', '')}", info_style))
        elements.append(Spacer(1, 15))
        
        # Nota
        elements.append(Paragraph(
            "<i>Devuelve el libro a tiempo para evitar multas.<br/>"
            f"Horario: {Config.HORARIO_APERTURA}:00 - {Config.HORARIO_CIERRE}:00</i>",
            ParagraphStyle('Nota', parent=styles['Normal'], fontSize=8, alignment=1)
        ))
        
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        
        return pdf
        
    except ImportError:
        return None