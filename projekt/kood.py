import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import csv
import os
from datetime import datetime
import matplotlib.pyplot as plt

# -----------------------
# Globaalsed muutujad
# -----------------------
kasutaja = ""
valitud_kuu = datetime.today().month

# -----------------------
# Sisselogimine / kasutaja kontroll
# -----------------------
def alusta():
    global kasutaja
    kasutaja = entry_kasutaja.get()
    parool = entry_parool.get()

    if kasutaja == "" or parool == "":
        messagebox.showerror("Viga", "Täida kõik väljad!")
        return

    leitud = False

    # kasutajad.csv peab olemas olema ja sisaldama veerge: kasutaja,parool
    try:
        with open("kasutajad.csv", "r", encoding="UTF-8") as f:
            reader = csv.DictReader(f)
            for rida in reader:
                if rida["kasutaja"] == kasutaja and rida["parool"] == parool:
                    leitud = True
                    break
    except FileNotFoundError:
        messagebox.showerror("Viga", "Faili 'kasutajad.csv' ei leitud!")
        return

    if not leitud:
        messagebox.showerror("Viga", "Vale kasutajanimi või parool!")
        return

    fail = f"{kasutaja}_kulud.csv"

    if not os.path.exists(fail):
        with open(fail, "w", newline="", encoding="UTF-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Kuupäev", "Kategooria", "Summa", "Märkus", "Piir"])

    kasutaja_aken.destroy()
    ava_peaaken()

# -----------------------
# Kulu lisamine
# -----------------------
def lisa_kulu():
    try:
        kuupäev = entry_kuup.get()
        
        if kat_valik.get() == "Muu":
            kategooria = entry_kat_muu.get()
            if kategooria.strip() == "":
                messagebox.showerror("Viga", "Sisesta kategooria, kui valisid 'Muu'!")
                return
        else:
            kategooria = kat_valik.get()
                
        summa = float(entry_summa.get())
        märkus = entry_markus.get()
        piir = float(entry_piir.get())
    except ValueError:
        messagebox.showerror("Viga", "Summa ja piir peavad olema arvud!")
        return

    fail = f"{kasutaja}_kulud.csv"

    with open(fail, "a", newline="", encoding="UTF-8") as f:
        writer = csv.writer(f)
        writer.writerow([kuupäev, kategooria, summa, märkus, piir])

    kontrolli_piiri()

    messagebox.showinfo("Lisatud", "Kulu edukalt lisatud!")

# -----------------------
# Piiri kontroll
# -----------------------
def kontrolli_piiri():
    kokku = {}
    fail = f"{kasutaja}_kulud.csv"

    with open(fail, "r", encoding="UTF-8") as f:
        reader = csv.DictReader(f)
        for rida in reader:
            kat = rida["Kategooria"]
            summa = float(rida["Summa"])
            piir = float(rida["Piir"])

            if kat not in kokku:
                kokku[kat] = [0, piir]

            kokku[kat][0] += summa

    for kat, (summa, piir) in kokku.items():
        if summa > piir:
            messagebox.showwarning("Hoiatus!", f"{kat} on ületanud piiri!")

# -----------------------
# Graafik
# -----------------------
def kuva_graafik():
    kokku = {}
    fail = f"{kasutaja}_kulud.csv"

    with open(fail, "r", encoding="UTF-8") as f:
        reader = csv.DictReader(f)
        for rida in reader:
            kat = rida["Kategooria"]
            summa = float(rida["Summa"])
            kokku[kat] = kokku.get(kat, 0) + summa

    if not kokku:
        messagebox.showinfo("Info", "Kulud puuduvad, graafikut pole võimalik kuvada.")
        return

    plt.pie(kokku.values(), labels=kokku.keys(), autopct="%1.1f%%")
    plt.title("Kulude jaotus")
    plt.show()

