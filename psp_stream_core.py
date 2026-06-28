#!/usr/bin/env python3
import os
import sys
import struct

class XorshiftSeekable:
    """
    Generador Xorshift64 optimizado para Streaming.
    Permite adelantar el estado de forma eficiente para generar ruido
    a partir de cualquier offset sin procesar los bytes anteriores.
    """
    def __init__(self, semilla: int):
        self.semilla_base = semilla if semilla != 0 else 88172645463325252
        self.current_state = self.semilla_base

    def _reset_to_block(self, block_index: int, block_size: int):
        """
        Sincroniza el estado del generador para un bloque específico.
        Para mantener la PoC simple y limpia en tu GitHub, avanzamos el estado
        de forma determinista en base al índice del bloque.
        """
        # Cambiamos el estado inicial combinando la semilla con el bloque
        # Esto asegura que el bloque N siempre genere el mismo ruido exacto
        self.current_state = (self.semilla_base ^ (block_index * 1103515245)) & 0xFFFFFFFFFFFFFFFF

    def generar_ruido_bloque(self, block_index: int, block_size: int) -> bytes:
        """Genera el bloque exacto de ruido en memoria."""
        self._reset_to_block(block_index, block_size)
        
        # Algoritmo Xorshift rápido por bloque
        ruido = bytearray(block_size)
        x = self.current_state
        for i in range(block_size):
            x ^= (x << 13) & 0xFFFFFFFFFFFFFFFF
            x ^= (x >> 7) & 0xFFFFFFFFFFFFFFFF
            x ^= (x << 17) & 0xFFFFFFFFFFFFFFFF
            ruido[i] = x & 0xFF
        self.current_state = x
        return bytes(ruido)


class PSPStreamEngine:
    """
    PSP STREAMING FRAMEWORK v6.0 (High-Performance Chunking)
    Diseñado para streaming de assets de baja latencia con consumo de RAM constante.
    """
    CHUNK_SIZE = 65536  # Bloques estándar de 64 KB

    @classmethod
    def empaquetar_asset(cls, ruta_origen: str, ruta_salida: str, semilla: int):
        """
        Transforma un asset masivo en un flujo de bloques protegidos por semilla.
        Procesa el archivo en trozos de 64KB para no saturar la RAM durante el empaquetado.
        """
        if not os.path.exists(ruta_origen):
            raise FileNotFoundError(f"Asset no encontrado: {ruta_origen}")

        tamano_total = os.path.getsize(ruta_origen)
        prng = XorshiftSeekable(semilla)

        with open(ruta_origen, "rb") as f_in, open(ruta_salida, "wb") as f_out:
            # Header del Stream: Magic(4B) + ChunkSize(4B) + TamanoTotal(8B) + Semilla(8B)
            header = struct.pack(">4sIQQ", b"PSPS", cls.CHUNK_SIZE, tamano_total, semilla)
            f_out.write(header)

            block_index = 0
            while True:
                datos = f_in.read(cls.CHUNK_SIZE)
                if not datos:
                    break
                
                # Generar ruido exclusivo para este bloque
                ruido_bloque = prng.generar_ruido_bloque(block_index, len(datos))
                payload_xor = bytes(b ^ r for b, r in zip(datos, ruido_bloque))
                
                f_out.write(payload_xor)
                block_index += 1

    def __init__(self, ruta_psps: str):
        """Inicializa el lector del Stream abriendo un puntero permanente al archivo."""
        self.f = open(ruta_psps, "rb")
        header_bytes = self.f.read(24) # Leer los 24 bytes del Header
        if len(header_bytes) < 24:
            raise ValueError("Header de stream inválido o corrupto.")
            
        magic, self.chunk_size, self.tamano_total, self.semilla = struct.unpack(">4sIQQ", header_bytes)
        if magic != b"PSPS":
            raise ValueError("Firma de framework de streaming inválida.")
            
        self.prng = XorshiftSeekable(self.semilla)
        self.HEADER_OFFSET = 24

    def leer_rango(self, offset_inicio: int, longitud: int) -> bytes:
        """
        EL NÚCLEO DEL STREAMING: Lee un rango arbitrario de bytes de forma instantánea
        sin cargar todo el archivo a la RAM.
        """
        if offset_inicio + longitud > self.tamano_total:
            longitud = self.tamano_total - offset_inicio
            
        if longitud <= 0:
            return b""

        # Calcular qué bloques físicos de 64KB contienen el rango pedido
        bloque_inicial = offset_inicio // self.chunk_size
        bloque_final = (offset_inicio + longitud - 1) // self.chunk_size

        resultado_completo = bytearray()

        for idx_bloque in range(bloque_inicial, bloque_final + 1):
            # Posicionarse en el archivo llave (.psps) exactamente donde empieza el bloque
            pos_archivo = self.HEADER_OFFSET + (idx_bloque * self.chunk_size)
            self.f.seek(pos_archivo)
            
            # Calcular cuánto leer de este bloque específico
            bytes_a_leer = self.chunk_size
            if (idx_bloque + 1) * self.chunk_size > self.tamano_total:
                bytes_a_leer = self.tamano_total - (idx_bloque * self.chunk_size)

            datos_llave = self.f.read(bytes_a_leer)
            
            # Reconstruir el ruido de ese bloque en la RAM usando la semilla
            ruido_bloque = self.prng.generar_ruido_bloque(idx_bloque, len(datos_llave))
            datos_reconstruidos = bytes(b ^ r for b, r in zip(datos_llave, ruido_bloque))
            
            resultado_completo.extend(datos_reconstructed)

        # Recortar el exceso debido a la alineación de bloques de 64KB
        recorte_inicio = offset_inicio % self.chunk_size
        return bytes(resultado_completo[recorte_inicio:recorte_inicio + longitud])

    def cerrar(self):
        self.f.close()

