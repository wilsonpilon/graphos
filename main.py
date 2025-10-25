import customtkinter as ctk
import sqlite3
import os
from typing import Optional
from PIL import Image, ImageTk

# --- IMPORTAÇÃO DO MÓDULO SCREEN 2 ---
try:
    from msx_screen2_editor import MSScreen2Editor
except ImportError:
    print("AVISO: Não foi possível importar 'msx_screen2_editor.py'. A opção 'edita tela' não funcionará como editor.")


    class MSScreen2Editor:
        def __init__(self, master, app_instance=None):
            ctk.CTkLabel(master, text="ERRO: Módulo SCREEN 2 não encontrado!", fg_color="red").pack(pady=20)

        def pack(self, **kwargs):
            pass

        # --- Constantes de Estilo e Configuração ---
DB_FILE = "msx_screen_editor.db"
SPLASH_IMAGE_PATH = "newgraphos.jpg"
SPLASH_DURATION_MS = 4000
TITLE_TEXT = "Graphos III"

# Cores Personalizadas (Hex) - Paleta de Acrílico/Glassmorphism
# Usando cores claras (quase brancas) com transparência simulada (alpha)
# NOTA: O CustomTkinter não suporta transparência real alfa,
# mas simulamos o efeito com tons muito claros e bordas/sombras suaves.

FUNDO_APLICACAO = "#F5F5F5"  # Cinza Claro (Fundo do sistema)
COR_VIDRO_NEUTRO = "#E0E0E0"  # Tom neutro e claro para o vidro (simulado)

# Cores VIBRANTES (Para destaques e efeito acrílico colorido)
FUNDO_TITULO = "#00BFA5"  # Teal/Cyan Moderno (Simulando vidro ciano claro)
FUNDO_MENU = "#FFD54F"  # Amarelo Pastel/Material (Simulando vidro amarelo claro)
FUNDO_SUB_OPCOES = "#BDBDBD"  # Cinza de fundo para sub-opções (para contraste)
FUNDO_STATUS = "#8BC34A"  # Verde Limão Suave (Simulando vidro verde)

# Cores para Borda, Texto e Interação
COR_BORDAS = "#B0BEC5"  # Cinza suave e claro para bordas (Efeito vidro)
COR_TEXTO_MENU = "#263238"  # Azul escuro/Preto (Alta Legibilidade)
COR_TEXTO_PADRAO = "#263238"  # Azul escuro/Preto

# Hover do menu: um tom levemente mais escuro/saturado
HOVER_MENU = "#FFA000"  # Laranja/Amarelo mais forte (para destacar)
COR_SAIR = "#E53935"  # Vermelho Alaranjado (Moderno)
HOVER_SAIR = "#FFCDD2"  # Rosa Claro (Simulação de clique/vidro pressionado)


