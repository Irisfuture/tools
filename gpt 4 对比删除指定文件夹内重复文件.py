
import os
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox, Scrollbar, Toplevel, Label, StringVar, Listbox, END, Entry, Button
import re


def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder_path)
        find_duplicates(folder_path)


def find_duplicates(folder_path):
    progress_window = Toplevel(root)
    progress_window.title("Progress")

    file_count_label_var = StringVar()
    progress_label_var = StringVar()

    file_count_label = Label(progress_window, textvariable=file_count_label_var)
    file_count_label.pack(pady=10)

    progress_label = Label(progress_window, textvariable=progress_label_var)
    progress_label.pack(pady=10)

    root.update_idletasks()

    # Count total number of files
    total_files = sum(len(files) for _, _, files in os.walk(folder_path))
    file_count_label_var.set(f"Total files: {total_files}")

    file_hashes = {}
    file_names = {}
    duplicates = []
    current_file_number = 0

    for root_dir, _, files in os.walk(folder_path):
        for file in files:
            current_file_number += 1
            progress_label_var.set(f"Processing file {current_file_number} of {total_files}")
            root.update_idletasks()

            file_path = os.path.join(root_dir, file)
            file_hash = hash_file(file_path)
            file_info = (file_path, os.path.getsize(file_path), os.path.getmtime(file_path))
            file_name_without_extension = os.path.splitext(file)[0]

            # Check for exact hash matches
            if file_hash in file_hashes:
                similar_file_info = file_hashes[file_hash]
                duplicates.append((file_info, similar_file_info, "exact"))
            else:
                file_hashes[file_hash] = file_info

            # Check for similar file names
            base_name = re.sub(r"\(\d+\)$", "", file_name_without_extension)
            if base_name in file_names:
                similar_file_info = file_names[base_name]
                if similar_file_info != file_info:
                    if abs(file_info[1] - similar_file_info[1]) == 0:
                        duplicates.append((file_info, similar_file_info, "same_size"))
                    elif abs(file_info[1] - similar_file_info[1]) < 1024:  # Size difference less than 1KB
                        if file_info[2] > similar_file_info[2]:
                            duplicates.append((file_info, similar_file_info, "close_size"))
                            file_names[base_name] = file_info  # Keep the latest version
                        else:
                            duplicates.append((similar_file_info, file_info, "close_size"))
            else:
                file_names[base_name] = file_info

    progress_window.destroy()

    listbox.delete(0, END)
    for current_file_info, similar_file_info, match_type in duplicates:
        file_name = os.path.basename(current_file_info[0])
        file_path = current_file_info[0]
        file_size = current_file_info[1]
        similar_file_name = os.path.basename(similar_file_info[0])
        similar_file_size = similar_file_info[1]
        list_item = f"{file_name} | {file_path} | {file_size} bytes | {similar_file_name}, {similar_file_size} bytes"

        if match_type == "exact":
            listbox.insert(END, list_item)
        elif match_type == "same_size":
            listbox.insert(END, list_item)
            listbox.itemconfig(END, {'fg': 'blue'})
        elif match_type == "close_size":
            listbox.insert(END, list_item)
            listbox.itemconfig(END, {'fg': 'green'})

    if not duplicates:
        messagebox.showinfo("No Duplicates Found", "No duplicate files found in the selected folder.")
    else:
        delete_button.config(state=tk.NORMAL)


def hash_file(file_path):
    hash_algo = hashlib.md5()
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            hash_algo.update(chunk)
    return hash_algo.hexdigest()


def delete_selected_files():
    selected_items = listbox.curselection()
    if not selected_items:
        messagebox.showwarning("No Selection", "No files selected for deletion.")
        return

    deleted_files = []
    total_freed_space = 0

    for index in selected_items[::-1]:
        file_info = listbox.get(index).split(" | ")[1]
        try:
            file_size = os.path.getsize(file_info)
            os.remove(file_info)
            total_freed_space += file_size
            deleted_files.append(file_info)
            listbox.delete(index)
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting file {file_info}: {e}")

    if listbox.size() == 0:
        delete_button.config(state=tk.DISABLED)

    show_deletion_summary(deleted_files, total_freed_space)


def show_deletion_summary(deleted_files, total_freed_space):
    summary_window = Toplevel(root)
    summary_window.title("Deletion Summary")

    summary_label = Label(summary_window, text="Deleted Files:")
    summary_label.pack(pady=10)

    summary_listbox = Listbox(summary_window, width=100, height=20)
    summary_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    for file in deleted_files:
        summary_listbox.insert(END, file)

    freed_space_label = Label(summary_window, text=f"Total Freed Space: {total_freed_space / (1024 * 1024):.2f} MB")
    freed_space_label.pack(pady=10)


def search_files():
    keyword = search_entry.get().lower()
    if not keyword:
        messagebox.showwarning("No Keyword", "Please enter a keyword to search.")
        return

    listbox.delete(0, END)

    for root_dir, _, files in os.walk(folder_entry.get()):
        for file in files:
            if keyword in file.lower():
                file_path = os.path.join(root_dir, file)
                file_size = os.path.getsize(file_path)
                listbox.insert(END, f"{file} | {file_path} | {file_size} bytes")
                listbox.itemconfig(END, {'fg': 'black'})


# Create the main window
root = tk.Tk()
root.title("Duplicate File Finder")

# Create and place the folder selection widgets
folder_label = tk.Label(root, text="Select Folder:")
folder_label.grid(row=0, column=0, padx=10, pady=10)

folder_entry = tk.Entry(root, width=50)
folder_entry.grid(row=0, column=1, padx=10, pady=10)

folder_button = tk.Button(root, text="Browse", command=select_folder)
folder_button.grid(row=0, column=2, padx=10, pady=10)

# Create a frame for the listbox and scrollbar
frame = tk.Frame(root)
frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

# Create and place the listbox to display duplicate files
listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE, width=100, height=20)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create and place the vertical scrollbar
v_scrollbar = Scrollbar(frame, orient=tk.VERTICAL)
v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Create and place the horizontal scrollbar
h_scrollbar = Scrollbar(root, orient=tk.HORIZONTAL)
h_scrollbar.grid(row=2, column=0, columnspan=3, sticky=tk.EW)

# Attach the scrollbars to the listbox
listbox.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
v_scrollbar.config(command=listbox.yview)
h_scrollbar.config(command=listbox.xview)

# Create and place the delete button
delete_button = tk.Button(root, text="Delete Selected Files", command=delete_selected_files, state=tk.DISABLED)
delete_button.grid(row=4, column=0, columnspan=3, pady=10)

# Create and place the search widgets
search_label = tk.Label(root, text="Search Keyword:")
search_label.grid(row=3, column=0, padx=10, pady=10)

search_entry = Entry(root, width=50)
search_entry.grid(row=3, column=1, padx=10, pady=10)

search_button = Button(root, text="Search", command=search_files)
search_button.grid(row=3, column=2, padx=10, pady=10)

# Run the main event loop
root.mainloop()
