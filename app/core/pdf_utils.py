from app.schemas.demande_out import Demande_out
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
#from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, HRFlowable
)

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, HRFlowable
)




def generate_pdf_report(payload: Demande_out) -> bytes:
    buffer = io.BytesIO()
    
    # --------------------------
    # Pied de page fixe
    # --------------------------
    def footer(canvas, doc):
        canvas.saveState()
        footer_text = "Document généré automatiquement par Drnoflu System - confidentiel"
        canvas.setFont("Helvetica-Oblique", 9)
        canvas.setFillColor(colors.grey)
        canvas.drawString(30*mm, 15*mm, footer_text)
        canvas.restoreState()
    
    # --------------------------
    # Création du document
    # --------------------------
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30*mm,
        leftMargin=30*mm,
        topMargin=30*mm,
        bottomMargin=30*mm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # --------------------------
    # LOGO à gauche + Texte à droite (en bleu)
    # --------------------------
    logo_path = "Api/core/logo-drnoflu.jpg"
    try:
        img = Image(logo_path, width=40*mm, height=40*mm)
        img.hAlign = 'LEFT'

        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            alignment=0,
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.black  # texte en bleu
        )
        header_text = Paragraph("Direction des Recettes Non Fiscales du Lualaba", header_style)

        header_table = Table([[img, header_text]], colWidths=[50*mm, 120*mm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (0,0), 'LEFT'),
            ('ALIGN', (1,0), (1,0), 'LEFT'),
        ]))

        elements.append(header_table)
        elements.append(Spacer(1, 12))
    except:
        pass
    
    # --------------------------
    # TITRE centré
    # --------------------------
    title_style = styles['Heading1']
    title_style.fontName = 'Helvetica-Bold'
    title_style.fontSize = 16
    title_style.alignment = 1
    title_style.textColor = colors.blue
    title_style.underline = True
    elements.append(Paragraph("Validation de votre demande d'imprimés de valeur", title_style))
    elements.append(Spacer(1, 12))
    
    # --------------------------
    # TEXTE PRINCIPAL JUSTIFIÉ
    # --------------------------
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        alignment=4,
        fontName='Helvetica',
        fontSize=12,
        leading=18
    )
    body_text = f"""
Madame, Monsieur,<br/><br/>
La Direction a l'honneur de vous informer que votre demande concernant les imprimés de valeurs a été dûment validée.<br/><br/>
Nous vous prions de bien vouloir prendre contact avec le service de comptabilité, afin d'accomplir les formalités d'usage.<br/><br/>
Veuillez agréer l'expression de nos salutations distinguées.<br/><br/>
"""
    elements.append(Paragraph(body_text, body_style))
    elements.append(Spacer(1, 12))
    
    # --------------------------
    # TABLEAU RÉCAPITULATIF
    # --------------------------
    table_data = [
        ["Champ", "Détails"],
        ["N° Demande", payload.id],
        ["Demandeur", payload.demandeur],
        ["Date de la demande", payload.date_dmde],
        ["Nature", payload.nature],
        ["Quantité demandée", str(payload.qte_dmde)],
        ["Quantité validée", str(payload.quantity)]
    ]
    table = Table(table_data, colWidths=[60*mm, 100*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 24))
    
    # --------------------------
    # SIGNATURES
    # --------------------------
    sig_style = ParagraphStyle(
        'Signature',
        parent=styles['Normal'],
        alignment=2,
        fontName='Helvetica',
        fontSize=12
    )
    cpte_style = ParagraphStyle(
        'Signature',
        parent=styles['Normal'],
        alignment=0,
        fontName='Helvetica',
        fontSize=12
    )
    demandeur_style = ParagraphStyle(
        'Signature',
        parent=styles['Normal'],
        alignment=2,
        fontName='Helvetica',
        fontSize=12
    )
    
    signature_text = f"Fait à Kolwezi, le {datetime.now().strftime('%d/%m/%Y')}<br/><br/><b>La Direction</b>"
    elements.append(Paragraph(signature_text, sig_style))
    elements.append(Spacer(1, 12))
    
    # Ligne de séparation
    elements.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.grey))
    elements.append(Spacer(1, 12))
    
    # Division de Comptabilité et Demandeur sur la même ligne
    cpte_text = "<b>Division de Comptabilité</b><br/><i>(Signature et cachet)</i>"
    demandeur_text = "<b>Demandeur</b><br/><i>(Signature)</i>"
    
    cpte_para = Paragraph(cpte_text, cpte_style)
    demandeur_para = Paragraph(demandeur_text, demandeur_style)
    
    data = [[cpte_para, demandeur_para]]
    table = Table(data, colWidths=[200, 200])
    table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 12))
    
    # --------------------------
    # BUILD PDF avec footer fixe
    # --------------------------
    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    buffer.seek(0)
    return buffer.read()


