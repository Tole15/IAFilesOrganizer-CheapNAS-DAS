import zipfile
import datetime
import os
import shutil
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, ttk

user_categories = []
base_directory = ''

def set_base_directory():
    global base_directory
    base_directory = filedialog.askdirectory()
    if base_directory:
        base_directory_label.config(text=f"Directorio base seleccionado: {base_directory}")
    else:
        messagebox.showwarning("Directorio Base", "No seleccionaste un directorio base.")

def add_categories():
    global user_categories, base_directory
    if base_directory:
        category = simpledialog.askstring("Nueva Categoría", "Ingresa el nombre para la nueva categoría:", parent=root)
        if category and category not in user_categories:
            user_categories.append(category)
            update_categories_list()
            category_path = os.path.join(base_directory, category)
            if not os.path.exists(category_path):
                os.makedirs(category_path)
                messagebox.showinfo("Categoría Añadida", f"Se ha añadido y creado la categoría: {category}")
        else:
            messagebox.showwarning("Categoría Existente o Vacía", "La categoría ya existe o el nombre está vacío.")
    else:
        messagebox.showwarning("Sin Directorio Base", "Primero selecciona un directorio base.")

def update_categories_list():
    categories_listbox.delete(0, tk.END)
    for category in user_categories:
        categories_listbox.insert(tk.END, category)

def create_subfolder(parent_path):
    subfolder_name = simpledialog.askstring("Subcarpeta", "Escribe el nombre de la subcarpeta (opcional, cancela para finalizar):", parent=root)
    if subfolder_name:
        new_path = os.path.join(parent_path, subfolder_name)
        if not os.path.exists(new_path):
            os.makedirs(new_path)
            messagebox.showinfo("Subcarpeta Creada", f"Subcarpeta creada: {subfolder_name}")
        return create_subfolder(new_path)
    return parent_path

def get_prefix():
    if not user_categories:
        messagebox.showwarning("Sin Categorías", "Primero configura las categorías.")
        return None, None
    
    category = simpledialog.askstring("Categoría", "Ingrese la categoría del archivo:", parent=root)
    if category not in user_categories:
        messagebox.showerror("Error", "La categoría ingresada no está configurada.")
        return None, None
    
    category_path = os.path.join(base_directory, category)
    subfolder_path = create_subfolder(category_path)
    
    path_relative_to_base = os.path.relpath(subfolder_path, base_directory)
    prefix = path_relative_to_base.replace(os.sep, "_") + "_"

    return subfolder_path, prefix

def unique_filename(path, filename):
    base, extension = os.path.splitext(filename)
    counter = 1
    unique_name = filename

    while os.path.exists(os.path.join(path, unique_name)):
        unique_name = f"{base}_{counter}{extension}"
        counter += 1

    return unique_name

def select_files_and_rename():
    filenames = filedialog.askopenfilenames(title="Selecciona archivos")
    if not filenames:
        return

    category_path, prefix = get_prefix()
    if not prefix:
        return
    
    additional_prefix = simpledialog.askstring("Prefijo Adicional", "Ingrese un prefijo adicional (opcional):", parent=root)
    if additional_prefix:
        prefix += f"{additional_prefix}_"

    progress = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate")
    progress.pack(pady=20)
    progress['maximum'] = len(filenames)

    for index, filename in enumerate(filenames):
        base_filename = os.path.basename(filename)
        new_name = prefix + base_filename

        if os.path.exists(os.path.join(category_path, new_name)):
            new_name = unique_filename(category_path, new_name)

        new_path = os.path.join(category_path, new_name)

        try:
            shutil.move(filename, new_path)
            messagebox.showinfo("Archivo Procesado", f"El archivo ha sido renombrado y movido a: {new_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo mover y renombrar el archivo: {e}")
        
        progress['value'] = index + 1
        root.update_idletasks()

    progress.pack_forget()

