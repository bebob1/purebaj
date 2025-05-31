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
    brightness: float = -50.0  # Reducir brillo (-100 a 100)
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
    """Aplicación principal para captura automática de webcam."""
    
    def __init__(self):
        """Inicializa la aplicación."""
        self.webcam = WebcamCapture()
        self.settings = ImageSettings()
    
    def setup(self) -> bool:
        """
        Configura la aplicación.
        
        Returns:
            bool: True si la configuración fue exitosa
        """
        return self.webcam.initialize_camera()
    

    
    def capture_single_image(self, output_filename: str) -> bool:
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


def generate_filename() -> str:
    """
    Genera un nombre de archivo único basado en timestamp.
    
    Returns:
        str: Nombre de archivo con timestamp
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"captura_{timestamp}.jpg"


def main():
    """Función principal - Captura automática sin interacción."""
    print("=== Captura Automática de Webcam ===")
    print("Inicializando cámara...")
    
    app = WebcamApp()
    
    try:
        # Generar nombre de archivo único
        filename = generate_filename()
        
        print(f"Capturando imagen...")
        
        if app.capture_single_image(filename):
            print(f"✓ Imagen capturada exitosamente: output/{filename}")
            print(f"✓ Brillo aplicado: {app.settings.brightness}")
            print(f"✓ Contraste aplicado: {app.settings.contrast}")
        else:
            print("✗ Error al capturar la imagen")
            return 1
    
    except KeyboardInterrupt:
        print("\n✗ Programa interrumpido por el usuario")
        return 1
    except Exception as e:
        print(f"✗ Error inesperado: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)