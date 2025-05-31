#!/usr/bin/env python3
"""
Aplicación para capturar imágenes de webcam y ajustar contraste/brillo.
Autor: Tu nombre
Fecha: 2025
"""

import cv2
import numpy as np
import logging
from typing import Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ImageSettings:
    """Configuración para ajustes de imagen."""
    brightness: float = 0  # Reducir brillo (-100 a 100)
    contrast: float = 0.8      # Reducir contraste (0.0 a 3.0)


class WebcamCapture:
    """Clase para manejar la captura de webcam y procesamiento de imágenes."""
    
    def __init__(self, camera_index: int = 0):
        """
        Inicializa la captura de webcam.
        
        Args:
            camera_index: Índice de la cámara (0 por defecto)
        """
        self.camera_index = camera_index
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_initialized = False
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def initialize_camera(self) -> bool:
        """
        Inicializa la cámara web.
        
        Returns:
            bool: True si la inicialización fue exitosa
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                self.logger.error(f"No se pudo abrir la cámara {self.camera_index}")
                return False
            
            # Configurar resolución (opcional)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            self.is_initialized = True
            self.logger.info("Cámara inicializada correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al inicializar cámara: {e}")
            return False
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Captura un frame de la webcam.
        
        Returns:
            np.ndarray o None: Frame capturado o None si hay error
        """
        if not self.is_initialized or self.cap is None:
            self.logger.warning("Cámara no inicializada")
            return None
        
        try:
            ret, frame = self.cap.read()
            if not ret:
                self.logger.warning("No se pudo capturar frame")
                return None
            
            return frame
            
        except Exception as e:
            self.logger.error(f"Error al capturar frame: {e}")
            return None
    
    def adjust_brightness_contrast(self, image: np.ndarray, 
                                 settings: ImageSettings) -> np.ndarray:
        """
        Ajusta brillo y contraste de una imagen.
        
        Args:
            image: Imagen de entrada
            settings: Configuración de ajustes
            
        Returns:
            np.ndarray: Imagen procesada
        """
        try:
            # Aplicar ajustes: nueva_imagen = contraste * imagen + brillo
            adjusted = cv2.convertScaleAbs(
                image, 
                alpha=settings.contrast,  # Factor de contraste
                beta=settings.brightness  # Valor de brillo
            )
            
            return adjusted
            
        except Exception as e:
            self.logger.error(f"Error al ajustar imagen: {e}")
            return image
    
    def save_image(self, image: np.ndarray, filename: str = "captured_image.jpg") -> bool:
        """
        Guarda una imagen en disco.
        
        Args:
            image: Imagen a guardar
            filename: Nombre del archivo
            
        Returns:
            bool: True si se guardó correctamente
        """
        try:
            # Crear directorio si no existe
            output_path = Path("output")
            output_path.mkdir(exist_ok=True)
            
            full_path = output_path / filename
            success = cv2.imwrite(str(full_path), image)
            
            if success:
                self.logger.info(f"Imagen guardada: {full_path}")
                return True
            else:
                self.logger.error(f"Error al guardar imagen: {full_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error al guardar imagen: {e}")
            return False
    
    def release_camera(self):
        """Libera los recursos de la cámara."""
        if self.cap is not None:
            self.cap.release()
            self.is_initialized = False
            self.logger.info("Cámara liberada")


class WebcamApp:
    """Aplicación principal para manejo de webcam."""
    
    def __init__(self):
        """Inicializa la aplicación."""
        self.webcam = WebcamCapture()
        self.settings = ImageSettings()
        self.running = False
    
    def setup(self) -> bool:
        """
        Configura la aplicación.
        
        Returns:
            bool: True si la configuración fue exitosa
        """
        return self.webcam.initialize_camera()
    
    def run_interactive_mode(self):
        """Ejecuta la aplicación en modo interactivo."""
        if not self.setup():
            print("Error: No se pudo inicializar la aplicación")
            return
        
        print("=== Aplicación de Webcam ===")
        print("Controles:")
        print("- Presiona 's' para capturar y guardar imagen")
        print("- Presiona 'q' para salir")
        print("- Presiona '+' para aumentar brillo")
        print("- Presiona '-' para disminuir brillo")
        print("- Presiona '[' para disminuir contraste")
        print("- Presiona ']' para aumentar contraste")
        print("\nConfiguración actual:")
        print(f"- Brillo: {self.settings.brightness}")
        print(f"- Contraste: {self.settings.contrast}")
        
        self.running = True
        frame_count = 0
        
        try:
            while self.running:
                # Capturar frame
                frame = self.webcam.capture_frame()
                if frame is None:
                    continue
                
                # Aplicar ajustes
                processed_frame = self.webcam.adjust_brightness_contrast(
                    frame, self.settings
                )
                
                # Mostrar frames
                cv2.imshow('Original', frame)
                cv2.imshow('Procesada (Brillo/Contraste Reducido)', processed_frame)
                
                # Manejar teclas
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    self.running = False
                elif key == ord('s'):
                    filename = f"imagen_{frame_count:04d}.jpg"
                    self.webcam.save_image(processed_frame, filename)
                    frame_count += 1
                elif key == ord('+') or key == ord('='):
                    self.settings.brightness = min(100, self.settings.brightness + 5)
                    print(f"Brillo: {self.settings.brightness}")
                elif key == ord('-'):
                    self.settings.brightness = max(-100, self.settings.brightness - 5)
                    print(f"Brillo: {self.settings.brightness}")
                elif key == ord('['):
                    self.settings.contrast = max(0.1, self.settings.contrast - 0.1)
                    print(f"Contraste: {self.settings.contrast:.1f}")
                elif key == ord(']'):
                    self.settings.contrast = min(3.0, self.settings.contrast + 0.1)
                    print(f"Contraste: {self.settings.contrast:.1f}")
        
        except KeyboardInterrupt:
            print("\nInterrumpido por el usuario")
        
        finally:
            self.cleanup()
    
    def capture_single_image(self, output_filename: str = "single_capture.jpg") -> bool:
        """
        Captura una sola imagen y la procesa.
        
        Args:
            output_filename: Nombre del archivo de salida
            
        Returns:
            bool: True si fue exitoso
        """
        if not self.setup():
            return False
        
        try:
            # Capturar frame
            frame = self.webcam.capture_frame()
            if frame is None:
                return False
            
            # Procesar imagen
            processed_frame = self.webcam.adjust_brightness_contrast(
                frame, self.settings
            )
            
            # Guardar imagen
            success = self.webcam.save_image(processed_frame, output_filename)
            
            return success
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Limpia recursos de la aplicación."""
        self.webcam.release_camera()
        cv2.destroyAllWindows()


def main():
    """Función principal."""
    app = WebcamApp()
    
    print("Seleccione el modo de operación:")
    print("1. Modo interactivo (visualización en tiempo real)")
    print("2. Captura única")
    
    try:
        choice = input("Ingrese su opción (1 o 2): ").strip()
        
        if choice == "1":
            app.run_interactive_mode()
        elif choice == "2":
            filename = input("Nombre del archivo (presione Enter para usar default): ").strip()
            if not filename:
                filename = "captura_unica.jpg"
            
            if app.capture_single_image(filename):
                print(f"Imagen capturada y guardada como: {filename}")
            else:
                print("Error al capturar imagen")
        else:
            print("Opción no válida")
    
    except KeyboardInterrupt:
        print("\nPrograma interrumpido")
    except Exception as e:
        print(f"Error inesperado: {e}")


if __name__ == "__main__":
    main()