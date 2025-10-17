from io import BytesIO
import traceback
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

from migrationsdb.services.digital_signature_service import DigitalSignatureService


def _build_table_books(books):
    """
    Construye una tabla de ReportLab con los libros proporcionados.
    :param books: queryset de Book
    :return: Table de ReportLab
    """
    # Construir datos de la tabla
    data = [['Título', 'Autor', 'Páginas', 'Publicado', 'Géneros']]
    for book in books:
        genres_text = ', '.join([g.name for g in book.genres.all()])
        data.append([
            (book.title[:50] + '...') if len(book.title) > 50 else book.title,
            f"{book.author.first_name} {book.author.last_name}",
            str(book.pages),
            str(book.published_date),
            (genres_text[:60] + '...') if len(genres_text) > 60 else genres_text,
        ])

    # Crear tabla con estilos
    table = Table(data, colWidths=[2.6*inch, 1.8*inch, 0.8*inch, 1.0*inch, 2.0*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    return table


def user_library_pdf(user, books, sign_document=True):
    """
    Genera PDF con ReportLab y firma opcional.
    :param books: queryset de Book
    :param sign_document: si True, intenta firmar el PDF generado
    :param user: instancia de User
    :return: HttpResponse con PDF generado
    """
    print(f"[pdf_services.user_library_pdf] Generando PDF para usuario id={user.id} "
          f"{user.first_name} {user.last_name} con {books.count()} libro(s).")

    # Generar PDF base
    buffer = BytesIO()

    # Configurar documento
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=0.5 * inch, bottomMargin=1.2 * inch,
        leftMargin=0.5 * inch, rightMargin=0.5 * inch
    )
    elements = []

    # Estilos personalizados
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Heading1'],
        fontSize=18, spaceAfter=20, alignment=1, textColor=colors.darkblue
    )
    stats_style = ParagraphStyle(
        'StatsStyle', parent=styles['Normal'],
        fontSize=11, spaceAfter=15, backColor=colors.lightgrey,
        borderPadding=8, alignment=1, textColor=colors.darkblue
    )

    # Título y estadísticas
    title = Paragraph(f"Biblioteca de {user.first_name} {user.last_name}", title_style)
    elements.append(title)

    stats_text = f"<b>Total de libros:</b> {books.count()}<br/><b>Usuario:</b> {user.first_name} {user.last_name} ({user.email})"
    elements.append(Paragraph(stats_text, stats_style))
    elements.append(Spacer(1, 12))

    # Tabla de libros
    elements.append(_build_table_books(books))
    elements.append(Spacer(1, 100))  # espacio visual para firma

    # Construir PDF
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    print(f"[pdf_services.user_library_pdf] PDF base generado: {len(pdf_bytes)} bytes")

    # Verificar encabezado PDF
    if not pdf_bytes.startswith(b'%PDF-'):
        print(f"[pdf_services.user_library_pdf] Atención: el PDF no inicia con %PDF-. Cabecera={pdf_bytes[:8]!r}")

    # Para firmar el PDF
    if sign_document:
        print("[pdf_services.user_library_pdf] Intentando firmar el PDF...")
        try:
            signer = DigitalSignatureService()
            signed_pdf = signer.sign_pdf(
                pdf_bytes,
                reason="Biblioteca Personal - Lista de libros",
                location="Sistema de Gestión de Biblioteca",
                add_visual_signature=True
            )
            print(f"[pdf_services.user_library_pdf] Resultado firma: {len(signed_pdf)} bytes")
            if len(signed_pdf) > len(pdf_bytes):
                print("[pdf_services.user_library_pdf] Firma aplicada. Reemplazando contenido.")
                pdf_bytes = signed_pdf
            else:
                print("[pdf_services.user_library_pdf] Tamaño no cambió o firma no aplicada. Se usa PDF original.")
        except Exception as e:
            print(f"[pdf_services.user_library_pdf] Error al firmar: {e}")
            traceback.print_exc()
            print("[pdf_services.user_library_pdf] Se devuelve el PDF original sin firmar.")

    # Preparar respuesta HTTP
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    filename = f"biblioteca_{user.first_name}_{user.last_name}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    print(f"[pdf_services.user_library_pdf] Respuesta lista. Nombre archivo: {filename}, bytes={len(pdf_bytes)}")
    return response


def books_report_pdf(books, sign_document=True):
    """
    Genera un reporte general de libros y firma opcionalmente.
    :param books: queryset de Book
    :param sign_document: si True, intenta firmar el PDF generado
    :return: HttpResponse con PDF generado
    """
    print(f"[pdf_services.books_report_pdf] Generando reporte de {books.count()} libro(s).")

    # Generar PDF base
    buffer = BytesIO()

    # Configurar documento
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=0.5 * inch, bottomMargin=1.2 * inch,
        leftMargin=0.5 * inch, rightMargin=0.5 * inch
    )
    elements = []

    # Estilos personalizados
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Heading1'],
        fontSize=18, spaceAfter=20, alignment=1, textColor=colors.darkblue
    )
    elements.append(Paragraph("Reporte de Libros", title_style))
    elements.append(_build_table_books(books))
    elements.append(Spacer(1, 100))

    # Construir PDF
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    print(f"[pdf_services.books_report_pdf] PDF base generado: {len(pdf_bytes)} bytes")

    # Verificar encabezado PDF
    if not pdf_bytes.startswith(b'%PDF-'):
        print(f"[pdf_services.books_report_pdf] Atención: el PDF no inicia con %PDF-. Cabecera={pdf_bytes[:8]!r}")


    # Para firmar el PDF
    if sign_document:
        print("[pdf_services.books_report_pdf] Intentando firmar el PDF...")
        try:
            signer = DigitalSignatureService()
            signed_pdf = signer.sign_pdf(
                pdf_bytes,
                reason="Reporte general de libros",
                location="Sistema de Gestión de Biblioteca",
                add_visual_signature=True
            )
            print(f"[pdf_services.books_report_pdf] Resultado firma: {len(signed_pdf)} bytes")
            if len(signed_pdf) > len(pdf_bytes):
                print("[pdf_services.books_report_pdf] Firma aplicada. Reemplazando contenido.")
                pdf_bytes = signed_pdf
            else:
                print("[pdf_services.books_report_pdf] Tamaño no cambió o firma no aplicada. Se usa PDF original.")
        except Exception as e:
            print(f"[pdf_services.books_report_pdf] Error al firmar: {e}")
            traceback.print_exc()
            print("[pdf_services.books_report_pdf] Se devuelve el PDF original sin firmar.")

    # Preparar respuesta HTTP
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_libros.pdf"'
    print(f"[pdf_services.books_report_pdf] Respuesta lista. bytes={len(pdf_bytes)}")
    return response