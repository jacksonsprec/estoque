from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

DATE_TIME_FORMAT = "%d/%m/%Y %H:%M:%S"


def exportar_relatorio_pdf(estoque, arquivo):
    materiais = sorted(
        estoque["itens"].items(),
        key=lambda item: (item[1].get("nome", item[0]).lower(), item[0]),
    )

    pdf = canvas.Canvas(arquivo, pagesize=letter)
    pdf.setTitle("Relatório de Estoque")
    pdf.setAuthor("Gerenciador de Estoque")
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, 760, "Relatório de Estoque")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 742, f"Gerado em: {datetime.now().strftime(DATE_TIME_FORMAT)}")

    total_itens = len(materiais)
    total_quantidade = sum(item["quantidade"] for _, item in materiais)
    pdf.drawString(50, 724, f"Total de materiais cadastrados: {total_itens}")
    pdf.drawString(50, 708, f"Quantidade total em estoque: {total_quantidade}")

    y = 680
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(50, y, "Material")
    pdf.drawString(260, y, "Quantidade")
    pdf.drawString(360, y, "Validade")
    pdf.drawString(470, y, "Descrição")
    y -= 16

    pdf.setFont("Helvetica", 8)
    for chave, item in materiais:
        nome = item.get("nome", chave)
        descricao = (item.get("descricao") or "")[:55]
        validade = item.get("validade") or "-"
        pdf.drawString(50, y, nome[:28])
        pdf.drawString(260, y, str(item.get("quantidade", 0)))
        pdf.drawString(360, y, validade)
        pdf.drawString(470, y, descricao)
        y -= 12
        if y < 60:
            pdf.showPage()
            y = 760
            pdf.setFont("Helvetica-Bold", 9)
            pdf.drawString(50, y, "Material")
            pdf.drawString(260, y, "Quantidade")
            pdf.drawString(360, y, "Validade")
            pdf.drawString(470, y, "Descrição")
            y -= 16
            pdf.setFont("Helvetica", 8)

    pdf.save()