def delete_category():
    selected_category = categories_listbox.get(tk.ANCHOR)
    if not selected_category:
        messagebox.showwarning("Selección", "Por favor, selecciona una categoría para borrar.")
        return
    
    if messagebox.askyesno("Confirmar", f"¿Estás seguro de que quieres borrar la categoría '{selected_category}'?"):
        user_categories.remove(selected_category)
        update_categories_list()
        category_path = os.path.join(base_directory, selected_category)
        
        if messagebox.askyesno("Borrar Carpeta", "¿Quieres también borrar la carpeta correspondiente del sistema de archivos?"):
            try:
                shutil.rmtree(category_path)
                messagebox.showinfo("Eliminada", f"La categoría y su carpeta '{selected_category}' han sido eliminadas.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo borrar la carpeta: {e}")
        else:
            messagebox.showinfo("Eliminada", f"La categoría '{selected_category}' ha sido eliminada.")
            
def backup_categories():
    backup_dir = filedialog.askdirectory(title="Selecciona la carpeta de destino para el respaldo")
    if not backup_dir:
        messagebox.showwarning("Selección de Carpeta", "No se seleccionó una carpeta de destino para el respaldo.")
        return
    
    backup_filename = f"backup_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.zip"
    backup_path = os.path.join(backup_dir, backup_filename)

    with zipfile.ZipFile(backup_path, 'w') as backup_zip:
        for category in user_categories:
            category_path = os.path.join(base_directory, category)
            for root, dirs, files in os.walk(category_path):
                for file in files:
                    backup_zip.write(os.path.join(root, file), 
                                     os.path.relpath(os.path.join(root, file), 
                                     os.path.join(category_path, '..')))

    messagebox.showinfo("Respaldo Completado", f"Los archivos han sido respaldados en: {backup_path}")

def restore_from_backup():
    backup_file_path = filedialog.askopenfilename(title="Selecciona el archivo de respaldo para restaurar",
                                                  filetypes=[("Zip files", "*.zip")])
    if not backup_file_path:
        messagebox.showwarning("Selección de Archivo", "No se seleccionó un archivo de respaldo para restaurar.")
        return

    restore_dir = filedialog.askdirectory(title="Selecciona la carpeta de destino para la restauración")
    if not restore_dir:
        messagebox.showwarning("Selección de Carpeta", "No se seleccionó una carpeta de destino para la restauración.")
        return

    try:
        with zipfile.ZipFile(backup_file_path, 'r') as backup_zip:
            backup_zip.extractall(restore_dir)
        messagebox.showinfo("Restauración Completada", f"Los archivos han sido restaurados en: {restore_dir}")
    except Exception as e:
        messagebox.showerror("Error de Restauración", f"Ocurrió un error al intentar restaurar los archivos: {e}")

root = tk.Tk()
root.title("Aplicación de Nomenclatura de Archivos")

base_directory_label = ttk.Label(root, text="Paso 1: Selecciona el directorio base", font=("Helvetica", 14))
base_directory_label.pack(pady=10)

base_dir_button = ttk.Button(root, text="Seleccionar Directorio Base", command=set_base_directory)
base_dir_button.pack(pady=5)

categories_label = ttk.Label(root, text="Paso 2: Configura las categorías iniciales", font=("Helvetica", 14))
categories_label.pack(pady=10)

categories_listbox = tk.Listbox(root)
categories_listbox.pack(pady=10)

set_button = ttk.Button(root, text="Añadir Categoría", command=add_categories)
set_button.pack(pady=5)

delete_button = ttk.Button(root, text="Borrar Categoría", command=delete_category)
delete_button.pack(pady=5)

select_files_label = ttk.Label(root, text="Paso 3: Selecciona archivos y renómbralos", font=("Helvetica", 14))
select_files_label.pack(pady=10)

select_button = ttk.Button(root, text="Seleccionar Archivos y Renombrar", command=select_files_and_rename)
select_button.pack(pady=10)

backup_button = ttk.Button(root, text="Respaldar Categorías", command=backup_categories)
backup_button.pack(pady=5)

restore_button = ttk.Button(root, text="Restaurar desde Respaldo", command=restore_from_backup)
restore_button.pack(pady=5)

root.mainloop()

