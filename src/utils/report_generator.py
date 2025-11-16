"""
Générateur de rapports pour les incidents
Formats supportés : PDF, Excel, CSV
"""

import csv
import io
import logging
import os
from datetime import datetime
from typing import List, Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Classe pour générer des rapports d'incidents dans différents formats"""

    def __init__(self):
        self.styles = getSampleStyleSheet()

    def generate_csv(self, incidents: List[Any], include_stats: bool = False) -> str:
        """
        Génère un rapport CSV des incidents

        Args:
            incidents: Liste des incidents
            include_stats: Inclure les statistiques

        Returns:
            str: Contenu CSV
        """
        try:
            output = io.StringIO()
            writer = csv.writer(output)

            # En-têtes
            headers = [
                'Numéro',
                'Titre',
                'Description',
                'Statut',
                'Priorité',
                'Impact',
                'Domaine',
                'Déclarant',
                'Assigné à',
                'Créé le',
                'Résolu le',
                'Notes de résolution',
                'Nombre de refus'
            ]
            writer.writerow(headers)

            # Données
            for incident in incidents:
                row = [
                    incident.incident_number or '',
                    incident.title or '',
                    (incident.description or '')[:100] + '...' if incident.description and len(incident.description) > 100 else (incident.description or ''),
                    incident.status or '',
                    incident.priority or '',
                    incident.impact or '',
                    incident.domain or '',
                    incident.declarant_name or '',
                    str(incident.assigned_to) if incident.assigned_to else '',
                    incident.created_at.strftime('%Y-%m-%d %H:%M') if incident.created_at else '',
                    incident.resolved_at.strftime('%Y-%m-%d %H:%M') if incident.resolved_at else '',
                    (incident.resolution_notes or '')[:100] + '...' if incident.resolution_notes and len(incident.resolution_notes) > 100 else (incident.resolution_notes or ''),
                    str(incident.refusal_count or 0)
                ]
                writer.writerow(row)

            # Statistiques si demandées
            if include_stats:
                writer.writerow([])
                writer.writerow(['=== STATISTIQUES ==='])
                writer.writerow(['Total incidents', len(incidents)])

                # Comptage par statut
                stats_by_status = {}
                stats_by_priority = {}
                stats_by_domain = {}

                for incident in incidents:
                    status = incident.status or 'inconnu'
                    priority = incident.priority or 'inconnu'
                    domain = incident.domain or 'non_specifie'

                    stats_by_status[status] = stats_by_status.get(status, 0) + 1
                    stats_by_priority[priority] = stats_by_priority.get(priority, 0) + 1
                    stats_by_domain[domain] = stats_by_domain.get(domain, 0) + 1

                writer.writerow([])
                writer.writerow(['Par statut'])
                for status, count in stats_by_status.items():
                    writer.writerow([status, count])

                writer.writerow([])
                writer.writerow(['Par priorité'])
                for priority, count in stats_by_priority.items():
                    writer.writerow([priority, count])

                writer.writerow([])
                writer.writerow(['Par domaine'])
                for domain, count in stats_by_domain.items():
                    writer.writerow([domain, count])

            return output.getvalue()

        except Exception as e:
            logger.error(f"Erreur génération CSV : {str(e)}")
            raise

    def generate_excel(self, incidents: List[Any], include_stats: bool = False) -> bytes:
        """
        Génère un rapport Excel des incidents

        Args:
            incidents: Liste des incidents
            include_stats: Inclure les statistiques

        Returns:
            bytes: Contenu Excel
        """
        try:
            # Import openpyxl uniquement pour la génération Excel
            import openpyxl
            from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
            from openpyxl.utils import get_column_letter

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Incidents"

            # Styles
            header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF")
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )

            # En-têtes
            headers = [
                'Numéro', 'Titre', 'Description', 'Statut', 'Priorité',
                'Impact', 'Domaine', 'Déclarant', 'Assigné à',
                'Créé le', 'Résolu le', 'Notes de résolution', 'Refus'
            ]

            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_num, value=header)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.border = border

            # Données
            for row_num, incident in enumerate(incidents, 2):
                data = [
                    incident.incident_number or '',
                    incident.title or '',
                    (incident.description or '')[:200] + '...' if incident.description and len(incident.description) > 200 else (incident.description or ''),
                    incident.status or '',
                    incident.priority or '',
                    incident.impact or '',
                    incident.domain or '',
                    incident.declarant_name or '',
                    str(incident.assigned_to) if incident.assigned_to else '',
                    incident.created_at.strftime('%Y-%m-%d %H:%M') if incident.created_at else '',
                    incident.resolved_at.strftime('%Y-%m-%d %H:%M') if incident.resolved_at else '',
                    (incident.resolution_notes or '')[:200] + '...' if incident.resolution_notes and len(incident.resolution_notes) > 200 else (incident.resolution_notes or ''),
                    incident.refusal_count or 0
                ]

                for col_num, value in enumerate(data, 1):
                    cell = ws.cell(row=row_num, column=col_num, value=value)
                    cell.border = border

                    # Coloration par statut
                    if col_num == 4:  # Colonne Statut
                        if incident.status == 'resolu':
                            cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
                        elif incident.status == 'en_cours':
                            cell.fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
                        elif incident.status == 'nouveau':
                            cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

            # Ajuster la largeur des colonnes
            for col_num in range(1, len(headers) + 1):
                column_letter = get_column_letter(col_num)
                ws.column_dimensions[column_letter].width = 20

            # Ajouter les statistiques si demandées
            if include_stats:
                self._add_excel_stats(wb, incidents)

            # Sauvegarder dans un buffer
            output = io.BytesIO()
            wb.save(output)
            output.seek(0)

            return output.getvalue()

        except Exception as e:
            logger.error(f"Erreur génération Excel : {str(e)}")
            raise

    def _add_excel_stats(self, wb, incidents: List[Any]):
        """Ajoute une feuille de statistiques dans le workbook Excel"""
        # Import openpyxl pour les styles
        from openpyxl.styles import Font

        ws_stats = wb.create_sheet("Statistiques")

        # Titre
        ws_stats['A1'] = 'STATISTIQUES DES INCIDENTS'
        ws_stats['A1'].font = Font(size=16, bold=True, color="4472C4")

        # Total
        ws_stats['A3'] = 'Total incidents'
        ws_stats['B3'] = len(incidents)
        ws_stats['B3'].font = Font(bold=True)

        # Statistiques par statut
        stats_by_status = {}
        stats_by_priority = {}
        stats_by_domain = {}

        for incident in incidents:
            status = incident.status or 'inconnu'
            priority = incident.priority or 'inconnu'
            domain = incident.domain or 'non_specifie'

            stats_by_status[status] = stats_by_status.get(status, 0) + 1
            stats_by_priority[priority] = stats_by_priority.get(priority, 0) + 1
            stats_by_domain[domain] = stats_by_domain.get(domain, 0) + 1

        # Par statut
        row = 5
        ws_stats[f'A{row}'] = 'Par statut'
        ws_stats[f'A{row}'].font = Font(bold=True)
        row += 1
        for status, count in stats_by_status.items():
            ws_stats[f'A{row}'] = status
            ws_stats[f'B{row}'] = count
            row += 1

        # Par priorité
        row += 1
        ws_stats[f'A{row}'] = 'Par priorité'
        ws_stats[f'A{row}'].font = Font(bold=True)
        row += 1
        for priority, count in stats_by_priority.items():
            ws_stats[f'A{row}'] = priority
            ws_stats[f'B{row}'] = count
            row += 1

        # Par domaine
        row += 1
        ws_stats[f'A{row}'] = 'Par domaine'
        ws_stats[f'A{row}'].font = Font(bold=True)
        row += 1
        for domain, count in stats_by_domain.items():
            ws_stats[f'A{row}'] = domain
            ws_stats[f'B{row}'] = count
            row += 1

        # Ajuster largeur
        ws_stats.column_dimensions['A'].width = 25
        ws_stats.column_dimensions['B'].width = 15

    def generate_pdf(self, incidents: List[Any], include_stats: bool = False) -> bytes:
        """
        Génère un rapport PDF des incidents

        Args:
            incidents: Liste des incidents
            include_stats: Inclure les statistiques

        Returns:
            bytes: Contenu PDF
        """
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=landscape(A4),
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=18
            )

            elements = []

            # Logo Datalys
            try:
                logo_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    'static', 'image', 'logodatalys_email.jpg'
                )
                if os.path.exists(logo_path):
                    logo = Image(logo_path, width=2*inch, height=0.8*inch)
                    elements.append(logo)
                    elements.append(Spacer(1, 15))
            except Exception as e:
                logger.warning(f"Logo non trouvé pour PDF: {str(e)}")

            # Titre
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#4472C4'),
                spaceAfter=30,
                alignment=1  # Centre
            )
            elements.append(Paragraph(f"RAPPORT D'INCIDENTS", title_style))
            elements.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", self.styles['Normal']))
            elements.append(Spacer(1, 20))

            # Statistiques en haut si demandées
            if include_stats:
                stats_data = self._generate_stats_data(incidents)
                stats_table = Table(stats_data, colWidths=[2*inch, 1.5*inch])
                stats_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(stats_table)
                elements.append(Spacer(1, 20))

            # Tableau des incidents
            data = [['N°', 'Titre', 'Statut', 'Priorité', 'Domaine', 'Créé le', 'Résolu le']]

            for incident in incidents:
                row = [
                    incident.incident_number or '',
                    (incident.title or '')[:40] + '...' if incident.title and len(incident.title) > 40 else (incident.title or ''),
                    incident.status or '',
                    incident.priority or '',
                    incident.domain or '',
                    incident.created_at.strftime('%d/%m/%Y') if incident.created_at else '',
                    incident.resolved_at.strftime('%d/%m/%Y') if incident.resolved_at else '-'
                ]
                data.append(row)

            table = Table(data, colWidths=[1.2*inch, 2.5*inch, 1*inch, 0.8*inch, 1.2*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))

            elements.append(table)

            # Construire le PDF
            doc.build(elements)
            buffer.seek(0)

            return buffer.getvalue()

        except Exception as e:
            logger.error(f"Erreur génération PDF : {str(e)}")
            raise

    def _generate_stats_data(self, incidents: List[Any]) -> List[List[str]]:
        """Génère les données statistiques pour le PDF"""
        stats_by_status = {}
        stats_by_priority = {}

        for incident in incidents:
            status = incident.status or 'inconnu'
            priority = incident.priority or 'inconnu'

            stats_by_status[status] = stats_by_status.get(status, 0) + 1
            stats_by_priority[priority] = stats_by_priority.get(priority, 0) + 1

        data = [['Statistique', 'Valeur']]
        data.append(['Total incidents', str(len(incidents))])
        data.append(['', ''])  # Ligne vide

        for status, count in stats_by_status.items():
            data.append([f'Statut: {status}', str(count)])

        data.append(['', ''])  # Ligne vide

        for priority, count in stats_by_priority.items():
            data.append([f'Priorité: {priority}', str(count)])

        return data
