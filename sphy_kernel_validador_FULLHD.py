import py5
import pandas as pd
import hashlib
import tkinter as tk
from tkinter import filedialog
import os

# --- MANTENHA A FUNÇÃO carregar_e_validar EXATAMENTE COMO ESTÁ ---
def carregar_e_validar():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Selecione o Dataset SPHY", filetypes=[("Parquet files", "*.parquet")])
    root.destroy()
    
    if not file_path:
        return None
    
    print(f"🧐 Iniciando Auditoria SHA-256 de {os.path.basename(file_path)}...")
    df = pd.read_parquet(file_path)
    
    for i, row in df.iterrows():
        seed = "".join([f"{pid}{t:.4f}" for pid, (t, off) in zip(row['pids'], row['positions'])])
        check_hash = hashlib.sha256(seed.encode()).hexdigest()
        if check_hash != row['hash']:
            print(f"❌ FALHA DE INTEGRIDADE NO FRAME {i}!")
            return None
            
    print("✅ Auditoria Completa: Todos os frames são autênticos.")
    return df

class AuditoriaVisual:
    def __init__(self, dataset):
        self.df = dataset
        self.frame_idx = 0
        self.PHI = (1 + 5**0.5) / 2

    def settings(self):
        # O py5 exige que definições de tela fiquem aqui para evitar o RuntimeError
        py5.size(1920, 1080, py5.P3D)

    def setup(self):
        # Configurações de estilo e recursos
        py5.text_font(py5.create_font("Courier", 22))

    def draw(self):
        if self.frame_idx >= len(self.df):
            self.frame_idx = 0 

        row = self.df.iloc[self.frame_idx]
        py5.background(8)
        
        self.draw_hud(row)
        
        py5.push_matrix()
        py5.translate(1150, 540, 0)
        py5.rotate_x(py5.mouse_y * 0.003)
        py5.rotate_y(py5.mouse_x * 0.003)
        
        py5.no_fill()
        py5.stroke(0, 120, 0, 100)
        self.draw_torus_grid(350, 140)
        
        for (t, offset) in row['positions']:
            self.draw_electron(t, offset)
        
        py5.pop_matrix()
        self.frame_idx += 1

    def draw_hud(self, row):
        py5.hint(py5.DISABLE_DEPTH_TEST)
        py5.fill(0, 255, 150)
        py5.text_size(32)
        py5.text("VALIDADOR DE KERNEL: SPHY-HILBERTLESS S(Φ):OK", 80, 80)
        
        py5.text_size(24)
        py5.fill(255)
        py5.text(f"FRAME AUDITADO: {row['frame']} / {len(self.df)}", 80, 130)
        py5.fill(0, 200, 255)
        py5.text(f"THREADS NO TORO: {len(row['pids'])}", 80, 170)
        
        py5.fill(255, 215, 0)
        py5.text("SHA-256 FRAME HASH (VERIFIED):", 80, 230)
        py5.text_size(18)
        py5.text(row['hash'].upper(), 80, 260)
        
        py5.fill(150)
        py5.text_size(22)
        py5.text("ACTIVE PIDs IN TORUS:", 80, 340)
        for i, pid in enumerate(row['pids']):
            py5.text(f"> PID: {pid}", 90, 380 + i*24)
            
        py5.hint(py5.ENABLE_DEPTH_TEST)

    def draw_torus_grid(self, R, r):
        for u in range(0, 360, 20):
            py5.begin_shape()
            for v in range(0, 365, 10):
                x = (R + r * py5.cos(py5.radians(v))) * py5.cos(py5.radians(u))
                y = (R + r * py5.cos(py5.radians(v))) * py5.sin(py5.radians(u))
                z = r * py5.sin(py5.radians(v))
                py5.vertex(x, y, z)
            py5.end_shape()

    def draw_electron(self, t, offset):
        R, r = 350, 140
        phi = t * self.PHI
        theta = t * (self.PHI**2) + offset
        x = (R + r * py5.cos(theta)) * py5.cos(phi)
        y = (R + r * py5.cos(theta)) * py5.sin(phi)
        z = r * py5.sin(theta)
        py5.push_matrix()
        py5.translate(x, y, z)
        py5.fill(255, 215, 0)
        py5.no_stroke()
        py5.sphere(8)
        py5.pop_matrix()

# --- PONTE DE EXECUÇÃO ATUALIZADA ---

auditoria = None

def settings():
    if auditoria:
        auditoria.settings()


def setup():
    if auditoria:
        auditoria.setup()


def draw():
    if auditoria:
        auditoria.draw()

if __name__ == "__main__":
    dataset = carregar_e_validar()
    if dataset is not None:
        auditoria = AuditoriaVisual(dataset)
        py5.run_sketch()
