import customtkinter as ctk
import tkinter as tk
from tkinter import colorchooser
from collections import defaultdict
from math import sqrt, floor

# --- Paleta de Cores do MSX (HEX RGB) ---
MSX_PALETTE = {
    0: "#000000",  # Preto
    1: "#000000",  # Preto Transparente (geralmente tratado como 0 no VRAM, mas aqui usaremos como preto sólido)
    2: "#21C842",  # Verde Médio
    3: "#5EDC78",  # Verde Claro
    4: "#5454ED",  # Azul Escuro
    5: "#7D76FC",  # Azul Claro
    6: "#C75454",  # Vermelho Escuro
    7: "#42E8EC",  # Ciano
    8: "#ED6A54",  # Vermelho Médio
    9: "#FF8C8C",  # Vermelho Claro
    10: "#C3C3C3", # Cinza Escuro
    11: "#FFFFFF", # Branco
    12: "#9C68CC", # Magenta
    13: "#CC9C9C", # Salmão
    14: "#3ADC3A", # Verde Lima
    15: "#CCCC3A", # Amarelo
}

# Inverso para buscar o índice da cor a partir do HEX
MSX_PALETTE_INV = {v: k for k, v in MSX_PALETTE.items()}

# --- Constantes do Editor ---
MSX_WIDTH = 256
MSX_HEIGHT = 192
PIXEL_SCALE = 4  # Cada pixel MSX será um bloco de PIXEL_SCALE x PIXEL_SCALE no canvas

CANVAS_WIDTH = MSX_WIDTH * PIXEL_SCALE
CANVAS_HEIGHT = MSX_HEIGHT * PIXEL_SCALE

