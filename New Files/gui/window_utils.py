import tkinter as tk
from tkinter import filedialog

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_DIM = f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}" # 800x600
FONT = "Arial"
FONT_SIZE = 14

def add_placeholder(entry, placeholder_text):
    """
    Adds placeholder functionality to a tkinter Entry widget.
    
    Parameters:
        entry (tk.Entry): The Entry widget to add the placeholder to.
        placeholder_text (str): The placeholder text to display.
    """
    def on_focus_in(event):
        if entry.get() == placeholder_text:
            entry.delete(0, tk.END)  # Remove placeholder
            entry.config(fg="white")  # Set text color to black

    def on_focus_out(event):
        if entry.get() == "":  # If empty, restore placeholder
            entry.insert(0, placeholder_text)
            entry.config(fg="white")

    # Initialize placeholder
    entry.insert(0, placeholder_text)  # Set placeholder text
    entry.config(fg="white")  # Set placeholder text color
    entry.bind("<FocusIn>", on_focus_in)  # Bind focus-in event
    entry.bind("<FocusOut>", on_focus_out)  # Bind focus-out event

def setup_close_behavior(window, root):
    """
    Sets up behavior for the close button (WM_DELETE_WINDOW) on a secondary window.
    
    Parameters:
        window (tk.Toplevel): The secondary window.
        root (tk.Tk): The main application window.
    """
    def on_close():
        root.deiconify()  # Show the main window
        window.destroy()  # Destroy the current window

    window.protocol("WM_DELETE_WINDOW", on_close)

def add_back_to_main_button(window, root, pos_x, pos_y, button_width, button_height):
    """
    Adds a "Go to Main Menu" button to a tkinter window.
    
    Parameters:
        window (tk.Toplevel): The secondary window where the button will be added.
        root (tk.Tk): The main application window.
        pos_x (int): The x position of the button
        pos_y (int): The y position of the button
        button_width (int): The width of the button
        button_height (int): The height of the button
    """
    def go_back():
        window.destroy()  # Close the current window
        root.deiconify()  # Show the main window

    button = tk.Button(window, text="Go to Main Menu", command=go_back, font=(FONT, FONT_SIZE))
    button.place(x=pos_x, y=pos_y, width=button_width, height=button_height)

def add_folder_selector(parent, button_text, pos_x, pos_y, button_width, button_height):
    """
    Adds a folder selector button and a label to display the selected folder.

    Parameters:
        parent (tk.Toplevel): The window where the button will be added.
        button_text (str): The default text for the folder selector button.
        pos_x (int): The x position of the button.
        pos_y (int): The y position of the button.
        button_width (int): The width of the button.
        button_height (int): The height of the button.

    Returns:
        tk.StringVar: A StringVar that holds the selected folder path.
    """
    folder_var = tk.StringVar()
    folder_var.set("No folder selected")  # Default message
    current_text = tk.StringVar()  # To track the button's current state
    current_text.set(button_text)

    def select_folder():
        folder_path = filedialog.askdirectory()  # Open folder selection dialog
        if folder_path:
            folder_var.set(folder_path)  # Update the folder path
            folder_name = folder_path if len(folder_path) <= 24 else folder_path[len(folder_path) - 24:]
            current_text.set(folder_name)  # Update button text to show folder name
            button.config(text=folder_name)

    def on_hover(event):
        button.config(text="Click to select a folder")

    def on_leave(event):
        button.config(text=current_text.get())  # Restore the current button text

    # Create button
    button = tk.Button(parent, text=button_text, command=select_folder, font=(FONT, FONT_SIZE))
    button.place(x=pos_x, y=pos_y, width=button_width, height=button_height)

    # Bind hover events
    button.bind("<Enter>", on_hover)
    button.bind("<Leave>", on_leave)

    return folder_var


def add_file_selector(parent, button_text, pos_x, pos_y, button_width, button_height):
    """
    Adds a file selector button and a label to display the selected file.

    Parameters:
        parent (tk.Toplevel): The window where the button will be added.
        button_text (str): The default text for the file selector button.
        pos_x (int): The x position of the button.
        pos_y (int): The y position of the button.
        button_width (int): The width of the button.
        button_height (int): The height of the button.

    Returns:
        tk.StringVar: A StringVar that holds the selected file path.
    """
    file_var = tk.StringVar()
    file_var.set("No file selected")  # Default message
    current_text = tk.StringVar()  # To track the button's current state
    current_text.set(button_text)

    def select_file():
        file_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[("Matrix files", "*.mtx"), ("All files", "*.*")]
        )
        if file_path:
            file_var.set(file_path)  # Update the selected file path
            file_name = file_path.split("/")[-1]  # Extract file name from the path
            new_text = file_name if len(file_name) <= 30 else file_name[:27] + "..."
            current_text.set(new_text)  # Update button text to show file name
            button.config(text=new_text)

    def on_hover(event):
        button.config(text="Click to select a file")

    def on_leave(event):
        button.config(text=current_text.get())  # Restore the current button text

    # Create button
    button = tk.Button(parent, text=button_text, command=select_file, font=(FONT, FONT_SIZE))
    button.place(x=pos_x, y=pos_y, width=button_width, height=button_height)

    # Bind hover events
    button.bind("<Enter>", on_hover)
    button.bind("<Leave>", on_leave)

    return file_var