# -----------------------
# Kuu kokkuvõte
# -----------------------
def kuva_kuu_kokkuvote():
    fail = f"{kasutaja}_kulud.csv"
    kokku = {}

    tana = datetime.today()
    see_kuu = valitud_kuu
    see_aasta = tana.year

    with open(fail, "r", encoding="UTF-8") as f:
        reader = csv.DictReader(f)
        for rida in reader:
            kuup = datetime.strptime(rida["Kuupäev"], "%Y-%m-%d")

            if kuup.month == see_kuu and kuup.year == see_aasta:
                kat = rida["Kategooria"]
                summa = float(rida["Summa"])
                kokku[kat] = kokku.get(kat, 0) + summa

    kokku_aken = tk.Toplevel()
    kokku_aken.title("Kuu kokkuvõte")
    kokku_aken.geometry("360x420")
    kokku_aken.configure(bg="#1e1e1e")

    tk.Label(
        kokku_aken,
        text="📅 Selle kuu kulude kokkuvõte",
        font=("Segoe UI", 14, "bold"),
        fg="white",
        bg="#1e1e1e"
    ).pack(pady=15)

    raam = tk.Frame(kokku_aken, bg="#2a2a2a")
    raam.pack(padx=20, pady=10, fill="both", expand=True)

    kogusumma = 0

    if not kokku:
        tk.Label(
            raam,
            text="Sellele kuule andmeid ei ole.",
            font=("Segoe UI", 11),
            fg="white",
            bg="#2a2a2a"
        ).pack(pady=10)
    else:
        for kat, summa in kokku.items():
            tk.Label(
                raam,
                text=f"{kat}: {summa:.2f} €",
                font=("Segoe UI", 11),
                fg="white",
                bg="#2a2a2a"
            ).pack(anchor="w", padx=10, pady=3)
            kogusumma += summa

        tk.Label(
            raam,
            text=f"\nKOKKU: {kogusumma:.2f} €",
            font=("Segoe UI", 13, "bold"),
            fg="#4CAF50",
            bg="#2a2a2a"
        ).pack(pady=15)

    tk.Button(
        raam,
        text="✅ Sulge",
        font=("Segoe UI", 11, "bold"),
        bg="#4CAF50",
        fg="white",
        command=kokku_aken.destroy
    ).pack(pady=10, fill="x", padx=10)

# -----------------------
# Kulude vaatamine ja kustutamine
# -----------------------
def kuva_kulud_ja_kustuta():
    fail = f"{kasutaja}_kulud.csv"

    aken = tk.Toplevel()
    aken.title("Kulude haldus")
    aken.geometry("700x400")

    tabel = ttk.Treeview(aken, columns=("Kuupäev", "Kategooria", "Summa", "Märkus", "Piir"), show="headings")
    for veerg in ("Kuupäev", "Kategooria", "Summa", "Märkus", "Piir"):
        tabel.heading(veerg, text=veerg)
        tabel.column(veerg, width=120)

    tabel.pack(fill="both", expand=True)

    with open(fail, "r", encoding="UTF-8") as f:
        reader = csv.reader(f)
        next(reader)  # päis
        for rida in reader:
            tabel.insert("", "end", values=rida)

    def kustuta_valitud():
        valik = tabel.selection()
        if not valik:
            messagebox.showinfo("Info", "Vali kõigepealt rida, mida kustutada.")
            return

        rida = tabel.item(valik)["values"]

        with open(fail, "r", encoding="UTF-8") as f:
            read = list(csv.reader(f))

        with open(fail, "w", newline="", encoding="UTF-8") as f:
            writer = csv.writer(f)
            for r in read:
                if r != list(map(str, rida)):
                    writer.writerow(r)

        tabel.delete(valik)

    tk.Button(aken, text="❌ Kustuta valitud kulu", command=kustuta_valitud).pack(pady=10)

