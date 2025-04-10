import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import pandas as pd
from common.data_manipulation.string_tools import does_string_contain_substring_list


RARITY_OPTIONS = ["", "Common", "Uncommon", "Rare", "Mythic"]


def filter_cards(
    df,
    text_keywords=None,
    mana_colors=None,
    card_types=None,
    subtypes=None,
    supertypes=None,
    rarity=None,
    condition=None,
    is_foil=None,
    price_range=None,
    mana_value_range=None,
    power=None,
    toughness=None,
    match_any_keyword=True,
    mana_colors_exclusive=True,
    match_any_type=True,
    match_any_subtype=True,
    match_any_supertype=True
):
    """
    Filter Magic cards with various criteria.
    """
    filtered_df = df.copy()

    # Drop rows with missing required fields
    filtered_df = filtered_df.dropna(subset=['text', 'manaCost', 'type'])

    # Keyword in text
    if text_keywords:
        filtered_df = filtered_df[
            filtered_df['text'].apply(lambda t: does_string_contain_substring_list(t.lower(), text_keywords, do_any=match_any_keyword))
        ]

    # Mana colors
    if mana_colors:
        def color_filter(mana_cost_str):
            if not isinstance(mana_cost_str, str):
                return False
            card_colors = [c for c in mana_cost_str if c in ["W", "U", "B", "R", "G"]]
            if mana_colors_exclusive:
                return sorted(card_colors) == sorted(mana_colors)
            else:
                return any(c in card_colors for c in mana_colors)

        filtered_df = filtered_df[filtered_df["manaCost"].apply(color_filter)]

    # Card types (match substrings in 'type' column)
    if card_types:
        filtered_df = filtered_df[
            filtered_df['type'].apply(
                lambda typ: does_string_contain_substring_list(typ, card_types, do_any=match_any_type)
            )
        ]

    # Subtypes
    if subtypes:
        filtered_df = filtered_df[
            filtered_df['subtypes'].apply(
                lambda val: does_string_contain_substring_list(val, subtypes, do_any=match_any_subtype)
            )
        ]

    # Supertypes
    if supertypes:
        filtered_df = filtered_df[
            filtered_df['supertypes'].apply(
                lambda val: does_string_contain_substring_list(val, supertypes, do_any=match_any_supertype)
            )
        ]

    # Rarity
    if rarity:
        filtered_df = filtered_df[filtered_df['rarity'].str.lower() == rarity.lower()]

    # Condition
    if condition:
        filtered_df = filtered_df[filtered_df['condition'].str.lower() == condition.lower()]

    # Foil
    if is_foil is not None:
        filtered_df = filtered_df[filtered_df['is_foil'] == is_foil]

    # Price range
    if price_range:
        min_price, max_price = price_range
        filtered_df = filtered_df[
            (filtered_df['price'] >= min_price) & (filtered_df['price'] <= max_price)
        ]

    # Mana value
    if mana_value_range:
        min_val, max_val = mana_value_range
        filtered_df = filtered_df[
            (filtered_df['manaValue'] >= min_val) & (filtered_df['manaValue'] <= max_val)
        ]

    # Power
    if power is not None:
        filtered_df = filtered_df[filtered_df['power'] == str(power)]

    # Toughness
    if toughness is not None:
        filtered_df = filtered_df[filtered_df['toughness'] == str(toughness)]

    return filtered_df


class MTGFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MTG Card Filter Tool")
        self.df = None

        # File loading
        self.load_button = tk.Button(root, text="Load CSV", command=self.load_csv)
        self.load_button.grid(row=0, column=0, columnspan=2, pady=5)

        # Entry fields
        self.entries = {}
        filters = [
            ("Keywords", "text_keywords"),
            ("Mana Colors", "mana_colors"),
            ("Card Types", "card_types"),
            ("Subtypes", "subtypes"),
            ("Supertypes", "supertypes"),
            ("Rarity", "rarity"),
            ("Condition", "condition"),
            ("Power", "power"),
            ("Toughness", "toughness"),
            ("Min Price", "min_price"),
            ("Max Price", "max_price"),
            ("Min Mana Value", "min_mv"),
            ("Max Mana Value", "max_mv")
        ]

        for i, (label_text, key) in enumerate(filters, start=1):
            # if key == "mana_colors":
            #     continue

            tk.Label(root, text=label_text).grid(row=i, column=0, sticky="e")

            if key == "rarity":
                entry = ttk.Combobox(root, values=RARITY_OPTIONS, width=28)
                entry.current(0)

            else:
                entry = tk.Entry(root, width=30)

            entry.grid(row=i, column=1, sticky="w")
            self.entries[key] = entry

        # Replace the mana_colors UI with checkboxes + exclusive toggle
        self.color_vars = {color: tk.IntVar() for color in ["W", "U", "B", "R", "G"]}
        tk.Label(root, text="Mana Colors").grid(row=2, column=0, sticky="ne")

        color_frame = tk.Frame(root)
        color_frame.grid(row=2, column=1, sticky="w")
        for i, color in enumerate(self.color_vars):
            cb = tk.Checkbutton(color_frame, text=color, variable=self.color_vars[color])
            cb.grid(row=0, column=i)

        self.exclusive_colors_var = tk.IntVar()
        exclusive_cb = tk.Checkbutton(color_frame, text="Match only selected colors",
                                      variable=self.exclusive_colors_var)
        exclusive_cb.grid(row=1, column=0, columnspan=5, sticky="w")

        # Is Foil
        self.foil_var = tk.IntVar()
        self.foil_check = tk.Checkbutton(root, text="Is Foil Only", variable=self.foil_var)
        self.foil_check.grid(row=len(filters)+1, column=0, columnspan=2)

        # Filter button
        self.filter_button = tk.Button(root, text="Apply Filter", command=self.apply_filter)
        self.filter_button.grid(row=len(filters)+2, column=0, columnspan=2, pady=10)

        # Scrollable canvas for card results
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.grid(row=len(filters) + 3, column=0, columnspan=2, pady=5, sticky="nsew")

        self.canvas = tk.Canvas(self.canvas_frame, width=1200, height=400)
        self.scrollbar = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Store variables to track selection
        self.card_vars = []
        self.card_rows = []

        # Card count labels
        self.total_label = tk.Label(root, text="Total cards: 0")
        self.total_label.grid(row=len(filters) + 6, column=0, sticky="w", padx=5)

        self.filtered_label = tk.Label(root, text="Filtered cards: 0")
        self.filtered_label.grid(row=len(filters) + 6, column=2, sticky="w", padx=5)

        # Export button
        self.export_button = tk.Button(root, text="Export Filtered CSV", command=self.export_filtered)
        self.export_button.grid(row=len(filters) + 6, column=0, columnspan=2, pady=(5, 10))

        # Keep track of last filtered result
        self.last_filtered_df = pd.DataFrame()

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return
        # try:
        self.df = pd.read_csv(file_path)
        self.df = self.df.fillna('')
        messagebox.showinfo("Success", f"Loaded file with {len(self.df)} cards.")

        self.total_label.config(text=f"Total cards: {len(self.df)}")
        self.filtered_label.config(text="Filtered cards: 0")  # reset filtered count

        self.populate_dynamic_filters()

        # except Exception as e:
        #     messagebox.showerror("Error", str(e))

    def populate_dynamic_filters(self):
        def create_combobox(entry_key, column_name, row, column, label):
            if column_name not in self.df.columns:
                print(f"⚠️ Column '{column_name}' not found in the CSV. Skipping dynamic filter '{entry_key}'.")
                return

            values = sorted(self.df[column_name].dropna().unique().tolist())

            combobox = ttk.Combobox(self.root, values=[""] + values, width=28)
            combobox.current(0)
            combobox.grid(row=row, column=column, sticky="w")
            tk.Label(self.root, text=label).grid(row=row, column=0, sticky="e")

            self.entries[entry_key] = combobox

        # Map from entry keys to column names in CSV
        field_map = {
            "rarity": "rarity",
            "condition": "condition",
            "card_types": "types",  # use 'types' from CSV
            "supertypes": "supertypes"  # already good
        }

        # Remove old widgets if they exist (optional, depends if you're replacing)
        for key in field_map:
            if key in self.entries and isinstance(self.entries[key], ttk.Combobox):
                self.entries[key].destroy()

        # Re-create relevant dropdowns
        for i, (entry_key, column_name) in enumerate(field_map.items()):
            row_index = {
                "rarity": 6,
                "condition": 7,
                "card_types": 3,
                "supertypes": 5
            }.get(entry_key, i)
            create_combobox(entry_key, column_name, row=row_index, column=1, label=entry_key.replace("_", " ").title())

    def apply_filter(self):
        if self.df is None:
            messagebox.showerror("No Data", "Please load a CSV file first.")
            return

        kwargs = {
            "text_keywords": self.parse_list(self.entries["text_keywords"].get()),
            "mana_colors": self.parse_list(self.entries["mana_colors"].get()),
            "card_types": self.parse_list(self.entries["card_types"].get()),
            "subtypes": self.parse_list(self.entries["subtypes"].get()),
            "supertypes": self.parse_list(self.entries["supertypes"].get()),
            "rarity": self.entries["rarity"].get() or None,
            "condition": self.entries["condition"].get() or None,
            "power": self.entries["power"].get() or None,
            "toughness": self.entries["toughness"].get() or None,
            "is_foil": True if self.foil_var.get() == 1 else None
        }

        selected_colors = [color for color, var in self.color_vars.items() if var.get()]
        if selected_colors:
            kwargs["mana_colors"] = selected_colors
            kwargs["mana_colors_exclusive"] = bool(self.exclusive_colors_var.get())

        # Ranges
        min_price = self.entries["min_price"].get()
        max_price = self.entries["max_price"].get()
        if min_price or max_price:
            kwargs["price_range"] = (float(min_price or 0), float(max_price or float('inf')))

        min_mv = self.entries["min_mv"].get()
        max_mv = self.entries["max_mv"].get()
        if min_mv or max_mv:
            kwargs["mana_value_range"] = (float(min_mv or 0), float(max_mv or float('inf')))

        try:
            filtered = filter_cards(self.df, **kwargs)
            self.last_filtered_df = filtered  # save for export
        except Exception as e:
            messagebox.showerror("Filter Error", str(e))
            return

        self.filtered_label.config(text=f"Filtered cards: {len(filtered)}")
        self.display_results(filtered)

    def display_results(self, df):
        # Clear old widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.card_vars.clear()
        self.card_rows.clear()

        if df.empty:
            tk.Label(self.scrollable_frame, text="No cards matched the filter.").pack(anchor="w")
            return

        for idx, (_, row) in enumerate(df.iterrows()):
            var = tk.BooleanVar()
            self.card_vars.append(var)
            self.card_rows.append(row)

            frame = tk.Frame(self.scrollable_frame, relief="groove", borderwidth=2, padx=5, pady=5)
            frame.pack(fill="x", padx=5, pady=2)

            cb = tk.Checkbutton(frame, variable=var)
            cb.pack(side="left", anchor="n")

            info = (
                f"{row['name']} | Rarity: {row['rarity']} | Price: {row['price']} | "
                f"Mana: {row['manaCost']} | Type: {row['type']} | Stats: {row['power']}/{row['toughness']}\n"
                f"{row['text']}"
            )
            label = tk.Label(frame, text=info, justify="left", anchor="w", wraplength=1000)
            label.pack(side="left", fill="both", expand=True)

    def export_filtered(self):
        if not self.card_vars:
            messagebox.showinfo("No Results", "No filtered results to export.")
            return

        selected_rows = [row for var, row in zip(self.card_vars, self.card_rows) if var.get()]
        if not selected_rows:
            messagebox.showinfo("No Selection", "No cards selected for export.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                pd.DataFrame(selected_rows).to_csv(file_path, index=False)
                messagebox.showinfo("Export Successful", f"Exported {len(selected_rows)} selected cards.")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))

    @staticmethod
    def parse_list(val):
        return [v.strip() for v in val.split(",")] if val else None


# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = MTGFilterApp(root)
    root.mainloop()