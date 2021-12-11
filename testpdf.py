from fpdf import FPDF  # fpdf class
from PIL import Image
import io
import base64
pdf = FPDF()
pdf.add_page()
pdf.set_font('Arial', 'B', 18)
pdf.cell(40, 10, 'GRACIAS POR UTILIZAR NUESTRO SERVICIO DE EVENTOS.')
pdf.set_draw_color(255, 0, 0)
pdf.line(20, 20, 160, 20)
pdf.set_font('Arial','B', 16)
pdf.cell(-30,120,"This is a multi-line text string\n\nNew line\nNew line"); 

pdf.image('C:\\Users\\Pablo\\OneDrive\\Escritorio\\Master\\TA\\Práctica\\P1\\Código\\celta.png', x=85, y=100, w=40, h=40)

pdf.output('ticket1.pdf', 'F')