# -----------------------
# Peaaken
# -----------------------
def ava_peaaken():
    global entry_kuup, entry_summa, entry_markus, entry_piir
    global kat_valik, entry_kat_muu

    root = tk.Tk()
    root.title("Tudengi eelarve haldur")
    root.geometry("420x600")
    root.configure(bg="#1e1e1e")

    # Pealkiri
    pealkiri = tk.Label(
        root,
        text="💰 Tudengi Eelarverakendus",
        font=("Segoe UI", 16, "bold"),
        fg="white",
        bg="#1e1e1e"
    )
    pealkiri.pack(pady=10)

    # Sisu raam
    raam = tk.Frame(root, bg="#2a2a2a")
    raam.pack(padx=20, pady=10, fill="both", expand=True)

    # Kuu valik
    def muuda_kuud(valik):
        global valitud_kuu
        valitud_kuu = int(valik)

    tk.Label(raam, text="Vali kuu", fg="white", bg="#2a2a2a").pack()

    kuuvalik = tk.StringVar(value=str(valitud_kuu))

    tk.OptionMenu(
        raam,
        kuuvalik,
        *[str(i) for i in range(1, 13)],
        command=muuda_kuud
    ).pack(fill="x", padx=10, pady=5)

    # Sisestusväljad
    def lisa_rida(tekst):
        silt = tk.Label(raam, text=tekst, fg="white", bg="#2a2a2a")
        silt.pack(anchor="w", padx=10)
        kast = tk.Entry(raam)
        kast.pack(fill="x", padx=10, pady=5)
        return kast

    entry_kuup = lisa_rida("Kuupäev (YYYY-MM-DD)")
    entry_kuup.insert(0, str(datetime.today().date()))
    
    #Kategooria rippmenüü ja 'Muu' tekstikast
    tk.Label(raam, text="Kategooria", fg="white",bg="#2a2a2a").pack(anchor="w",padx=10)
    
    kategooriad = ["Toit", "Transport", "Arved", "Meelelahutus", "Tervis", "Muu"]
    
    kat_valik = tk.StringVar()
    kat_valik.set(kategooriad[0]) #Vaikimisi "Toit"
    
    kategooria_menu = tk.OptionMenu(raam, kat_valik, *kategooriad)
    kategooria_menu.pack(fill="x", padx=10, pady=5)
    
    #Tekstikast, mis ilmub ainult kui valitakse 'Muu'
    entry_kat_muu = tk.Entry(raam)
    entry_kat_muu.pack(fill="x", padx=10, pady=5)
    entry_kat_muu.pack_forget() #Peidetud vaikimisi
    
    def kontrolli_muu(*args):
        if kat_valik.get() == "Muu": #Näitab kastikest kui valiti 'Muu'
            entry_kat_muu.pack(fill="x", padx=10, pady=5)
        else:
            entry_kat_muu.pack_forget()
    
    kat_valik.trace("w", kontrolli_muu)


    entry_summa = lisa_rida("Summa (€)")
    entry_markus = lisa_rida("Märkus")
    entry_piir = lisa_rida("Kategooria piir (€)")

    # Nupud
    tk.Button(
        raam,
        text="➕ Lisa kulu",
        bg="#4CAF50",
        fg="white",
        command=lisa_kulu
    ).pack(fill="x", padx=10, pady=5)

    tk.Button(
        raam,
        text="📅 Näita kuu kokkuvõtet",
        bg="#FF9800",
        fg="white",
        command=kuva_kuu_kokkuvote
    ).pack(fill="x", padx=10, pady=5)

    tk.Button(
        raam,
        text="🗑 Halda kulusid",
        bg="#F44336",
        fg="white",
        command=kuva_kulud_ja_kustuta
    ).pack(fill="x", padx=10, pady=5)

    tk.Button(
        raam,
        text="📊 Näita graafikut",
        bg="#2196F3",
        fg="white",
        command=kuva_graafik
    ).pack(fill="x", padx=10, pady=5)

    root.mainloop()

# -----------------------
# Sisselogimise aken
# -----------------------
def ilus_sisselogimine():
    global entry_kasutaja, entry_parool, kasutaja_aken

    kasutaja_aken = tk.Tk()
    kasutaja_aken.title("Sisselogimine")
    kasutaja_aken.geometry("360x260")
    kasutaja_aken.configure(bg="#1e1e1e")

    tk.Label(
        kasutaja_aken,
        text="👤 Kasutaja sisselogimine",
        font=("Segoe UI", 16, "bold"),
        fg="white",
        bg="#1e1e1e"
    ).pack(pady=20)

    raam = tk.Frame(kasutaja_aken, bg="#2a2a2a")
    raam.pack(padx=20, pady=10, fill="both", expand=True)

    tk.Label(
        raam,
        text="Sisesta kasutajanimi:",
        font=("Segoe UI", 11),
        fg="white",
        bg="#2a2a2a"
    ).pack(pady=5)

    entry_kasutaja = tk.Entry(raam, font=("Segoe UI", 12))
    entry_kasutaja.pack(pady=5, fill="x", padx=20)

    tk.Label(
        raam,
        text="Parool:",
        font=("Segoe UI", 11),
        fg="white",
        bg="#2a2a2a"
    ).pack(pady=5)

    entry_parool = tk.Entry(raam, font=("Segoe UI", 12), show="*")
    entry_parool.pack(pady=5, fill="x", padx=20)

    tk.Button(
        raam,
        text="🚀 Alusta",
        font=("Segoe UI", 12, "bold"),
        bg="#4CAF50",
        fg="white",
        command=alusta
    ).pack(pady=20, fill="x", padx=20)

    kasutaja_aken.mainloop()

# -----------------------
# Programmi käivitamine
# -----------------------
ilus_sisselogimine()