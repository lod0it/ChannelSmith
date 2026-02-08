# GUI Components - Simple Reference

**For:** Non-developers who need to iterate on the GUI

---

## Core tkinter Widgets

All GUI built from these simple building blocks:

### Frame (Container)
Groups widgets together in a box.

```python
import tkinter as tk

root = tk.Tk()
container = tk.Frame(root, bg="white", padx=10, pady=10)
container.pack()
```

**Common options:**
- `bg` - background color (hex: `"#ffffff"` or name: `"white"`)
- `padx`, `pady` - internal padding
- `relief` - border style (`"flat"`, `"raised"`, `"sunken"`)
- `width`, `height` - size in pixels

---

### Label (Text)
Displays static text.

```python
label = tk.Label(container, text="Template", font=("Arial", 12))
label.pack()
```

**Common options:**
- `text` - display text
- `font` - tuple (name, size): `("Arial", 12)`, `("Courier", 10, "bold")`
- `fg` - text color
- `bg` - background color

---

### Button (Clickable)
Triggers action when clicked.

```python
def on_click():
    print("Clicked!")

btn = tk.Button(container, text="Click Me", command=on_click)
btn.pack()
```

**Common options:**
- `text` - button label
- `command` - function to call on click
- `bg`, `fg` - colors
- `width`, `height` - size
- `state` - `"normal"` or `"disabled"` (grayed out)

---

### Entry (Text Input)
Single-line text input.

```python
entry = tk.Entry(container, width=30)
entry.pack()

# Get value
value = entry.get()

# Set value
entry.insert(0, "default text")
```

---

### Listbox (Selection List)
Pick one item from many.

```python
listbox = tk.Listbox(container, height=5)
listbox.insert(0, "Option 1")
listbox.insert(1, "Option 2")
listbox.pack()

# Get selected
selected = listbox.get(listbox.curselection())
```

---

### Canvas (Draw Area)
Display images or draw shapes.

```python
canvas = tk.Canvas(container, width=300, height=300, bg="gray")
canvas.pack()

# Display PIL Image
from PIL import ImageTk
photo = ImageTk.PhotoImage(pil_image)
canvas.create_image(150, 150, image=photo)
canvas.image = photo  # Keep reference!
```

---

### LabelFrame (Grouped Widgets)
Frame with a label border.

```python
frame = tk.LabelFrame(root, text="Image Options")
frame.pack()

label = tk.Label(frame, text="Select Image:")
label.pack()
```

---

### Notebook (Tabs)
Multiple tabs/pages.

```python
from tkinter import ttk

notebook = ttk.Notebook(root)
notebook.pack()

tab1 = tk.Frame(notebook)
tab2 = tk.Frame(notebook)

notebook.add(tab1, text="Pack")
notebook.add(tab2, text="Unpack")
```

---

## Layout (pack, grid, place)

Three ways to position widgets:

### pack() - Simple stacking
```python
label.pack()              # Top to bottom
label.pack(side="left")   # Left to right
label.pack(fill="x")      # Stretch horizontally
```

**Common options:**
- `side` - `"top"`, `"left"`, `"right"`, `"bottom"`
- `fill` - `"x"` (horizontal), `"y"` (vertical), `"both"`
- `expand` - `True` to grow with window
- `padx`, `pady` - spacing around widget

### grid() - Table layout
```python
label.grid(row=0, column=0)
btn.grid(row=1, column=0)
entry.grid(row=1, column=1)
```

**Better for complex layouts:**
```python
frame.columnconfigure(0, weight=1)  # Column 0 stretches
frame.rowconfigure(0, weight=1)     # Row 0 stretches
```

### place() - Absolute positioning
```python
label.place(x=100, y=50, width=200, height=30)
```

---

## File Dialogs

### Open File
```python
from tkinter import filedialog

path = filedialog.askopenfilename(
    title="Open Image",
    filetypes=[("PNG", "*.png"), ("TGA", "*.tga"), ("All", "*.*")]
)
```

