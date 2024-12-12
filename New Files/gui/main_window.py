import tkinter as tk
from gui.window_utils import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_DIM
from gui.create_window import open_create_window
from gui.generate_window import open_generate_window

# Create the main window
root = tk.Tk()
root.geometry(WINDOW_DIM)
root.resizable(False, False)
root.title("Main Menu")

# Define button dimensions in pixels
button_width = 400  # Width of the button in pixels
button_height = 50  # Height of the button in pixels

# Calculate the x-coordinate for centering the buttons
center_x = (WINDOW_WIDTH - button_width) // 2

# Pass the root to other windows
def switch_create_window():
    root.withdraw()  # Hide the main window
    open_create_window(root)

def switch_generate_window():
    root.withdraw()  # Hide the main window
    open_generate_window(root)

# Create buttons
button1 = tk.Button(root, text="Create new matrices", command=switch_create_window)
button2 = tk.Button(root, text="Generate matrices with Neural Network", command=switch_generate_window)
button3 = tk.Button(root, text="Close", command=root.destroy)

button1.place(x=center_x, y=360, width=button_width, height=button_height)
button2.place(x=center_x, y=430, width=button_width, height=button_height)
button3.place(x=center_x, y=500, width=button_width, height=button_height)

# Run the application
root.mainloop()