import sys
import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage
import numpy as np
from scipy.stats import qmc
import pandas as pd
import subprocess
import os
import webbrowser

freecad_python_path = ""
output_folder = ""
SU2_CFD_path = ""
paths_selected = 0
geometries_generated = 0

def select_paths():
    global freecad_python_path, output_folder, paths_selected, SU2_CFD_path
    messagebox.showinfo("FreeCAD Python", "Select the FreeCAD Python executable.")
    freecad_python_path = filedialog.askopenfilename(title="Select FreeCAD Python Executable",
                                                     filetypes=[("Python Executable", "*.exe")])
    messagebox.showinfo("Output Folder", "Select output folder for FreeCAD results.")
    output_folder = filedialog.askdirectory(title="Select Output Folder")
    messagebox.showinfo("SU2_CFD", "Select the SU2_CFD executable.")
    SU2_CFD_path = filedialog.askopenfilename(title="Select SU2_CFD Executable",
                                                     filetypes=[("SU2_CFD Executable", "*.exe")])
    paths_selected = 1
    if not (freecad_python_path and output_folder):
        messagebox.showerror("Error", "Both Pathways must be selected. Please try again.")
def run_freecad_macro(csv_path):
    macro_path = os.path.join(os.path.dirname(__file__), "macro.FCMacro")
    if macro_path:
        subprocess.run([freecad_python_path, macro_path, csv_path])
def delta(c, b, sweep, trail):
    return c - b * (np.tan(np.radians(sweep)) + np.tan(np.radians(trail)))
def generate_and_run(entries, labels, sample_count_var, window):
    global geometries_generated
    try:
        bounds = []
        for entry in entries:
            vals = list(map(float, entry.get().split()))
            if len(vals) != 2:
                raise ValueError("Each field must contain min and max values.")
            bounds.append(sorted(vals))
        param_bounds = np.array(bounds)
        sampler = qmc.LatinHypercube(d=param_bounds.shape[0])
        sample_count = int(sample_count_var.get())
        lhs_samples = sampler.random(n=sample_count)
        scaled = qmc.scale(lhs_samples, param_bounds[:, 0], param_bounds[:, 1])

        df = pd.DataFrame(scaled, columns=labels)
        df["Output Folder"] = output_folder
        csv_path = os.path.join(output_folder, "samples.csv")
        df.to_csv(csv_path, index=False)
        samples, trash = [], []
        for i in range(len(df)):
            c, sweep, span, trail, root = df.iloc[i, :5]
            b = span / 2
            d_val = delta(c, b, sweep, trail)
            row = list(df.iloc[i])
            if d_val >= 0:
                samples.append(row)
            else:
                trash.append(row)
        pd.DataFrame(samples, columns=df.columns).to_csv(os.path.join(output_folder, "samples.csv"), index=False)
        trash_df = pd.DataFrame(trash, columns=df.columns)
        if not trash_df.empty:
            trash_df.to_csv(os.path.join(output_folder, "trash.csv"), index=False)
        total = len(samples) + len(trash)
        valid_pct = 100 * len(samples) / total if total > 0 else 0
        trash_pct = 100 * len(trash) / total if total > 0 else 0
        if valid_pct < 50.0:
            chord = trash_df["Chord Length"].values
            sweep = trash_df["Sweep Angle"].values
            span = trash_df["Wing Span"].values
            trail = trash_df["Trailing Angle"].values
            b = span / 2
            d0 = delta(chord, b, sweep, trail)
            delta_changes = {
                "Chord Length": np.mean(delta(chord * 1.05, b, sweep, trail) - d0),
                "Sweep Angle": np.mean(delta(chord, b, sweep * 1.05, trail) - d0),
                "Wing Span": np.mean(delta(chord, b * 1.05, sweep, trail) - d0),
                "Trailing Angle": np.mean(delta(chord, b, sweep, trail * 1.05) - d0)
            }
            suggestions = []
            for param, change in delta_changes.items():
                direction = "reduce" if change < 0 else "increase"
                suggestions.append(f"- {param}: consider to {direction} (Δdelta {change:+.2f})")
            delta_tip = (
                    f"Only {valid_pct:.1f}% of the geometries are valid.\n"
                    "\nNote: Δdelta indicates the effect on wing profile feasibility.\n"
                    "Delta = Chord Length - Span * (tan(Sweep Angle) + tan(Trailing Angle)).\n"
                    "Positive delta → valid geometry, Negative delta → invalid geometry.\n"
                    "\nTips to reduce invalid samples:\n" + "\n".join(suggestions)
            )
            messagebox.showerror("Low Valid Geometry Rate", delta_tip)
            window.lift()
            return
        else:
            msg = f"{len(samples)} valid samples ({valid_pct:.1f}%).\n{len(trash)} invalid samples ({trash_pct:.1f}%)."
            messagebox.showinfo("Result", msg)
            run_freecad_macro(csv_path)
            geometries_generated = 1
            #window.destroy()
    except Exception as e:
        messagebox.showerror("Error", str(e))