### Save File
```python
path = filedialog.asksaveasfilename(
    defaultextension=".png",
    filetypes=[("PNG", "*.png"), ("TIFF", "*.tiff")]
)
```

### Open Folder
```python
folder = filedialog.askdirectory(title="Select Project Folder")
```

---

## Message Dialogs

### Show Info
```python
from tkinter import messagebox

messagebox.showinfo("Success", "Textures packed successfully!")
```

### Show Error
```python
messagebox.showerror("Error", "Failed to load image: invalid format")
```

### Ask Yes/No
```python
response = messagebox.askyesno("Confirm", "Delete this file?")
if response:
    # Delete...
```

---

## Common Patterns

### Enable/Disable Button
```python
btn = tk.Button(root, text="Pack", state="normal")

# Disable
btn.config(state="disabled")

# Enable
btn.config(state="normal")
```

### Update Label Text
```python
label = tk.Label(root, text="Old text")
label.config(text="New text")
```

### Clear Entry
```python
entry = tk.Entry(root)
entry.delete(0, "end")
```

### Get Multiple Selections from Listbox
```python
listbox = tk.Listbox(root, selectmode="multiple")
selected = [listbox.get(i) for i in listbox.curselection()]
```

---

## Simple App Template

```python
import tkinter as tk
from tkinter import ttk

class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("My App")
        self.geometry("800x600")

        self._build_ui()

    def _build_ui(self):
        # Create widgets
        label = tk.Label(self, text="Hello")
        label.pack()

        btn = tk.Button(self, text="Click", command=self.on_click)
        btn.pack()

    def on_click(self):
        print("Button clicked!")

if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
```

---

## Colors

Use hex colors (`"#RRGGBB"`) or names:

```python
"#ffffff"  # White
"#000000"  # Black
"#FF0000"  # Red
"#4CAF50"  # Green
"#2196F3"  # Blue
```

Or simple names:
```python
"white", "black", "red", "green", "blue", "gray", "lightgray"
```

---

## Fonts

```python
("Arial", 12)              # Arial, size 12
("Arial", 12, "bold")      # Bold
("Arial", 12, "italic")    # Italic
("Courier", 10, "bold italic")  # Both
```

Common fonts: `Arial`, `Courier`, `Times`, `Helvetica`

---

## Common Gotchas

**Forgot to keep image reference:**
```python
# WRONG - image disappears!
canvas.create_image(0, 0, image=ImageTk.PhotoImage(pil_img))

# RIGHT - keep reference
photo = ImageTk.PhotoImage(pil_img)
canvas.create_image(0, 0, image=photo)
canvas.image = photo
```

**Forgot mainloop():**
```python
# App won't start!
root = tk.Tk()
label = tk.Label(root, text="Hi")
label.pack()
# WRONG - missing:
# root.mainloop()
```

**Trying to use pack() and grid() together:**
```python
# WRONG - will break!
label.pack()
btn.grid(row=0, column=0)

# RIGHT - use one or the other
label.pack()
btn.pack()
```

---

## Sizing Widgets

### Auto-size to content
```python
label = tk.Label(root, text="This sizes itself")
label.pack()
```

### Fixed size
```python
btn = tk.Button(root, text="Click", width=20, height=2)
btn.pack()
```

### Stretch to fill
```python
frame = tk.Frame(root, bg="white")
frame.pack(fill="both", expand=True)
```

---

## Quick Reference

| Widget | Use |
|--------|-----|
| Frame | Container |
| Label | Static text |
| Button | Clickable action |
| Entry | Text input |
| Listbox | Pick from list |
| Canvas | Show images |
| LabelFrame | Grouped widgets |
| Notebook | Multiple tabs |

---

## Next Steps

For more:
- Read `GUI_STRUCTURE.md` - how components fit together
- Look at actual code in `channelsmith/gui/` - examples
- Python tkinter docs: https://docs.python.org/3/library/tkinter.html
