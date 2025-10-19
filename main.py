import customtkinter as ctk
import sqlite3
import os
from typing import Optional
from msx_screen2_editor import MSScreen2Editor, MSX_PALETTE, MSX_PALETTE_INV

# --- 1. Configurações e Funções do SQLite ---
# Nome do arquivo do banco de dados
DB_FILE = "msx_screen_editor.db"

def setup_database():
    """Cria a tabela de configurações se ela não existir e insere valores padrão."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Cria a tabela 'configuracoes'
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                id INTEGER PRIMARY KEY,
                tema TEXT NOT NULL,
                ultima_tela_aberta TEXT
            )
        """)

        # Verifica se já existe um registro (deve ser único, id=1)
        cursor.execute("SELECT id FROM configuracoes WHERE id = 1")
        if cursor.fetchone() is None:
            # Insere as configurações padrão
            cursor.execute("INSERT INTO configuracoes (id, tema, ultima_tela_aberta) VALUES (1, ?, ?)",
                           ("Dark", "")) # Tema padrão: Dark

        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Erro ao configurar o banco de dados: {e}")

def get_config_value(key: str) -> Optional[str]:
    """Lê um valor de configuração do banco de dados."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(f"SELECT {key} FROM configuracoes WHERE id = 1")
        result = cursor.fetchone()
        conn.close()
        return str(result[0]) if result else None
    except sqlite3.Error as e:
        print(f"Erro ao ler a configuração '{key}': {e}")
        return None

def update_config_value(key: str, value: str):
    """Atualiza um valor de configuração no banco de dados."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(f"UPDATE configuracoes SET {key} = ? WHERE id = 1", (value,))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Erro ao atualizar a configuração '{key}': {e}")


# --- 2. Classe da Janela de Configurações ---
class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Configurações")
        self.geometry("300x200")
        self.transient(master) # Mantém a janela de configurações acima da principal
        self.resizable(False, False)

        # Configura o tema atual lido do DB
        current_theme = get_config_value("tema")

        ctk.CTkLabel(self, text="Tema da Aplicação:").pack(pady=10)

        self.theme_var = ctk.StringVar(value=current_theme)
        self.theme_optionmenu = ctk.CTkOptionMenu(
            self,
            values=["Light", "Dark", "System"],
            variable=self.theme_var,
            command=self.change_theme_event
        )
        self.theme_optionmenu.pack(pady=10)

    def change_theme_event(self, new_theme: str):
        """Aplica o novo tema e o salva no banco de dados."""
        ctk.set_appearance_mode(new_theme)
        update_config_value("tema", new_theme)
        print(f"Tema alterado para: {new_theme} e salvo no DB.")


# --- 3. Classe Principal da Aplicação ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações iniciais da janela principal
        self.title("MSX Screen Editor")
        self.geometry("800x600")
        self.minsize(600, 400)

        # 3.1 Carrega a configuração do tema e aplica
        initial_theme = get_config_value("tema")
        if initial_theme:
            ctk.set_appearance_mode(initial_theme)

        # 3.2 Configurações de layout (Grid)
        self.grid_rowconfigure(1, weight=1)    # Linha 1 para o editor, expansível
        self.grid_columnconfigure(0, weight=1) # Coluna 0, expansível

        # 3.3 Frame para o conteúdo (onde o editor irá aparecer)
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # 3.4 Criação do Menu
        self.create_menu()

        # Inicia com uma tela de boas vindas ou o último modo aberto
        self.show_welcome_screen()

    def create_menu(self):
        """Cria um Frame superior para simular o menu/botões de navegação."""
        menu_frame = ctk.CTkFrame(self, height=50)
        menu_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        menu_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        # Botões dos Modos de Tela do MSX
        ctk.CTkButton(menu_frame, text="SCREEN 0 (Texto)",
                      command=self.open_editor_screen0).grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        ctk.CTkButton(menu_frame, text="SCREEN 1 (Texto/Gráfico)",
                      command=self.open_editor_screen1).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkButton(menu_frame, text="SCREEN 2 (Gráfico)",
                      command=self.open_editor_screen2).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Botão de Configurações
        ctk.CTkButton(menu_frame, text="Configurações",
                      command=self.open_settings).grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # Botão Sair
        ctk.CTkButton(menu_frame, text="Sair", fg_color="red", hover_color="#8b0000",
                      command=self.quit).grid(row=0, column=4, padx=5, pady=5, sticky="ew")


    # --- 4. Funções de Navegação e Configurações ---

    def clear_content_frame(self):
        """Remove todos os widgets do frame de conteúdo."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_welcome_screen(self):
        self.clear_content_frame()
        ctk.CTkLabel(self.content_frame,
                     text="Bem-vindo ao MSX Screen Editor!\nSelecione um modo de tela no menu acima.",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(expand=True)

    def open_settings(self):
        """Abre a janela de configurações."""
        if not hasattr(self, "settings_window") or self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self)
        self.settings_window.focus() # Traz a janela para a frente

    # --- 5. Esqueletos das Funções do Editor ---

    def open_editor_screen0(self):
        self.clear_content_frame()
        ctk.CTkLabel(self.content_frame, text="EDITOR SCREEN 0\n(Modo Texto 40x24)").pack(pady=20)
        # TODO: Sua lógica para o editor SCREEN 0 (Texto com 40 colunas e 24 linhas)
        # Você precisará de:
        # - Um widget de texto ou células para simular o grid 40x24.
        # - Lógica para seleção de cores de foreground/background.
        # - Lógica para salvar os dados no formato MSX.

    def open_editor_screen1(self):
        self.clear_content_frame()
        ctk.CTkLabel(self.content_frame, text="EDITOR SCREEN 1\n(Modo Gráfico com 32x24 blocos de 8x8)").pack(pady=20)
        # TODO: Sua lógica para o editor SCREEN 1
        # Este modo tem 32 colunas de 8x8 e 24 linhas de 8x8.
        # Você trabalhará com Pattern Table (Caracteres) e Color Table.

    def open_editor_screen2(self):
        self.clear_content_frame()
        self.screen2_editor = MSScreen2Editor(self.content_frame, app_instance=self)
        self.screen2_editor.pack(expand=True, fill="both")

        # Exemplo de um botão para salvar que você pode adicionar
        # Salvar/Carregar pode ser adicionado à toolbar_frame do editor,
        # ou como um menu na janela principal se você tiver um Tkinter Menubar.
        # Aqui, para exemplo, vou adicionar um botão simples abaixo do editor.
        save_button = ctk.CTkButton(self.content_frame, text="Salvar Imagem (BMP)",
                                    command=lambda: self.screen2_editor.save_screen_data("myscreen2"))
        save_button.pack(pady=5)

        ctk.CTkLabel(self.content_frame, text="EDITOR SCREEN 2\n(Modo Gráfico 256x192, ampliado 4x)").pack(pady=5)
        # Este modo é o mais detalhado. Você precisará de uma tela de desenho (canvas)
        # e lógica para gerenciar as cores de 16 tons por linha de 8 pixels.


# --- 6. Execução Principal ---
if __name__ == "__main__":
    # 1. Configura o banco de dados antes de iniciar a aplicação
    setup_database()

    # 2. Configura o CustomTkinter
    ctk.set_default_color_theme("blue") # Define a cor padrão dos widgets

    # 3. Inicia a aplicação
    app = App()
    app.mainloop()