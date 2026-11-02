import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image, ImageTk
import requests
from io import BytesIO

def load_image_from_url(url, size):
    try:
        response = requests.get(url)
        response.raise_for_status()
        image_data = response.content
        image = Image.open(BytesIO(image_data))
        image = image.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(image)
    except requests.RequestException as e:
        messagebox.showerror("Erreur", f"Impossible de charger l'image : {e}")
        return None

def generate_order(pages_per_booklet):
    """Génère l'ordre des pages selon la règle spécifiée."""
    if pages_per_booklet == 16:
        return [15, 0, 1, 14, 13, 2, 3, 12, 11, 4, 5, 10, 9, 6, 7, 8]
    elif pages_per_booklet == 24:
        return [23, 0, 1, 22, 21, 2, 3, 20, 19, 4, 5, 18, 17, 6, 7, 16, 15, 8, 9, 14, 13, 10, 11, 12]
    elif pages_per_booklet == 32:
        return [31, 0, 1, 30, 29, 2, 3, 28, 27, 4, 5, 26, 25, 6, 7, 24, 23, 8, 9, 22, 21, 10, 11, 20, 19, 12, 13, 18, 17, 14, 15, 16]
    else:
        raise ValueError("Nombre de pages par cahier non supporté")

def process_pdf(pdf_path, output_dir, pages_per_booklet):
    try:
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        num_files = (total_pages + pages_per_booklet - 1) // pages_per_booklet
        order = generate_order(pages_per_booklet)
        merged_writer = PdfWriter()

        for file_index in range(num_files):
            writer = PdfWriter()
            start_index = file_index * pages_per_booklet
            end_index = start_index + pages_per_booklet
            pages = [reader.pages[i] if i < total_pages else None for i in range(start_index, end_index)]

            for idx in order:
                if idx < len(pages) and pages[idx] is not None:
                    writer.add_page(pages[idx])
                    merged_writer.add_page(pages[idx])
                else:
                    width, height = (595.276, 841.890)
                    writer.add_blank_page(width=width, height=height)
                    merged_writer.add_blank_page(width=width, height=height)

            output_file = os.path.join(output_dir, f"output_part_{file_index + 1}.pdf")
            with open(output_file, "wb") as output_pdf:
                writer.write(output_pdf)

        merged_output_file = os.path.join(output_dir, "merged_output.pdf")
        with open(merged_output_file, "wb") as merged_pdf:
            merged_writer.write(merged_pdf)

        messagebox.showinfo("Succès", f"Découpage terminé. Fichiers générés dans {output_dir}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Problème lors du traitement : {e}")

def start_processing():
    pdf_path = pdf_path_var.get()
    output_dir = output_dir_var.get()
    if not os.path.isfile(pdf_path):
        messagebox.showerror("Erreur", "Fichier PDF invalide ou introuvable.")
        return
    if not os.path.isdir(output_dir):
        messagebox.showerror("Erreur", "Répertoire de sortie invalide.")
        return
    pages_per_booklet = int(pages_combobox.get())
    if pages_per_booklet not in [16, 24, 32]:
        messagebox.showerror("Erreur", "Nombre de pages par cahier non supporté. Veuillez choisir 16, 24 ou 32 pages.")
        return
    process_pdf(pdf_path, output_dir, pages_per_booklet)

# Fenêtre principale
root = tk.Tk()
root.title("PDFtoCahiers")
root.configure(bg="#f0f0f0")

# Cadre principal
main_frame = tk.Frame(root, bg="#ffffff", padx=20, pady=20, relief=tk.RIDGE, borderwidth=3)
main_frame.pack(pady=20, padx=20)

# Ajouter un titre
tk.Label(main_frame, text="Découpage en cahiers PDF", bg="#ffffff", font=("Arial", 16, "bold")).pack(pady=10)

# Variables
tk.Label(main_frame, text="Chemin du fichier PDF :", bg="#ffffff", font=("Arial", 12)).pack(anchor="w")
pdf_path_var = tk.StringVar()
pdf_entry = tk.Entry(main_frame, textvariable=pdf_path_var, width=50, font=("Arial", 10))
pdf_entry.pack(pady=5)
tk.Button(main_frame, text="Parcourir", command=lambda: pdf_path_var.set(filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])), bg="#007BFF", fg="white", font=("Arial", 10), relief=tk.FLAT).pack(pady=5)

# Répertoire de sortie
tk.Label(main_frame, text="Répertoire de sortie :", bg="#ffffff", font=("Arial", 12)).pack(anchor="w")
output_dir_var = tk.StringVar()
output_entry = tk.Entry(main_frame, textvariable=output_dir_var, width=50, font=("Arial", 10))
output_entry.pack(pady=5)
tk.Button(main_frame, text="Parcourir", command=lambda: output_dir_var.set(filedialog.askdirectory()), bg="#007BFF", fg="white", font=("Arial", 10), relief=tk.FLAT).pack(pady=5)

# Choix du nombre de pages
tk.Label(main_frame, text="Pages par cahier :", bg="#ffffff", font=("Arial", 12)).pack(anchor="w")
pages_combobox = ttk.Combobox(main_frame, values=[16, 24, 32], state="readonly", font=("Arial", 10))
pages_combobox.current(0)
pages_combobox.pack(pady=5)

# Bouton démarrer
tk.Button(main_frame, text="Démarrer le traitement", bg="#28A745", fg="white", font=("Arial", 12, "bold"), relief=tk.FLAT, padx=10, pady=5, command=start_processing).pack(pady=15)

# Lancer la boucle principale
root.mainloop()
