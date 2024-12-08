import cv2
import numpy as np
from pyzbar.pyzbar import decode
import csv
import pygame  # Para emitir un sonido

# Ruta del archivo CSV con las secuencias válidas
csv_file = "sillas_qr.csv"

# Inicializar pygame para sonido
pygame.mixer.init()

# Cargar las secuencias válidas desde el CSV
def cargar_secuencias(csv_file):
    secuencias_validas = {}
    with open(csv_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            secuencias_validas[row["Secuencia"]] = row["Silla"]
    return secuencias_validas

# Verificar si el QR es válido
def verificar_qr(secuencia, secuencias_validas):
    if secuencia in secuencias_validas:
        return f"QR Valido: {secuencias_validas[secuencia]}"
    return "QR Invalido"

# Reproducir un sonido cuando un QR es leído
def emitir_sonido():
    try:
        pygame.mixer.music.load("sonido_correcto.mp3")  # Cambia el nombre si tu archivo tiene otro nombre
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():  # Espera a que termine el sonido
            pygame.time.Clock().tick(10)
    except pygame.error as e:
        print(f"Error al reproducir sonido: {e}")

# Escanear QR en tiempo real usando la cámara
def escanear_qr_en_vivo():
    secuencias_validas = cargar_secuencias(csv_file)

    # Abrir la cámara
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo acceder a la cámara.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo capturar el video.")
            break

        # Decodificar QR en el cuadro capturado
        decoded_objects = decode(frame)
        for obj in decoded_objects:
            secuencia = obj.data.decode("utf-8")
            resultado = verificar_qr(secuencia, secuencias_validas)

            # Si el QR es válido, emitir un sonido y detener la cámara
            if "Válido" in resultado:
                emitir_sonido()
                print(resultado)
                cap.release()  # Detener la cámara
                cv2.destroyAllWindows()  # Cerrar todas las ventanas de OpenCV
                return  # Salir de la función

            # Dibujar el rectángulo alrededor del QR y mostrar el resultado
            points = obj.polygon
            if len(points) > 4:  # Para polígonos irregulares
                hull = cv2.convexHull(np.array([p for p in points], dtype=np.float32))
                points = hull
            n = len(points)
            for j in range(n):
                cv2.line(frame, tuple(points[j]), tuple(points[(j+1) % n]), (0, 255, 0), 3)

            # Mostrar el resultado en pantalla
            cv2.putText(frame, resultado, (obj.rect.left, obj.rect.top - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Mostrar el video
        cv2.imshow("Escáner de QR", frame)

        # Salir si se presiona 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Ejecutar el escáner
if __name__ == "__main__":
    escanear_qr_en_vivo()