class MSScreen2Editor(ctk.CTkFrame):
    def __init__(self, master, app_instance=None):
        super().__init__(master)
        self.app_instance = app_instance # Para acesso a funções da app principal, se necessário

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Variáveis de Estado do Editor ---
        self.current_tool = "pencil" # Ferramenta atual (pencil, line, rect, fill, etc.)
        self.primary_color_index = 11 # Cor primária padrão: Branco
        self.secondary_color_index = 0  # Cor secundária padrão: Preto
        self.current_drawing_color = self.primary_color_index # Cor que está sendo usada para desenhar

        # Armazenar os pixels da tela MSX real
        # self.pixels[y][x] = cor_index
        self.pixels = [[self.secondary_color_index for _ in range(MSX_WIDTH)] for _ in range(MSX_HEIGHT)]

        # --- Painel de Ferramentas (Coluna 0) ---
        self.toolbar_frame = ctk.CTkFrame(self, width=150)
        self.toolbar_frame.grid(row=0, column=0, sticky="nswe", padx=(5, 2), pady=5)
        self.toolbar_frame.grid_propagate(False) # Impede que o frame se redimensione para caber o conteúdo
        self.toolbar_frame.grid_columnconfigure(0, weight=1)

        # --- Ferramentas ---
        ctk.CTkLabel(self.toolbar_frame, text="Ferramentas", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        self.tool_buttons = {}
        tools = [
            ("Lápis (Livre)", "pencil", self.set_tool),
            ("Linha", "line", self.set_tool),
            ("Retângulo Vazio", "rect_empty", self.set_tool),
            ("Retângulo Cheio", "rect_fill", self.set_tool),
            ("Círculo Vazio", "circle_empty", self.set_tool),
            ("Círculo Cheio", "circle_fill", self.set_tool),
            ("Preenchimento", "fill_area", self.set_tool),
            # Adicione mais ferramentas aqui conforme necessário
        ]
        for text, tool_name, command in tools:
            btn = ctk.CTkButton(self.toolbar_frame, text=text, command=lambda t=tool_name: command(t))
            btn.pack(pady=2, padx=5, fill="x")
            self.tool_buttons[tool_name] = btn

        # --- Paleta de Cores ---
        ctk.CTkLabel(self.toolbar_frame, text="Paleta MSX", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        self.color_buttons_frame = ctk.CTkFrame(self.toolbar_frame)
        self.color_buttons_frame.pack(pady=5, padx=5)
        self.color_buttons_frame.grid_columnconfigure((0,1,2,3), weight=1)

        self.color_palette_widgets = {}
        row, col = 0, 0
        for i in range(16):
            color_hex = MSX_PALETTE[i]
            btn = ctk.CTkButton(self.color_buttons_frame, text="",
                                fg_color=color_hex, hover_color=color_hex,
                                width=25, height=25,
                                command=lambda c=i: self.set_drawing_color(c))
            btn.grid(row=row, column=col, padx=1, pady=1)
            self.color_palette_widgets[i] = btn
            col += 1
            if col > 3:
                col = 0
                row += 1

        # Mostrador de Cores Selecionadas
        self.selected_colors_frame = ctk.CTkFrame(self.toolbar_frame)
        self.selected_colors_frame.pack(pady=(10, 5), padx=5, fill="x")
        self.selected_colors_frame.grid_columnconfigure((0,1), weight=1)

        ctk.CTkLabel(self.selected_colors_frame, text="Principal:").grid(row=0, column=0, sticky="w")
        self.primary_color_display = ctk.CTkFrame(self.selected_colors_frame, width=30, height=30, fg_color=MSX_PALETTE[self.primary_color_index])
        self.primary_color_display.grid(row=0, column=1, padx=5, pady=2, sticky="e")

        ctk.CTkLabel(self.selected_colors_frame, text="Secundária:").grid(row=1, column=0, sticky="w")
        self.secondary_color_display = ctk.CTkFrame(self.selected_colors_frame, width=30, height=30, fg_color=MSX_PALETTE[self.secondary_color_index])
        self.secondary_color_display.grid(row=1, column=1, padx=5, pady=2, sticky="e")

        # --- Canvas de Desenho (Coluna 1) ---
        self.canvas_frame = ctk.CTkFrame(self)
        self.canvas_frame.grid(row=0, column=1, sticky="nswe", padx=(2, 5), pady=5)
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.canvas_frame,
                                width=CANVAS_WIDTH,
                                height=CANVAS_HEIGHT,
                                bg=MSX_PALETTE[self.secondary_color_index],
                                highlightthickness=0) # Remove a borda padrão do canvas
        self.canvas.pack(expand=True, fill="both")

        # --- Eventos do Mouse ---
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Button-3>", self.on_right_click) # Botão direito para cor secundária

        # Variáveis para desenho
        self.last_x, self.last_y = None, None
        self.start_x, self.start_y = None, None # Para ferramentas de arrasto (linha, retângulo, etc.)

        # Inicializa a tela com a cor secundária
        self.draw_all_pixels()
        self.update_color_displays()


    def set_drawing_color(self, color_index: int):
        """Define a cor de desenho principal e atualiza o display."""
        if color_index in MSX_PALETTE:
            self.primary_color_index = color_index
            self.current_drawing_color = self.primary_color_index
            self.update_color_displays()
        else:
            print(f"Cor {color_index} inválida para a paleta MSX.")

    def set_tool(self, tool_name: str):
        """Define a ferramenta atual e atualiza o estado visual."""
        self.current_tool = tool_name
        print(f"Ferramenta selecionada: {tool_name}")
        # Opcional: Adicionar feedback visual ao botão da ferramenta selecionada
        for btn_name, btn_widget in self.tool_buttons.items():
            if btn_name == tool_name:
                btn_widget.configure(border_color=MSX_PALETTE[11], border_width=2) # Destaca com borda branca
            else:
                btn_widget.configure(border_width=0)


    def update_color_displays(self):
        """Atualiza os quadrados de exibição de cor."""
        self.primary_color_display.configure(fg_color=MSX_PALETTE[self.primary_color_index])
        self.secondary_color_display.configure(fg_color=MSX_PALETTE[self.secondary_color_index])


    def get_msx_pixel_coords(self, event_x, event_y):
        """Converte as coordenadas do canvas para coordenadas de pixel MSX."""
        msx_x = floor(event_x / PIXEL_SCALE)
        msx_y = floor(event_y / PIXEL_SCALE)
        return msx_x, msx_y

    def draw_pixel_on_canvas(self, msx_x: int, msx_y: int, color_index: int):
        """Desenha um único pixel MSX no canvas ampliado."""
        if 0 <= msx_x < MSX_WIDTH and 0 <= msx_y < MSX_HEIGHT:
            x1 = msx_x * PIXEL_SCALE
            y1 = msx_y * PIXEL_SCALE
            x2 = x1 + PIXEL_SCALE
            y2 = y1 + PIXEL_SCALE
            self.canvas.create_rectangle(x1, y1, x2, y2,
                                         fill=MSX_PALETTE[color_index],
                                         outline="", # Sem borda para os pixels
                                         tags=f"pixel_{msx_x}_{msx_y}") # Tag para fácil atualização
            # Atualiza o array de pixels
            self.pixels[msx_y][msx_x] = color_index

    def draw_all_pixels(self):
        """Redesenha todos os pixels do array de pixels no canvas."""
        self.canvas.delete("all") # Limpa o canvas antes de redesenhar
        for y in range(MSX_HEIGHT):
            for x in range(MSX_WIDTH):
                self.draw_pixel_on_canvas(x, y, self.pixels[y][x])


    # --- Lógica de Restrição de Cores do MSX SCREEN 2 ---
    def apply_msx_color_constraint(self, msx_y: int, msx_x_start: int, msx_x_end: int):
        """
        Aplica a restrição de duas cores para cada bloco horizontal de 8 pixels no MSX SCREEN 2.
        Todos os pixels em uma linha de 8 pixels (x // 8) * 8 a ((x // 8) * 8) + 7
        só podem usar duas cores. Se mais de duas forem usadas, as extras são substituídas.
        Esta é uma simplificação. Em um editor real, você precisaria de uma interface
        para o usuário escolher as duas cores por bloco de 8.
        Por simplicidade, aqui vamos:
        1. Identificar as duas cores mais usadas no bloco.
        2. Substituir as outras por uma das duas predominantes.
        """
        if not (0 <= msx_y < MSX_HEIGHT):
            return

        # Itera sobre os blocos de 8 pixels afetados
        block_start = (msx_x_start // 8) * 8
        block_end = ((msx_x_end // 8) * 8) + 8 # Garante que o último bloco também seja processado
        if block_end > MSX_WIDTH: block_end = MSX_WIDTH

        for x_block_start in range(block_start, block_end, 8):
            x_block_end = min(x_block_start + 8, MSX_WIDTH)

            # Coleta as cores usadas neste bloco
            colors_in_block = defaultdict(int)
            for x in range(x_block_start, x_block_end):
                colors_in_block[self.pixels[msx_y][x]] += 1

            # Seleciona as duas cores mais frequentes
            sorted_colors = sorted(colors_in_block.items(), key=lambda item: item[1], reverse=True)
            
            if len(sorted_colors) > 2:
                # Pegamos as 2 cores mais frequentes. Se houver um empate grande, a ordem pode importar.
                color1_idx = sorted_colors[0][0]
                color2_idx = sorted_colors[1][0] if len(sorted_colors) > 1 else color1_idx # Se só 1 cor, a segunda é a mesma

                # Substitui quaisquer outras cores por uma das duas predominantes
                for x in range(x_block_start, x_block_end):
                    current_pixel_color = self.pixels[msx_y][x]
                    if current_pixel_color != color1_idx and current_pixel_color != color2_idx:
                        # Simplificação: Substitui pela cor principal selecionada para desenho
                        # Ou você pode escolher a mais próxima no MSX PALETTE, ou a mais frequente
                        self.pixels[msx_y][x] = self.current_drawing_color # Ou color1_idx
                        self.draw_pixel_on_canvas(x, msx_y, self.pixels[msx_y][x]) # Redesenha

            # Se houver 1 ou 2 cores, está OK, não faz nada.

    # --- Funções de Manipulação do Canvas / Eventos do Mouse ---

    def on_mouse_down(self, event):
        self.start_x, self.start_y = self.get_msx_pixel_coords(event.x, event.y)
        self.last_x, self.last_y = self.start_x, self.start_y
        self.current_drawing_color = self.primary_color_index # Usar cor primária no clique esquerdo

        if self.current_tool == "pencil":
            self.draw_pencil_pixel(self.start_x, self.start_y)
        elif self.current_tool in ["line", "rect_empty", "rect_fill", "circle_empty", "circle_fill"]:
            # Para ferramentas de arrasto, apenas guarda o ponto inicial
            pass

    def on_mouse_drag(self, event):
        msx_x, msx_y = self.get_msx_pixel_coords(event.x, event.y)

        if self.last_x is None or self.last_y is None: # Primeira arrastada
            self.last_x, self.last_y = msx_x, msx_y
            return

        if msx_x == self.last_x and msx_y == self.last_y: # Não moveu para outro pixel MSX
            return

        if self.current_tool == "pencil":
            self.draw_line_pixels(self.last_x, self.last_y, msx_x, msx_y) # Simula um "lápis" conectando pontos
            self.last_x, self.last_y = msx_x, msx_y
        elif self.current_tool in ["line", "rect_empty", "rect_fill", "circle_empty", "circle_fill"]:
            # Limpa o preview anterior e desenha um novo preview
            self.canvas.delete("preview_shape")
            if self.current_tool == "line":
                self._preview_line(self.start_x, self.start_y, msx_x, msx_y)
            elif self.current_tool == "rect_empty":
                self._preview_rectangle(self.start_x, self.start_y, msx_x, msx_y, fill=False)
            elif self.current_tool == "rect_fill":
                self._preview_rectangle(self.start_x, self.start_y, msx_x, msx_y, fill=True)
            elif self.current_tool == "circle_empty":
                self._preview_circle(self.start_x, self.start_y, msx_x, msx_y, fill=False)
            elif self.current_tool == "circle_fill":
                self._preview_circle(self.start_x, self.start_y, msx_x, msx_y, fill=True)


    def on_mouse_up(self, event):
        end_x, end_y = self.get_msx_pixel_coords(event.x, event.y)

        # Para ferramentas de arrasto, aplica a forma final
        if self.current_tool == "line":
            self.canvas.delete("preview_shape")
            self.draw_line_pixels(self.start_x, self.start_y, end_x, end_y)
        elif self.current_tool == "rect_empty":
            self.canvas.delete("preview_shape")
            self.draw_rectangle_pixels(self.start_x, self.start_y, end_x, end_y, fill=False)
        elif self.current_tool == "rect_fill":
            self.canvas.delete("preview_shape")
            self.draw_rectangle_pixels(self.start_x, self.start_y, end_x, end_y, fill=True)
        elif self.current_tool == "circle_empty":
            self.canvas.delete("preview_shape")
            self.draw_circle_pixels(self.start_x, self.start_y, end_x, end_y, fill=False)
        elif self.current_tool == "circle_fill":
            self.canvas.delete("preview_shape")
            self.draw_circle_pixels(self.start_x, self.start_y, end_x, end_y, fill=True)
        elif self.current_tool == "fill_area":
            self.fill_area(self.start_x, self.start_y, self.current_drawing_color)

        # Reseta as coordenadas de arrasto
        self.last_x, self.last_y = None, None
        self.start_x, self.start_y = None, None

    def on_right_click(self, event):
        """Define a cor de desenho como a cor secundária ao clicar com o botão direito."""
        self.current_drawing_color = self.secondary_color_index
        msx_x, msx_y = self.get_msx_pixel_coords(event.x, event.y)
        if self.current_tool == "pencil":
            self.draw_pencil_pixel(msx_x, msx_y)
        elif self.current_tool == "fill_area":
            self.fill_area(msx_x, msx_y, self.current_drawing_color)
        # Para ferramentas de arrasto, se quiser que o botão direito também funcione,
        # você precisaria adaptar a lógica de on_mouse_down e on_mouse_up para considerar o botão.


    # --- Implementação das Ferramentas de Desenho ---

    def draw_pencil_pixel(self, msx_x: int, msx_y: int):
        """Desenha um único pixel MSX na posição."""
        if 0 <= msx_x < MSX_WIDTH and 0 <= msx_y < MSX_HEIGHT:
            self.pixels[msx_y][msx_x] = self.current_drawing_color
            self.draw_pixel_on_canvas(msx_x, msx_y, self.current_drawing_color)
            self.apply_msx_color_constraint(msx_y, msx_x, msx_x) # Aplica a restrição de cor


    def draw_line_pixels(self, x0: int, y0: int, x1: int, y1: int):
        """Implementação do algoritmo de linha de Bresenham."""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        pixels_to_update = set()

        while True:
            self.draw_pencil_pixel(x0, y0)
            pixels_to_update.add((y0, x0)) # Guarda para aplicar restrição

            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

        # Aplica a restrição de cor para todas as linhas afetadas
        for y, x in pixels_to_update:
            self.apply_msx_color_constraint(y, x, x)

    def _preview_line(self, x0, y0, x1, y1):
        """Desenha uma linha de preview no canvas."""
        x0_c, y0_c = x0 * PIXEL_SCALE, y0 * PIXEL_SCALE
        x1_c, y1_c = x1 * PIXEL_SCALE, y1 * PIXEL_SCALE
        self.canvas.create_line(x0_c, y0_c, x1_c, y1_c,
                                fill=MSX_PALETTE[self.current_drawing_color],
                                width=PIXEL_SCALE,
                                tags="preview_shape")

    def draw_rectangle_pixels(self, x0: int, y0: int, x1: int, y1: int, fill: bool):
        """Desenha um retângulo (cheio ou vazio)."""
        x_min, x_max = min(x0, x1), max(x0, x1)
        y_min, y_max = min(y0, y1), max(y0, y1)

        pixels_to_update_y = set()

        for y in range(y_min, y_max + 1):
            pixels_to_update_y.add(y)
            for x in range(x_min, x_max + 1):
                if fill or (y == y_min or y == y_max or x == x_min or x == x_max):
                    self.draw_pencil_pixel(x, y) # Reusa a função que já aplica a restrição

        # Aplica restrição para todas as linhas afetadas
        for y in pixels_to_update_y:
            self.apply_msx_color_constraint(y, x_min, x_max)


    def _preview_rectangle(self, x0, y0, x1, y1, fill: bool):
        """Desenha um retângulo de preview no canvas."""
        x0_c, y0_c = x0 * PIXEL_SCALE, y0 * PIXEL_SCALE
        x1_c, y1_c = x1 * PIXEL_SCALE + PIXEL_SCALE, y1 * PIXEL_SCALE + PIXEL_SCALE # Adiciona PIXEL_SCALE para incluir o pixel final
        
        fill_color = MSX_PALETTE[self.current_drawing_color] if fill else ""
        outline_color = MSX_PALETTE[self.current_drawing_color]

        self.canvas.create_rectangle(x0_c, y0_c, x1_c, y1_c,
                                     fill=fill_color,
                                     outline=outline_color,
                                     width=PIXEL_SCALE, # Borda mais grossa para o preview
                                     tags="preview_shape")

    def draw_circle_pixels(self, x0: int, y0: int, x1: int, y1: int, fill: bool):
        """Desenha um círculo (cheio ou vazio) usando o algoritmo de ponto médio."""
        center_x = (x0 + x1) // 2
        center_y = (y0 + y1) // 2
        radius = int(sqrt((x1 - x0)**2 + (y1 - y0)**2) / 2) # Distância do centro ao ponto mais distante

        pixels_to_update_y = set()

        def plot_circle_points(cx, cy, x, y):
            """Desenha os 8 pontos simétricos de um círculo."""
            points = [
                (cx + x, cy + y), (cx - x, cy + y), (cx + x, cy - y), (cx - x, cy - y),
                (cx + y, cy + x), (cx - y, cy + x), (cx + y, cy - x), (cx - y, cy - x),
            ]
            for px, py in points:
                if 0 <= px < MSX_WIDTH and 0 <= py < MSX_HEIGHT:
                    self.draw_pencil_pixel(px, py)
                    pixels_to_update_y.add(py)

        x = 0
        y = radius
        d = 3 - 2 * radius # Parâmetro de decisão inicial para o algoritmo de ponto médio

        plot_circle_points(center_x, center_y, x, y)

        while y >= x:
            x += 1
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6
            plot_circle_points(center_x, center_y, x, y)

        if fill:
            # Preenchimento do círculo (simplesmente desenha linhas horizontais)
            for y_line in range(center_y - radius, center_y + radius + 1):
                if 0 <= y_line < MSX_HEIGHT:
                    # Encontra os pontos mais à esquerda e à direita para esta linha
                    x_start = -1
                    x_end = -1
                    for x_fill in range(MSX_WIDTH):
                        if self.pixels[y_line][x_fill] == self.current_drawing_color: # Se for um pixel da borda do círculo
                            if x_start == -1:
                                x_start = x_fill
                            x_end = x_fill
                    
                    if x_start != -1 and x_end != -1:
                        for x_fill in range(x_start, x_end + 1):
                            self.draw_pencil_pixel(x_fill, y_line)
                            pixels_to_update_y.add(y_line)
        
        # Aplica a restrição de cor para todas as linhas afetadas
        for y_affected in pixels_to_update_y:
            self.apply_msx_color_constraint(y_affected, 0, MSX_WIDTH-1) # Aplica a toda a linha, mais seguro para círculos


    def _preview_circle(self, x0, y0, x1, y1, fill: bool):
        """Desenha um círculo de preview no canvas."""
        center_x_msx = (x0 + x1) // 2
        center_y_msx = (y0 + y1) // 2
        
        # O raio é a distância do centro a um dos pontos extremos
        radius_msx = int(sqrt((x1 - x0)**2 + (y1 - y0)**2) / 2)
        
        # Coordenadas do canvas
        center_x_c = center_x_msx * PIXEL_SCALE
        center_y_c = center_y_msx * PIXEL_SCALE
        radius_c = radius_msx * PIXEL_SCALE

        x_start_c = center_x_c - radius_c
        y_start_c = center_y_c - radius_c
        x_end_c = center_x_c + radius_c + PIXEL_SCALE # + PIXEL_SCALE para incluir o último pixel MSX
        y_end_c = center_y_c + radius_c + PIXEL_SCALE

        fill_color = MSX_PALETTE[self.current_drawing_color] if fill else ""
        outline_color = MSX_PALETTE[self.current_drawing_color]

        self.canvas.create_oval(x_start_c, y_start_c, x_end_c, y_end_c,
                                fill=fill_color,
                                outline=outline_color,
                                width=PIXEL_SCALE,
                                tags="preview_shape")


    def fill_area(self, start_x: int, start_y: int, fill_color_index: int):
        """
        Preenchimento de área (Flood Fill).
        Este é um algoritmo recursivo (ou iterativo com pilha) para preencher uma área contígua.
        """
        if not (0 <= start_x < MSX_WIDTH and 0 <= start_y < MSX_HEIGHT):
            return

        target_color_index = self.pixels[start_y][start_x]
        if target_color_index == fill_color_index:
            return # Já está preenchido com a cor alvo

        stack = [(start_x, start_y)]
        visited = set()
        pixels_to_update_y = set() # Para aplicar a restrição de cor no final

        while stack:
            x, y = stack.pop()

            if not (0 <= x < MSX_WIDTH and 0 <= y < MSX_HEIGHT):
                continue
            if (x, y) in visited:
                continue
            visited.add((x, y))

            if self.pixels[y][x] == target_color_index:
                self.pixels[y][x] = fill_color_index
                self.draw_pixel_on_canvas(x, y, fill_color_index)
                pixels_to_update_y.add(y)

                # Adiciona vizinhos à pilha
                stack.append((x + 1, y))
                stack.append((x - 1, y))
                stack.append((x, y + 1))
                stack.append((x, y - 1))
        
        # Aplica a restrição de cor para todas as linhas afetadas
        for y_affected in pixels_to_update_y:
            self.apply_msx_color_constraint(y_affected, 0, MSX_WIDTH-1) # Aplica a toda a linha


    # --- Funções de Salvar/Carregar (Esqueletos) ---
    def save_screen_data(self, filename: str):
        """
        Salva os dados da tela MSX.
        Este é um placeholder. A implementação real dependerá do formato
        que você deseja usar (e.g., binário, array de bytes para BASIC/Assembly).
        Você precisará extrair o Pattern Table, Color Table e Name Table.
        """
        print(f"Salvando dados da tela MSX em {filename}...")
        # Lógica para converter self.pixels em Pattern Table, Color Table, Name Table
        # Exemplo simples: salvar como uma imagem BMP para visualização rápida (não nativo MSX)
        from PIL import Image
        img = Image.new('P', (MSX_WIDTH, MSX_HEIGHT))
        img.putpalette([int(c[i:i+2], 16) for color_hex in MSX_PALETTE.values() for i in (1,3,5)]) # RGB bytes
        
        for y in range(MSX_HEIGHT):
            for x in range(MSX_WIDTH):
                img.putpixel((x, y), self.pixels[y][x])
        
        img.save(f"{filename}.bmp")
        print(f"Imagem BMP salva: {filename}.bmp (para visualização, não é formato MSX nativo)")


    def load_screen_data(self, filename: str):
        """Carrega dados da tela MSX."""
        print(f"Carregando dados da tela MSX de {filename}...")
        # TODO: Implementar lógica para carregar dados de um arquivo MSX
        # e preencher self.pixels.

# Exemplo de como integrar ao seu App principal:
# No seu arquivo principal (App.py):
# def open_editor_screen2(self):
#     self.clear_content_frame()
#     self.screen2_editor = MSScreen2Editor(self.content_frame, app_instance=self)
#     self.screen2_editor.pack(expand=True, fill="both")
#     # Exemplo de uso:
#     # self.screen2_editor.set_drawing_color(MSX_PALETTE_INV["#FF8C8C"]) # Definir cor de desenho para Vermelho Claro
#     # self.screen2_editor.set_tool("line") # Definir ferramenta como linha