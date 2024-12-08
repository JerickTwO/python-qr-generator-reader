import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import os
import secrets
import csv

# Variables globales
logo_path = "Logo-UFC.png"  # Ruta al logo del evento
output_pdf = "sillas_evento.pdf"  # Nombre del PDF de salida
temp_qr_folder = "qr_codes"  # Carpeta para guardar los QR temporales
csv_file = "sillas_qr.csv"  # Archivo para guardar las secuencias
os.makedirs(temp_qr_folder, exist_ok=True)

# Generar secuencia aleatoria y asociarla con las sillas
def generar_secuencias():
    secuencias = []
    for i in range(1, 71):
        random_id = secrets.token_hex(16)  # Generar una secuencia aleatoria segura
        secuencias.append((f"Silla {i}", random_id, "No leído"))
    # Guardar las secuencias en un archivo CSV
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Silla", "Secuencia", "Estado"])
        writer.writerows(secuencias)
    return secuencias


# Generar los códigos QR
def generar_qr(secuencias):
    for silla, random_id, estado in secuencias:
        qr = qrcode.QRCode(box_size=10, border=2)
        qr.add_data(random_id)  # Usar la secuencia única
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        qr_path = os.path.join(temp_qr_folder, f"{silla}.png")
        img.save(qr_path)

# Crear el PDF
def crear_pdf(secuencias):
    c = canvas.Canvas(output_pdf, pagesize=letter)
    width, height = letter

    # Logo
    logo = ImageReader(logo_path)
    logo_width, logo_height = 150, 150  # Tamaño del logo

    for silla, _ in secuencias:
        qr_path = os.path.join(temp_qr_folder, f"{silla}.png")
        
        # Añadir logo
        c.drawImage(logo, (width - logo_width) / 2, height - logo_height - 50, 
                    width=logo_width, height=logo_height)

        # Añadir QR
        c.drawImage(qr_path, (width - 200) / 2, (height - logo_height - 300), width=200, height=200)

        # Añadir texto
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - logo_height - 280, silla)

        c.showPage()  # Crear nueva página

    c.save()

# Limpieza de archivos temporales
def limpiar_temp():
    for file in os.listdir(temp_qr_folder):
        os.remove(os.path.join(temp_qr_folder, file))
    os.rmdir(temp_qr_folder)

# Ejecutar las funciones
secuencias = generar_secuencias()
print("Secuencias generadas:", secuencias)  # Verificar contenido
generar_qr(secuencias)

crear_pdf(secuencias)
limpiar_temp()

print(f"PDF generado: {output_pdf}")
print(f"Secuencias guardadas en: {csv_file}")