# Funções do SQLite (Mantidas)
# ... (setup_database, get_config_value, update_config_value - Mantenha o código destas funções) ...
def setup_database():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS configuracoes
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY,
                           tema
                           TEXT
                           NOT
                           NULL,
                           ultima_tela_aberta
                           TEXT
                       )
                       """)
        cursor.execute("SELECT id FROM configuracoes WHERE id = 1")
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO configuracoes (id, tema, ultima_tela_aberta) VALUES (1, ?, ?)",
                           ("Dark", ""))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Erro ao configurar o banco de dados: {e}")


def get_config_value(key: str) -> Optional[str]:
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(f"SELECT {key} FROM configuracoes WHERE id = 1")
        result = cursor.fetchone()
        conn.close()
        return str(result[0]) if result else "Dark"
    except sqlite3.Error as e:
        return "Dark"


def update_config_value(key: str, value: str):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(f"UPDATE configuracoes SET {key} = ? WHERE id = 1", (value,))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Erro ao atualizar a configuração '{key}': {e}")


# --- Configurações de Menu ---

MAIN_MENU_OPTIONS = {
    "display tela": "display_tela",
    "edita tela": "open_editor_screen2",
    "arquiva tela": "arquiva_tela",
    "recupera tela": "recupera_tela",
    "edita alfabeto": "edita_alfabeto",
    "arquiva alfabeto": "arquiva_alfabeto",
    "recupera alfabeto": "recupera_alfabeto",
    "cria shapes": "cria_shapes",
    "arquiva shapes": "arquiva_shapes",
    "recupera shapes": "recupera_shapes",
    "mostra diretório": "mostra_diretorio",
    "versão do sistema": "versao_sistema",
    "encerrar": "quit",
}


# --- Classe Principal da Aplicação (O Editor) ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.current_editor = None
        self.init_app()

    def init_app(self):
        self.title("MSX Graphos III Editor")
        self.geometry("1200x800")
        self.minsize(800, 600)
        self.deiconify()
        self.configure(fg_color=FUNDO_APLICACAO)

        initial_theme = get_config_value("tema")
        if initial_theme:
            ctk.set_appearance_mode(initial_theme)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.create_title_bar()
        self.create_vertical_menu(MAIN_MENU_OPTIONS)
        self.create_content_areas()
        self.create_status_bar()

        self.log_status("Bem-vindo ao Graphos III. Selecione uma opção no menu.")

    def create_title_bar(self):
        """Cria a barra de título superior (Acrílico Cyan/Teal)."""
        title_frame = ctk.CTkFrame(self, fg_color=FUNDO_TITULO, height=40,
                                   border_width=2, border_color=COR_BORDAS, corner_radius=0)
        title_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        title_frame.grid_rowconfigure(0, weight=1)
        title_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(title_frame, text=TITLE_TEXT,
                     text_color="white",  # Texto branco para excelente legibilidade no fundo colorido
                     font=ctk.CTkFont(family="Arial", size=24, weight="bold")).grid(row=0, column=0, sticky="nsew")

    def create_vertical_menu(self, menu_config):
        """Cria o menu vertical (Acrílico Amarelo/Pastel)."""

        if hasattr(self, 'menu_frame') and self.menu_frame.winfo_exists():
            self.menu_frame.destroy()

        self.menu_frame = ctk.CTkFrame(self, fg_color=FUNDO_MENU, width=180,
                                       border_width=2, border_color=COR_BORDAS, corner_radius=10)  # Cantos arredondados
        self.menu_frame.grid(row=1, column=0, sticky="nswe", padx=(10, 5), pady=(10, 5))
        self.menu_frame.grid_propagate(False)
        self.menu_frame.grid_columnconfigure(0, weight=1)

        for idx, (text, method_name) in enumerate(menu_config.items()):

            command_method = getattr(self, method_name,
                                     lambda t=text: self.log_status(f"Comando '{t}' não implementado."))

            button = ctk.CTkButton(self.menu_frame,
                                   text=text.upper(),
                                   command=command_method,
                                   fg_color=COR_VIDRO_NEUTRO,  # Fundo do botão claro (Efeito vidro)
                                   text_color=COR_TEXTO_MENU,  # Texto escuro (Alta Legibilidade)
                                   hover_color=HOVER_MENU,
                                   corner_radius=8,  # Cantos arredondados nos botões
                                   height=38,
                                   font=ctk.CTkFont(family="Arial", size=14, weight="bold"))
            button.grid(row=idx, column=0, sticky="ew", padx=8, pady=4)

            if method_name == "quit":
                button.configure(fg_color=COR_SAIR, hover_color=HOVER_SAIR, text_color="white")

    def create_content_areas(self):
        """Cria as áreas de Sub-Opções e Conteúdo/Editor."""
        content_wrapper = ctk.CTkFrame(self, fg_color=FUNDO_APLICACAO)
        content_wrapper.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(10, 5))
        content_wrapper.grid_rowconfigure(0, weight=1)
        content_wrapper.grid_columnconfigure(1, weight=1)

        # 1. Sub-Opções (Painel de Acrílico Neutro)
        self.sub_options_frame = ctk.CTkFrame(content_wrapper, fg_color=COR_VIDRO_NEUTRO, width=150,
                                              border_width=2, border_color=COR_BORDAS, corner_radius=10)
        self.sub_options_frame.grid(row=0, column=0, sticky="nswe", padx=(0, 10), pady=0)
        self.sub_options_frame.grid_propagate(False)
        ctk.CTkLabel(self.sub_options_frame, text="SUB-OPÇÕES", text_color=COR_TEXTO_PADRAO,
                     font=ctk.CTkFont(family="Arial", weight="bold")).pack(pady=10)

        # 2. Área Principal de Conteúdo/Editor
        self.main_content_frame = ctk.CTkFrame(content_wrapper, fg_color=COR_VIDRO_NEUTRO,
                                               border_width=2, border_color=COR_BORDAS, corner_radius=10)
        self.main_content_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 0), pady=0)
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)

        self.show_welcome_screen()

    # Substitua esta função:
    def create_status_bar(self):
        """Cria a área de status/entrada de comandos (Linha 2, Fundo Verde modernizado)."""
        status_frame = ctk.CTkFrame(self, fg_color=FUNDO_STATUS, height=70,
                                    border_width=2, border_color=COR_BORDAS, corner_radius=10)
        status_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        status_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(status_frame, text="STATUS/CMD:", text_color="white",
                     font=ctk.CTkFont(family="Arial", weight="bold")).grid(row=0, column=0, padx=10, pady=(5, 2),
                                                                           sticky="w")

        # SOLUÇÃO 1: Atribua o widget primeiro, posicione em seguida.
        self.status_label = ctk.CTkLabel(status_frame, text="", text_color="white", anchor="w",
                                         font=ctk.CTkFont(family="Arial"))
        self.status_label.grid(row=0, column=1, padx=10, pady=(5, 2), sticky="ew")  # <--- APENAS POSICIONAMENTO

        # Campo de entrada
        self.command_entry = ctk.CTkEntry(status_frame, placeholder_text="Entre com comandos aqui...",
                                          text_color=COR_TEXTO_PADRAO,
                                          fg_color=FUNDO_APLICACAO,
                                          border_color=COR_BORDAS,
                                          border_width=1,
                                          corner_radius=5,
                                          font=ctk.CTkFont(family="Arial"))
        self.command_entry.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="ew")

    # Substitua esta função (simplificação):
    def log_status(self, message: str):
        """Atualiza a mensagem diretamente no widget self.status_label."""
        # SOLUÇÃO 2: Use a referência direta para configurar o texto.
        if hasattr(self, 'status_label') and self.status_label is not None:
            self.status_label.configure(text=message)
        else:
            # Fallback caso a barra de status ainda não tenha sido criada
            print(f"[STATUS] {message}")
        print(f"[STATUS] {message}")

    def clear_content_area(self):
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()
        for widget in self.sub_options_frame.winfo_children():
            if widget.winfo_class() != "CTkLabel":
                widget.destroy()

    def show_welcome_screen(self):
        self.clear_content_area()
        ctk.CTkLabel(self.main_content_frame,
                     text="Editor Gráfico MSX Graphos III\n\nSelecione uma opção no menu lateral.",
                     font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
                     text_color=COR_TEXTO_PADRAO).pack(expand=True)

    # --- Funções de Transição/Menu (Mantidas) ---

    def open_editor_screen2(self):
        self.clear_content_area()
        self.log_status("Modo: Edição de Tela (SCREEN 2, 256x192)")
        self.current_editor = MSScreen2Editor(self.main_content_frame, app_instance=self)
        self.current_editor.pack(expand=True, fill="both")
        self._load_editor_sub_options()

    def _load_editor_sub_options(self):
        for widget in [w for w in self.sub_options_frame.winfo_children() if w.winfo_class() != "CTkLabel"]:
            widget.destroy()

        # Botões com estilo moderno e cantos arredondados
        ctk.CTkButton(self.sub_options_frame, text="EXPORTAR VRAM",
                      command=lambda: self.log_status("Função: Exportar dados VRAM"),
                      fg_color=FUNDO_TITULO, text_color="white", hover_color="#008C9E", corner_radius=8).pack(pady=5,
                                                                                                              padx=8,
                                                                                                              fill="x")
        ctk.CTkButton(self.sub_options_frame, text="MUDAR PALETA",
                      command=lambda: self.log_status("Função: Abrir Paleta de Cores"),
                      fg_color=FUNDO_TITULO, text_color="white", hover_color="#008C9E", corner_radius=8).pack(pady=5,
                                                                                                              padx=8,
                                                                                                              fill="x")

    def display_tela(self):
        self.clear_content_area()
        self.log_status("Modo: Display Tela (Visualização)")
        ctk.CTkLabel(self.main_content_frame, text="VISUALIZADOR DE TELA AQUI", text_color=COR_TEXTO_PADRAO,
                     font=ctk.CTkFont(family="Arial", size=20)).pack(pady=50)

    # --- Placeholder para as demais funções (Mantidas) ---
    def arquiva_tela(self):
        self.clear_content_area()
        self.log_status("Modo: Arquiva Tela")
        ctk.CTkLabel(self.main_content_frame, text="Função de Salvar/Exportar Tela (binário MSX)",
                     text_color=COR_TEXTO_PADRAO,
                     font=ctk.CTkFont(family="Arial", size=20)).pack(pady=50)

    def recupera_tela(self):
        self.clear_content_area()
        self.log_status("Modo: Recupera Tela")
        ctk.CTkLabel(self.main_content_frame, text="Função de Carregar Tela (binário MSX)", text_color=COR_TEXTO_PADRAO,
                     font=ctk.CTkFont(family="Arial", size=20)).pack(pady=50)

    def edita_alfabeto(self):
        self.clear_content_area()
        self.log_status("Modo: Edita Alfabeto (Pattern/Char Table)")
        ctk.CTkLabel(self.main_content_frame, text="EDITOR DE CARACTERES 8x8 AQUI", text_color=COR_TEXTO_PADRAO,
                     font=ctk.CTkFont(family="Arial", size=20)).pack(pady=50)

    def arquiva_alfabeto(self):
        self.clear_content_area()
        self.log_status("Modo: Arquiva Alfabeto")
        ctk.CTkLabel(self.main_content_frame, text="Função de salvar Pattern Table", text_color=COR_TEXTO_PADRAO,
                     font=ctk.CTkFont(family="Arial", size=20)).pack(pady=50)

    def recupera_alfabeto(self):
        self.clear_content_area()
        self.log_status("Modo: Recupera Alfabeto")
        ctk.CTkLabel(self.main_content_frame, text="Função de carregar Pattern Table", text_color=COR_TEXTO_PADRAO,
                     font=ctk.CTkFont(family="Arial", size=20)).pack(pady=50)

    def cria_shapes(self):
        self.clear_content_area()
        self.log_status("Modo: Cria Shapes (Sprites/Blocos)")
        ctk.CTkLabel(self.main_content_frame, text="EDITOR DE SPRITES 16x16 ou 8x8 AQUI", text_color=COR_TEXTO_PADRAO,
                     font=ctk.CTkFont(family="Arial", size=20)).pack(pady=50)

    def arquiva_shapes(self):
        self.clear_content_area()
        self.log_status("Modo: Arquiva Shapes")
        ctk.CTkLabel(self.main_content_frame, text="Função de salvar Sprite/Shape data", text_color=COR_TEXTO_PADRAO,
                     font=ctk.CTkFont(family="Arial", size=20)).pack(pady=50)

    def recupera_shapes(self):
        self.clear_content_area()
        self.log_status("Modo: Recupera Shapes")
        ctk.CTkLabel(self.main_content_frame, text="Função de carregar Sprite/Shape data", text_color=COR_TEXTO_PADRAO,
                     font=ctk.CTkFont(family="Arial", size=20)).pack(pady=50)

    def mostra_diretorio(self):
        self.clear_content_area()
        self.log_status("Modo: Mostra Diretório")
        ctk.CTkLabel(self.main_content_frame, text=f"Conteúdo do diretório atual:\n{os.getcwd()}",
                     text_color=COR_TEXTO_PADRAO,
                     font=ctk.CTkFont(family="Arial", size=20)).pack(pady=50)

    def versao_sistema(self):
        self.clear_content_area()
        self.log_status("Modo: Versão do Sistema")
        ctk.CTkLabel(self.main_content_frame,
                     text=f"{TITLE_TEXT} v1.0\nCompilado em {os.getenv('COMPUTERNAME', 'Python/CustomTkinter')}",
                     text_color=COR_TEXTO_PADRAO,
                     font=ctk.CTkFont(family="Arial", size=20)).pack(pady=50)

    def quit(self):
        self.log_status("Encerrando aplicação...")
        super().quit()


# --- Classe da Splash Screen (Mantida) ---
class SplashScreen(ctk.CTk):
    def __init__(self, app_to_run):
        super().__init__()
        self.app_to_run = app_to_run

        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.resizable(False, False)
        ctk.set_appearance_mode("Dark")

        self.img_tk = self.load_splash_image()

        if self.img_tk:
            img_width = self.img_tk.width()
            img_height = self.img_tk.height()

            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x = (screen_width // 2) - (img_width // 2)
            y = (screen_height // 2) - (img_height // 2)
            self.geometry(f"{img_width}x{img_height}+{x}+{y}")

            label = ctk.CTkLabel(self, image=self.img_tk, text="")
            label.pack(expand=True, fill="both")

            self.after(SPLASH_DURATION_MS, self.start_main_app)
        else:
            self.start_main_app()

    def load_splash_image(self):
        if not os.path.exists(SPLASH_IMAGE_PATH):
            return None

        try:
            img = Image.open(SPLASH_IMAGE_PATH)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            return None

    def start_main_app(self):
        self.destroy()
        main_app = self.app_to_run()
        main_app.mainloop()


# --- Execução Principal (Mantida) ---
if __name__ == "__main__":
    setup_database()
    splash = SplashScreen(App)
    splash.mainloop()