#Rejet de la demande

def generate_pdf_rejected_report(payload: Demande_out) -> bytes:
    buffer = io.BytesIO()
    
    # --------------------------
    # Pied de page fixe
    # --------------------------
    def footer(canvas, doc):
        canvas.saveState()
        footer_text = "Document généré automatiquement par Drnoflu System - confidentiel"
        canvas.setFont("Helvetica-Oblique", 9)
        canvas.setFillColor(colors.grey)
        canvas.drawString(30*mm, 15*mm, footer_text)
        canvas.restoreState()
    
    # --------------------------
    # Création du document
    # --------------------------
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30*mm,
        leftMargin=30*mm,
        topMargin=30*mm,
        bottomMargin=30*mm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # --------------------------
    # LOGO en haut à gauche
    # --------------------------
    logo_path = "Api/core/logo-drnoflu.jpg"  # Assurez-vous que le chemin est correct
    try:
        img = Image(logo_path, width=40*mm, height=40*mm)
        img.hAlign = 'LEFT'
        elements.append(img)
        elements.append(Spacer(1, 12))
    except:
        pass  # si logo absent, continuer
    
    # --------------------------
    # TITRE centré
    # --------------------------
    title_style = styles['Heading1']
    title_style.fontName = 'Helvetica-Bold'
    title_style.fontSize = 16
    title_style.alignment = 1  # centré
    title_style.textColor = colors.red
    title_style.underline = True
    elements.append(Paragraph("Rejet de votre demande d'imprimés de valeur", title_style))
    elements.append(Spacer(1, 12))
    
    # --------------------------
    # TEXTE PRINCIPAL JUSTIFIÉ
    # --------------------------
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        alignment=4,  # justifié
        fontName='Helvetica',
        fontSize=12,
        leading=18
    )
    body_text = f"""
Madame, Monsieur,<br/><br/>
La Direction a le regret de vous informer que votre demande concernant les imprimés de valeurs a été rejetée.<br/><br/>
Nous vous prions de bien vouloir prendre contact avec le service de comptabilité, pour des plus amples informations.<br/><br/>
Veuillez agréer l'expression de nos salutations distinguées.<br/><br/>

"""
    elements.append(Paragraph(body_text, body_style))
    elements.append(Spacer(1, 12))
    
    # --------------------------
    # TABLEAU RÉCAPITULATIF
    # --------------------------
    table_data = [
        ["Champ", "Détails"], 
        ["N° Demande", payload.id],       
        ["Demandeur", payload.demandeur],
        ["Date de la demande", payload.date_dmde],
        ["Nature", payload.nature],
        ["Quantité demandée", str(payload.qte_dmde)],
        ["Décision ", "Demande rejetée"]
    ]
    table = Table(table_data, colWidths=[60*mm, 100*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 24))
    
    # --------------------------
    # SIGNATURE + SCEAU à droite
    # --------------------------
    sig_style = ParagraphStyle(
        'Signature',
        parent=styles['Normal'],
        alignment=2,  # droite
        fontName='Helvetica',
        fontSize=12
    )
    
    
    signature_text = f"Fait à Kolwezi, le {datetime.now().strftime('%d/%m/%Y')}<br/><br/><b>La Direction</b>"
    elements.append(Paragraph(signature_text, sig_style))
    elements.append(Spacer(1, 12))
    
    
    # --------------------------
    # BUILD PDF avec footer fixe
    # --------------------------
    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    buffer.seek(0)
    return buffer.read()