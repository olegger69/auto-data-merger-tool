"""
Диалог выбора цветовой палитры для графиков
"""

import tkinter as tk
from tkinter import ttk
from core.chart_palettes import ChartPalettes


class PaletteDialog:
    """Диалоговое окно выбора цветовой палитры"""

    def __init__(self, parent, current_palette: str):
        self.parent = parent
        self.current_palette = current_palette
        self.selected_palette = current_palette
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🎨 Выбор цветовой палитры")
        self.dialog.geometry("550x650")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 275
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 325
        self.dialog.geometry(f"+{max(0, x)}+{max(0, y)}")

        self._create_widgets()
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _create_widgets(self):
        """Создание виджетов диалога"""
        main_frame = ttk.Frame(self.dialog, padding=15)
        main_frame.pack(fill='both', expand=True)

        ttk.Label(
            main_frame,
            text="Выберите цветовую палитру для графиков",
            font=('Arial', 12, 'bold')
        ).pack(pady=(0, 5))

        ttk.Label(
            main_frame,
            text="Каждая палитра содержит набор цветов для столбчатых, линейных и круговых диаграмм",
            font=('Arial', 9),
            wraplength=500
        ).pack(pady=(0, 10))

        # Прокручиваемая область
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill='both', expand=True)

        self.canvas = tk.Canvas(canvas_frame, highlightthickness=0, borderwidth=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Привязка прокрутки к canvas
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel_linux)
        self.canvas.bind("<Button-5>", self._on_mousewheel_linux)

        # Привязка прокрутки ко всем дочерним виджетам
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<Button-4>", self._on_mousewheel_linux)
        self.scrollable_frame.bind("<Button-5>", self._on_mousewheel_linux)

        self.palette_var = tk.StringVar(value=self.current_palette)
        self.color_labels = {}

        # Создаём палитры
        for palette_key in ChartPalettes.get_available_palettes():
            palette_info = ChartPalettes.PALETTES[palette_key]

            option_frame = ttk.Frame(self.scrollable_frame, relief='groove', borderwidth=2)
            option_frame.pack(fill='x', pady=5)

            # Привязка прокрутки к каждой рамке палитры
            option_frame.bind("<MouseWheel>", self._on_mousewheel)
            option_frame.bind("<Button-4>", self._on_mousewheel_linux)
            option_frame.bind("<Button-5>", self._on_mousewheel_linux)

            top_frame = ttk.Frame(option_frame)
            top_frame.pack(fill='x', padx=10, pady=5)

            ttk.Radiobutton(
                top_frame,
                text=palette_info['name'],
                variable=self.palette_var,
                value=palette_key,
                command=lambda k=palette_key: self._show_preview(k)
            ).pack(side='left')

            ttk.Label(
                top_frame,
                text=palette_info['description'],
                font=('Arial', 9),
                foreground='gray'
            ).pack(side='left', padx=10)

            # Привязка прокрутки к верхнему фрейму
            top_frame.bind("<MouseWheel>", self._on_mousewheel)
            top_frame.bind("<Button-4>", self._on_mousewheel_linux)
            top_frame.bind("<Button-5>", self._on_mousewheel_linux)

            colors_frame = ttk.Frame(option_frame)
            colors_frame.pack(fill='x', padx=10, pady=(0, 10))

            for i, color in enumerate(palette_info['bar_colors'][:6]):
                color_label = tk.Label(
                    colors_frame,
                    bg=color,
                    width=3,
                    height=1,
                    relief='solid',
                    borderwidth=1
                )
                color_label.pack(side='left', padx=2)
                self.color_labels[f'{palette_key}_{i}'] = color_label

                # Привязка прокрутки к каждому цветному квадратику
                color_label.bind("<MouseWheel>", self._on_mousewheel)
                color_label.bind("<Button-4>", self._on_mousewheel_linux)
                color_label.bind("<Button-5>", self._on_mousewheel_linux)

            # Привязка прокрутки к фрейму с цветами
            colors_frame.bind("<MouseWheel>", self._on_mousewheel)
            colors_frame.bind("<Button-4>", self._on_mousewheel_linux)
            colors_frame.bind("<Button-5>", self._on_mousewheel_linux)

        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(15, 0))

        ttk.Button(btn_frame, text="❌ Отмена", command=self._on_cancel, width=15).pack(side='left')
        ttk.Button(btn_frame, text="✅ Применить", command=self._on_apply, width=15).pack(side='right')

        self._show_preview(self.current_palette)

    def _on_mousewheel(self, event):
        """Прокрутка колёсиком мыши (Windows/Mac)"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux(self, event):
        """Прокрутка колёсиком мыши (Linux)"""
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    def _show_preview(self, palette_key: str):
        """Показать превью цветов выбранной палитры"""
        palette_info = ChartPalettes.PALETTES[palette_key]

        for key, label in self.color_labels.items():
            label.configure(bg='white')

        for i, color in enumerate(palette_info['bar_colors'][:6]):
            label_key = f'{palette_key}_{i}'
            if label_key in self.color_labels:
                self.color_labels[label_key].configure(bg=color)

    def _on_apply(self):
        """Применить выбранную палитру"""
        self.selected_palette = self.palette_var.get()
        self.result = self.selected_palette
        self.dialog.destroy()

    def _on_cancel(self):
        """Отмена"""
        self.result = None
        self.dialog.destroy()

    def show(self) -> str:
        """Показать диалог и вернуть выбранную палитру"""
        self.parent.wait_window(self.dialog)
        return self.result