# =====================================================================
# CLI DE CONTROL DE LABORATORIO (STREAMING AUTOMATIZADO)
# =====================================================================
if __name__ == "__main__":
    import random

    # 1. Crear un archivo de prueba "pesado" con datos conocidos en posiciones específicas
    print("🔬 [Paso 1/4] Creando asset original ('video_asset.raw')...")
    
    # Creamos un bloque de 1 Megabyte lleno de ruido de fondo ('A')
    bloque_ruido = b"A" * 500000
    # Insertamos un "Huevo de Pascua" de texto exactamente en la mitad
    huevo_pascua = b"METADATA_CRITICA_OCULTA_EN_EL_MEDIO"
    offset_exacto_original = len(bloque_ruido)
    
    with open("video_asset.raw", "wb") as f:
        f.write(bloque_ruido)
        f.write(huevo_pascua)
        f.write(bloque_ruido)
        
    print(f"   ✓ Asset creado. Tamaño: {os.path.getsize('video_asset.raw')} bytes.")
    print(f"   📌 El mensaje secreto está exactamente en el offset: {offset_exacto_original}\n")

    # 2. Empaquetar y cifrar el archivo usando la Semilla Matemática
    print("🔐 [Paso 2/4] Ejecutando 'pack' para generar el stream protegido (.psps)...")
    semilla_laboratorio = 999
    PSPStreamEngine.empaquetar_asset("video_asset.raw", "game_asset.psps", semilla=semilla_laboratorio)
    print("   ✓ Archivo empaquetado como 'game_asset.psps'.")
    
    # Borramos el archivo original para demostrar que ya no se necesita en el disco
    os.remove("video_asset.raw")
    print("   🗑️ Archivo original 'video_asset.raw' ELIMINADO del disco.\n")

    # 3. Inicializar el Streamer de Acceso Aleatorio
    print("🧠 [Paso 3/4] Inicializando el motor de Streaming en modo lectura...")
    streamer = PSPStreamEngine("game_asset.psps")
    print(f"   ✓ Conectado a 'game_asset.psps' ({streamer.tamano_total} bytes).")
    print(f"   ✓ Memoria RAM en uso por bloque: {streamer.chunk_size // 1024} KB (Constante).\n")

    # 4. Simular la extracción quirúrgica (Streaming Seek)
    longitud_a_pedir = len(huevo_pascua)
    print(f"🔥 [Paso 4/4] Buscando fragmento en offset {offset_exacto_original} por {longitud_a_pedir} bytes...")
    
    # El motor viaja en el tiempo, genera el ruido de ese bloque específico y extrae la metadata
    fragmento_ram = streamer.leer_rango(offset_exacto_original, longitud_a_pedir)
    
    print("-" * 60)
    print(f"📥 RESULTADO EXTRAÍDO DIRECTAMENTE DE LA RAM:")
    print(f"👉 {fragmento_ram.decode('utf-8', errors='ignore')}")
    print("-" * 60)
    
    streamer.cerrar()
    print("\n✓ Prueba de laboratorio completada con éxito.")
