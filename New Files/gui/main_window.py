import tkinter as tk
from gui.window_utils import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_DIM
from gui.create_window import open_create_window
from gui.generate_window import open_generate_window

# Create the main window
root = tk.Tk()
root.geometry(WINDOW_DIM)
root.resizable(False, False)
root.title("Main Menu")

# Define button dimensions
button_width = 400
button_height = 50

# Calculate x-coordinate for centering buttons
center_x = (WINDOW_WIDTH - button_width) // 2

# Button functionalities
def switch_create_window():
    root.withdraw()  # Hide main window
    open_create_window(root)

def switch_generate_window():
    root.withdraw()  # Hide main window
    open_generate_window(root)

# Proper close behavior to terminate the application
def on_close():
    root.destroy()  # Destroy the Tkinter window
    root.quit()     # Exit the mainloop

# Create buttons
button1 = tk.Button(root, text="Create new matrices", command=switch_create_window)
button2 = tk.Button(root, text="Generate matrices with Neural Network", command=switch_generate_window)
button3 = tk.Button(root, text="Close", command=on_close)

button1.place(x=center_x, y=360, width=button_width, height=button_height)
button2.place(x=center_x, y=430, width=button_width, height=button_height)
button3.place(x=center_x, y=500, width=button_width, height=button_height)

# Bind the window close button to the on_close function
root.protocol("WM_DELETE_WINDOW", on_close)

# Run the application
root.mainloop()