labels = ["Chord Length", "Sweep Angle", "Wing Span", "Trailing Angle", "Root Thickness"]
form = tk.Tk()
form.title("Single Delta Wing Optimization")
form.geometry("423x400")
form.resizable(True, False)
sample_count_var = tk.StringVar()
entries = []
column_width = 200
row_width = 40
for i, label in enumerate(labels):
    tk.Label(form, text=f"{label} (min max):", font='Arial 11').place(x=10, y=10+row_width*i)
    ent = tk.Entry(form, font='Arial 12', width=10)
    ent.place(x=column_width, y=10+row_width*i)
    entries.append(ent)
tk.Label(form, text="Number of geometries:", font="Arial 11").place(x=10,y=10+row_width*len(labels))
tk.Entry(form, textvariable=sample_count_var, font="Arial 12", width=10).place(x=column_width,y=10+row_width*len(labels))
mach_label = tk.Label(form, text="Operating Mach Number(s):", font="Arial 11")
mach_label.place(x=10, y=10+row_width*6)
mach_entry = tk.Entry(form, font="Arial 12", width=20)
mach_entry.place(x=column_width, y=10+row_width*6)
coefficients_label = tk.Label(form, text="Mach Coefficient(s):", font="Arial 11")
coefficients_label.place(x=10, y=10+row_width*7)
coefficients_entry = tk.Entry(form, font="Arial 12", width=20)
coefficients_entry.place(x=column_width, y=10+row_width*7)
def generate_geometry():
    if paths_selected == 0:
        messagebox.showerror("Error", "Please select paths by clicking the 'Select Paths' button.")
    else:
        generate_and_run(entries, labels, sample_count_var, form)
def generate_mesh():
    meshing_script = os.path.join(os.path.dirname(__file__), "meshing.py")
    if os.path.exists(meshing_script):
        subprocess.run([sys.executable, meshing_script, output_folder])
    else:
        messagebox.showerror("Error", "meshing.py not found.")
def analyse():
    analyse_script = os.path.join(os.path.dirname(__file__), "Analyse.py")
    optimization_script = os.path.join(os.path.dirname(__file__), "optimization.py")
    if os.path.exists(analyse_script):
        mach_input=mach_entry.get()
        mach_list=mach_input.split()
        mach_arg=",".join(mach_list)
        subprocess.run([sys.executable, analyse_script, output_folder, SU2_CFD_path,mach_arg])
        if os.path.exists(optimization_script):
            subprocess.run([sys.executable, optimization_script, output_folder, mach_arg])
            optimization_script = os.path.join(os.path.dirname(__file__), "optimization.py")
            if os.path.exists(optimization_script):
                coefficients_input = coefficients_entry.get()
                coefficients_list = coefficients_input.split()
                coefficients_arg = ",".join(coefficients_list)
                mach_input = mach_entry.get()
                mach_list = mach_input.split()
                mach_arg = ",".join(mach_list)
                subprocess.run([sys.executable, optimization_script, output_folder, mach_arg, coefficients_arg])
    else:
        messagebox.showerror("Error", "Analyse.py not found.")
def optimize():
    optimization_script = os.path.join(os.path.dirname(__file__), "optimization.py")
    if os.path.exists(optimization_script):
        coefficients_input = coefficients_entry.get()
        coefficients_list = coefficients_input.split()
        coefficients_arg = ",".join(coefficients_list)
        mach_input = mach_entry.get()
        mach_list = mach_input.split()
        mach_arg = ",".join(mach_list)
        subprocess.run([sys.executable, optimization_script, output_folder, mach_arg, coefficients_arg])
def continuous():
    generate_geometry()
    generate_mesh()
    analyse()
def open_website():
    webbrowser.open("https://me-eng.marmara.edu.tr/")

button_y= y=10+row_width*8
tk.Button(form, text="Generate Geometry", bg="#0071CE", fg="white",
          font="TimesNewRoman 12", command=generate_geometry).place(x=10, y=button_y)
tk.Button(form, text="Generate Mesh", bg="#0071CE", fg="white",
          font="TimesNewRoman 12", command=generate_mesh).place(x=195, y=button_y)
tk.Button(form, text="Analyse", bg="#0071CE", fg="white",
          font="TimesNewRoman 12", command=analyse).place(x=345, y=button_y)
tk.Button(form, text="Select Paths", bg="gray", fg="black",
          font="TimesNewRoman 12 bold", command=select_paths).place(x=305, y=130)
photo=PhotoImage(file=os.path.join(os.path.dirname(__file__), "University of Marmara.png"))
tk.Button(form, image=photo, command=open_website,bd=0).place(x=304,y=8)
tk.Button(form, text="Continuous", bg="gray", fg="black",
          font="TimesNewRoman 12 bold", command=continuous).place(x=305, y=170)

form.mainloop()