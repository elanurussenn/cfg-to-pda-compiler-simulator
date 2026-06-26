import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from dosya_okuma import EPSILON, oku_girdiler, oku_gramer
from pda_olusturucu import pda_uret
from pda_simulator import EMPTY_STACK, PDASimulator


class Arayuz:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Proje 6 - Yığınlı Otomat (PDA) Simülatörü")
        self.root.geometry("1180x720")
        self.root.minsize(1050, 640)

        self.grammar_path = tk.StringVar(value="gramer.json")
        self.input_value = tk.StringVar(value="")

        self.status_var = tk.StringVar(value="Gramer dosyasını yükleyip simülasyonu başlatın.")
        self.result_var = tk.StringVar(value="Sonuç: -")
        self.state_var = tk.StringVar(value="Durum: -")
        self.read_var = tk.StringVar(value="Okunan: -")
        self.remaining_var = tk.StringVar(value="Kalan: -")
        self.action_var = tk.StringVar(value="Geçiş: -")

        self.grammar_data = None
        self.pda_data = None
        self.simulator = None

        self.trace = []
        self.current_step = 0
        self.accepted = False
        self.auto_running = False

        self.generated_pda_file = "pda_gecisleri_uretilen.json"

        self._configure_style()
        self._build_ui()
        self._try_load_defaults()

    def baslat(self):
        self.root.mainloop()

    def _configure_style(self):
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("Result.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("Big.TButton", font=("Segoe UI", 10, "bold"), padding=6)

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        top = ttk.Frame(main)
        top.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(
            top,
            text="Yığınlı Otomat (PDA) Simülatörü",
            style="Title.TLabel"
        ).pack(side=tk.LEFT)

        ttk.Label(
            top,
            textvariable=self.status_var
        ).pack(side=tk.RIGHT)

        paned = ttk.PanedWindow(main, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(paned, padding=6)
        right = ttk.Frame(paned, padding=6)

        paned.add(left, weight=1)
        paned.add(right, weight=3)

        self._build_left_panel(left)
        self._build_right_panel(right)

    def _build_left_panel(self, parent):
        file_frame = ttk.LabelFrame(parent, text="Gramer dosyası", padding=8)
        file_frame.pack(fill=tk.X)

        self._file_row(
            file_frame,
            0,
            "CFG / Gramer",
            self.grammar_path,
            [("JSON", "*.json"), ("Tüm dosyalar", "*.*")]
        )

        ttk.Button(
            file_frame,
            text="Grameri Yükle ve PDA Üret",
            command=self.load_files,
            style="Big.TButton"
        ).grid(row=1, column=0, columnspan=3, sticky="ew", pady=(8, 0))

        file_frame.columnconfigure(1, weight=1)

        input_frame = ttk.LabelFrame(parent, text="Simülasyon girdisi", padding=8)
        input_frame.pack(fill=tk.X, pady=8)

        ttk.Label(
            input_frame,
            text="girdiler.txt dosyasından seç veya elle yaz:"
        ).pack(anchor="w")

        self.input_combo = ttk.Combobox(input_frame, textvariable=self.input_value)
        self.input_combo.pack(fill=tk.X, pady=(4, 8))

        button_grid = ttk.Frame(input_frame)
        button_grid.pack(fill=tk.X)

        ttk.Button(
            button_grid,
            text="Simülasyonu Hazırla",
            command=self.prepare_simulation,
            style="Big.TButton"
        ).grid(row=0, column=0, columnspan=2, sticky="ew", pady=2)

        ttk.Button(
            button_grid,
            text="Önceki",
            command=self.previous_step
        ).grid(row=1, column=0, sticky="ew", padx=(0, 3), pady=2)

        ttk.Button(
            button_grid,
            text="Sonraki",
            command=self.next_step
        ).grid(row=1, column=1, sticky="ew", padx=(3, 0), pady=2)

        self.auto_button = ttk.Button(
            button_grid,
            text="Otomatik Oynat",
            command=self.toggle_auto
        )
        self.auto_button.grid(row=2, column=0, sticky="ew", padx=(0, 3), pady=2)

        ttk.Button(
            button_grid,
            text="Sıfırla",
            command=self.reset_simulation
        ).grid(row=2, column=1, sticky="ew", padx=(3, 0), pady=2)

        button_grid.columnconfigure(0, weight=1)
        button_grid.columnconfigure(1, weight=1)

        grammar_frame = ttk.LabelFrame(
            parent,
            text="Okunan CFG ve üretilen PDA özeti",
            padding=8
        )
        grammar_frame.pack(fill=tk.BOTH, expand=True)

        self.grammar_text = tk.Text(
            grammar_frame,
            height=16,
            wrap="word",
            font=("Consolas", 10)
        )
        self.grammar_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(grammar_frame, command=self.grammar_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.grammar_text.configure(
            yscrollcommand=scrollbar.set,
            state="disabled"
        )

    def _build_right_panel(self, parent):
        info_frame = ttk.LabelFrame(parent, text="Anlık konfigürasyon", padding=8)
        info_frame.pack(fill=tk.X)

        ttk.Label(
            info_frame,
            textvariable=self.result_var,
            style="Result.TLabel"
        ).grid(row=0, column=0, sticky="w", padx=4)

        ttk.Label(
            info_frame,
            textvariable=self.state_var
        ).grid(row=0, column=1, sticky="w", padx=4)

        ttk.Label(
            info_frame,
            textvariable=self.read_var
        ).grid(row=1, column=0, sticky="w", padx=4)

        ttk.Label(
            info_frame,
            textvariable=self.remaining_var
        ).grid(row=1, column=1, sticky="w", padx=4)

        ttk.Label(
            info_frame,
            textvariable=self.action_var,
            wraplength=680
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=4, pady=(4, 0))

        info_frame.columnconfigure(1, weight=1)

        mid = ttk.Frame(parent)
        mid.pack(fill=tk.BOTH, expand=True, pady=8)

        stack_frame = ttk.LabelFrame(mid, text="Canlı yığın görünümü", padding=8)
        stack_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 8))

        self.stack_canvas = tk.Canvas(
            stack_frame,
            width=260,
            height=430,
            bg="white",
            highlightthickness=1,
            highlightbackground="#bdbdbd"
        )
        self.stack_canvas.pack(fill=tk.BOTH, expand=True)

        table_frame = ttk.LabelFrame(mid, text="Adım adım çalışma tablosu", padding=8)
        table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        columns = ("step", "state", "read", "remaining", "stack", "action")

        self.step_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=16
        )

        self.step_table.heading("step", text="Adım")
        self.step_table.heading("state", text="Durum")
        self.step_table.heading("read", text="Okunan")
        self.step_table.heading("remaining", text="Kalan")
        self.step_table.heading("stack", text="Yığın alt→üst")
        self.step_table.heading("action", text="Uygulanan geçiş")

        self.step_table.column("step", width=50, anchor="center")
        self.step_table.column("state", width=90, anchor="center")
        self.step_table.column("read", width=90, anchor="center")
        self.step_table.column("remaining", width=90, anchor="center")
        self.step_table.column("stack", width=150, anchor="center")
        self.step_table.column("action", width=420)

        y_scroll = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.step_table.yview
        )

        x_scroll = ttk.Scrollbar(
            table_frame,
            orient=tk.HORIZONTAL,
            command=self.step_table.xview
        )

        self.step_table.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )

        self.step_table.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.step_table.bind("<<TreeviewSelect>>", self._table_selected)

        self._draw_stack([])

    def _file_row(self, parent, row, label, variable, filetypes):
        ttk.Label(
            parent,
            text=label + ":"
        ).grid(row=row, column=0, sticky="w", pady=2)

        ttk.Entry(
            parent,
            textvariable=variable
        ).grid(row=row, column=1, sticky="ew", padx=4, pady=2)

        ttk.Button(
            parent,
            text="Seç",
            command=lambda: self._select_file(variable, filetypes),
        ).grid(row=row, column=2, sticky="e", pady=2)

    def _select_file(self, variable, filetypes):
        selected = filedialog.askopenfilename(filetypes=filetypes)

        if selected:
            variable.set(selected)

    def _try_load_defaults(self):
        try:
            self.load_files(silent=True)
        except Exception:
            pass

    def load_files(self, silent=False):
        try:
            self.grammar_data = oku_gramer(self.grammar_path.get())

            self.pda_data = pda_uret(self.grammar_data)

            with open(self.generated_pda_file, "w", encoding="utf-8") as file:
                json.dump(self.pda_data, file, ensure_ascii=False, indent=4)

            self.simulator = PDASimulator(self.pda_data, self.grammar_data)

            try:
                inputs = oku_girdiler("girdiler.txt")
            except Exception:
                inputs = []

            combo_values = [
                EPSILON if value == "" else value
                for value in inputs
            ]

            self.input_combo.configure(values=combo_values)

            if combo_values and not self.input_value.get():
                self.input_value.set(combo_values[0])

            self._write_summary()

            self.status_var.set(
                f"Gramer okundu. PDA otomatik üretildi ve {self.generated_pda_file} dosyasına yazıldı."
            )

            if not silent:
                messagebox.showinfo(
                    "Başarılı",
                    "Gramer dosyası okundu. PDA geçişleri otomatik oluşturuldu."
                )

        except Exception as exc:
            self.status_var.set("Gramer yükleme hatası.")

            if not silent:
                messagebox.showerror("Hata", str(exc))

            raise

    def _write_summary(self):
        grammar = self.grammar_data
        pda = self.pda_data

        lines = []

        lines.append("CFG")
        lines.append("---")
        lines.append(f"Dil: {grammar.get('description', '-')}")
        lines.append(f"Non-terminal semboller: {', '.join(grammar['nonterminals'])}")
        lines.append(f"Terminal semboller: {', '.join(grammar['terminals'])}")
        lines.append(f"Başlangıç sembolü: {grammar['start_symbol']}")
        lines.append("")
        lines.append("Üretimler:")

        for left, rights in grammar["productions"].items():
            formatted = []

            for right in rights:
                formatted.append("".join(right) if right else EPSILON)

            lines.append(f"  {left} → {' | '.join(formatted)}")

        lines.append("")
        lines.append("OTOMATİK ÜRETİLEN PDA")
        lines.append("----------------------")
        lines.append(f"Durumlar: {', '.join(pda['states'])}")
        lines.append(f"Başlangıç durumu: {pda['start_state']}")
        lines.append(f"Başlangıç yığın sembolü: {pda['start_stack_symbol']}")
        lines.append(f"Kabul durumları: {', '.join(pda['accept_states'])}")
        lines.append(f"Geçiş sayısı: {len(pda['transitions'])}")
        lines.append(f"Üretilen geçiş dosyası: {self.generated_pda_file}")
        lines.append("")
        lines.append("Geçişler:")

        for transition in pda["transitions"]:
            push_text = "".join(transition["push"]) if transition["push"] else EPSILON

            lines.append(
                f"  δ({transition['from']}, {transition['input']}, {transition['pop']}) "
                f"→ ({transition['to']}, {push_text})"
            )

        self.grammar_text.configure(state="normal")
        self.grammar_text.delete("1.0", tk.END)
        self.grammar_text.insert(tk.END, "\n".join(lines))
        self.grammar_text.configure(state="disabled")

    def prepare_simulation(self):
        if self.simulator is None:
            try:
                self.load_files(silent=True)
            except Exception as exc:
                messagebox.showerror("Hata", str(exc))
                return

        input_text = self.input_value.get().strip()

        if input_text == EPSILON:
            input_text = ""

        try:
            result = self.simulator.simulate(input_text)
        except Exception as exc:
            messagebox.showerror("Simülasyon hatası", str(exc))
            return

        self.trace = result["trace"]
        self.accepted = result["accepted"]
        self.current_step = 0
        self.auto_running = False

        self.auto_button.configure(text="Otomatik Oynat")

        self._fill_table()
        self._show_step(0)

        sonuc = "KABUL" if self.accepted else "RED"

        self.status_var.set(
            f"Simülasyon hazırlandı. Sonuç: {sonuc}. "
            f"İncelenen konfigürasyon: {result['explored']}"
        )

    def _fill_table(self):
        for item in self.step_table.get_children():
            self.step_table.delete(item)

        for snapshot in self.trace:
            self.step_table.insert(
                "",
                tk.END,
                iid=str(snapshot["step"]),
                values=(
                    snapshot["step"],
                    snapshot["state"],
                    snapshot["read_input"],
                    snapshot["remaining_input"],
                    snapshot["stack_bottom_to_top"],
                    snapshot["action"],
                ),
            )

    def _show_step(self, index):
        if not self.trace:
            self._draw_stack([])
            return

        index = max(0, min(index, len(self.trace) - 1))
        self.current_step = index

        snapshot = self.trace[index]

        if index == len(self.trace) - 1:
            sonuc = "KABUL" if self.accepted else "RED"
        else:
            sonuc = "ÇALIŞIYOR"

        self.result_var.set(f"Sonuç: {sonuc}")
        self.state_var.set(f"Durum: {snapshot['state']}")
        self.read_var.set(f"Okunan: {snapshot['read_input']}")
        self.remaining_var.set(f"Kalan: {snapshot['remaining_input']}")
        self.action_var.set(f"Geçiş: {snapshot['action']}")

        self._draw_stack(snapshot["stack"])

        iid = str(snapshot["step"])

        if self.step_table.exists(iid):
            self.step_table.selection_set(iid)
            self.step_table.focus(iid)
            self.step_table.see(iid)

    def _draw_stack(self, stack):
        canvas = self.stack_canvas
        canvas.delete("all")

        width = max(canvas.winfo_width(), 260)
        height = max(canvas.winfo_height(), 430)

        canvas.create_text(
            width / 2,
            22,
            text="YIĞIN",
            font=("Segoe UI", 13, "bold")
        )

        canvas.create_text(
            width / 2,
            44,
            text="üst taraf yukarıda",
            font=("Segoe UI", 9)
        )

        if not stack:
            canvas.create_rectangle(
                60,
                170,
                width - 60,
                230,
                outline="#444",
                width=2
            )

            canvas.create_text(
                width / 2,
                200,
                text=EMPTY_STACK,
                font=("Segoe UI", 18, "bold")
            )

            canvas.create_text(
                width / 2,
                255,
                text="Yığın boş",
                font=("Segoe UI", 10)
            )

            return

        box_w = min(150, width - 70)
        box_h = 36
        gap = 6
        top_start = 72

        symbols = list(reversed(stack))

        for i, symbol in enumerate(symbols):
            y1 = top_start + i * (box_h + gap)
            y2 = y1 + box_h

            x1 = (width - box_w) / 2
            x2 = x1 + box_w

            fill = "#d8ecff" if i == 0 else "#f4f4f4"
            outline = "#1f5f99" if i == 0 else "#555"

            canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill=fill,
                outline=outline,
                width=2
            )

            canvas.create_text(
                width / 2,
                (y1 + y2) / 2,
                text=symbol,
                font=("Segoe UI", 13, "bold")
            )

            if i == 0:
                canvas.create_text(
                    x2 + 35,
                    (y1 + y2) / 2,
                    text="← üst",
                    font=("Segoe UI", 9, "bold"),
                    anchor="w"
                )

        bottom_y = top_start + len(symbols) * (box_h + gap) + 6

        canvas.create_line(
            (width - box_w) / 2,
            bottom_y,
            (width + box_w) / 2,
            bottom_y,
            width=3
        )

        canvas.create_text(
            width / 2,
            min(bottom_y + 22, height - 20),
            text="alt",
            font=("Segoe UI", 9)
        )

    def next_step(self):
        if not self.trace:
            self.prepare_simulation()
            return

        if self.current_step < len(self.trace) - 1:
            self._show_step(self.current_step + 1)

    def previous_step(self):
        if self.trace and self.current_step > 0:
            self._show_step(self.current_step - 1)

    def reset_simulation(self):
        self.auto_running = False
        self.auto_button.configure(text="Otomatik Oynat")

        if self.trace:
            self._show_step(0)

    def toggle_auto(self):
        if not self.trace:
            self.prepare_simulation()

            if not self.trace:
                return

        self.auto_running = not self.auto_running

        self.auto_button.configure(
            text="Durdur" if self.auto_running else "Otomatik Oynat"
        )

        if self.auto_running:
            self._auto_tick()

    def _auto_tick(self):
        if not self.auto_running:
            return

        if self.current_step < len(self.trace) - 1:
            self._show_step(self.current_step + 1)
            self.root.after(700, self._auto_tick)
        else:
            self.auto_running = False
            self.auto_button.configure(text="Otomatik Oynat")

    def _table_selected(self, _event):
        selected = self.step_table.selection()

        if not selected:
            return

        try:
            index = int(selected[0])
        except ValueError:
            return

        if index != self.current_step:
            self._show_step(index)