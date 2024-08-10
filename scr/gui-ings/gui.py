import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def browse_source_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        source_folder_entry.delete(0, tk.END)
        source_folder_entry.insert(0, folder_selected)

def browse_backup_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        backup_folder_entry.delete(0, tk.END)
        backup_folder_entry.insert(0, folder_selected)

def start_conversion():
    global progress_label, start_time, pause_event, cancel_event

    target_folder = source_folder_entry.get()
    backup_folder = backup_folder_entry.get()
    texture_format = texture_format_var.get()
    overwrite_vmat = overwrite_vmat_var.get()
    overwrite_tga = overwrite_tga_var.get()
    generate_normal = generate_normal_var.get()
    generate_height = generate_height_var.get()
    generate_roughness = generate_roughness_var.get()
    darkness_value = darkness_scale.get()

    if not target_folder or not backup_folder or not texture_format:
        messagebox.showerror("Error", "Please ensure all fields are filled in correctly!")
        return

    convert_button.config(state=tk.DISABLED)
    progress_label.config(text="Processing...")
    progress_bar.start()
    pause_button.config(state=tk.NORMAL)
    cancel_button.config(state=tk.NORMAL)

    pause_event = threading.Event()
    cancel_event = threading.Event()
    pause_event.set()  # Start in the running state

    def run_conversion():
        main(target_folder, backup_folder, texture_format, overwrite_vmat, overwrite_tga, generate_normal, generate_height, generate_roughness, darkness_value)
        progress_bar.stop()
        progress_label.config(text="Completed!")
        convert_button.config(state=tk.NORMAL)
        pause_button.config(state=tk.DISABLED)
        cancel_button.config(state=tk.DISABLED)

    threading.Thread(target=run_conversion).start()

def toggle_pause():
    if pause_event.is_set():
        pause_event.clear()  # Pause
        pause_button.config(text="Resume")
        progress_label.config(text="Paused")
    else:
        pause_event.set()  # Resume
        pause_button.config(text="Pause")

def cancel_conversion():
    cancel_event.set()
    progress_label.config(text="Cancelled")
    convert_button.config(state=tk.NORMAL)
    pause_button.config(state=tk.DISABLED)

def open_help():
    import webbrowser
    webbrowser.open('https://github.com/oskarmikey/vmt-to-vmat-enhanced-GUI/tree/main')

# Create GUI
root = tk.Tk()
root.title("VMT To VMAT and RoughGen")

# Console output
console_frame = tk.Frame(root)
console_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky=tk.W+tk.E)
console_output = tk.Text(console_frame, height=10, width=100, wrap=tk.WORD)
console_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
console_scroll = tk.Scrollbar(console_frame, command=console_output.yview)
console_scroll.pack(side=tk.RIGHT, fill=tk.Y)
console_output.config(yscrollcommand=console_scroll.set)

# Redirect stdout and stderr to console
class ConsoleWriter:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.text_widget.tag_configure("stderr", foreground="#b22222")

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()

    def flush(self):
        pass

sys.stdout = ConsoleWriter(console_output)
sys.stderr = ConsoleWriter(console_output)

# Help button
help_button = tk.Button(root, text="Help", command=open_help, bd=0, bg='lightgrey')
help_button.grid(row=1, column=2, padx=10, pady=5, sticky=tk.E)

# Material folder
tk.Label(root, text="Material Directory (containing VMT and texture files):").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
source_folder_entry = tk.Entry(root, width=50)
source_folder_entry.grid(row=2, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=browse_source_folder).grid(row=2, column=2, padx=10, pady=5)

# Backup folder
tk.Label(root, text="Backup Directory for VMT files:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
backup_folder_entry = tk.Entry(root, width=50)
backup_folder_entry.grid(row=3, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=browse_backup_folder).grid(row=3, column=2, padx=10, pady=5)

# Texture format
tk.Label(root, text="Texture Format (e.g., tga, png, jpg):").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
texture_format_var = tk.StringVar(value='tga')
texture_format_menu = tk.OptionMenu(root, texture_format_var, 'tga', 'png', 'jpg', 'dds', 'bmp')
texture_format_menu.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)

# Overwrite options
overwrite_vmat_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Overwrite VMAT files", variable=overwrite_vmat_var).grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
overwrite_tga_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Overwrite texture files", variable=overwrite_tga_var).grid(row=5, column=1, padx=10, pady=5, sticky=tk.W)

# Normal and roughness options
generate_normal_var = tk.BooleanVar(value=False)
tk.Checkbutton(root, text="Generate Normal Maps", variable=generate_normal_var).grid(row=6, column=0, padx=10, pady=5, sticky=tk.W)
generate_height_var = tk.BooleanVar(value=False)
tk.Checkbutton(root, text="Generate Height Maps", variable=generate_height_var).grid(row=6, column=1, padx=10, pady=5, sticky=tk.W)
generate_roughness_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Generate Roughness Maps", variable=generate_roughness_var).grid(row=6, column=2, padx=10, pady=5, sticky=tk.W)

# Darkness value
tk.Label(root, text="Darkness Value (0-255):").grid(row=7, column=0, padx=10, pady=5, sticky=tk.W)
darkness_scale = tk.Scale(root, from_=0, to=255, orient=tk.HORIZONTAL)
darkness_scale.set(128)
darkness_scale.grid(row=7, column=0, columnspan=2, padx=150, pady=10, sticky=tk.W)

# Convert button
convert_button = tk.Button(root, text="Convert", command=start_conversion, width=20, height=0)
convert_button.grid(row=8, column=0, columnspan=3, pady=10)

# Pause button
pause_button = tk.Button(root, text="Pause", command=toggle_pause, state=tk.DISABLED)
pause_button.grid(row=9, column=0, pady=10)

# Cancel button
cancel_button = tk.Button(root, text="Cancel", command=cancel_conversion, state=tk.DISABLED)
cancel_button.grid(row=9, column=1, pady=10)

# Progress label and bar
progress_label = tk.Label(root, text="Progress: 0%")
progress_label.grid(row=10, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)
progress_bar = ttk.Progressbar(root, mode='determinate')
progress_bar.grid(row=11, column=0, columnspan=3, padx=10, pady=5, sticky=tk.W+tk.E)

root.mainloop()