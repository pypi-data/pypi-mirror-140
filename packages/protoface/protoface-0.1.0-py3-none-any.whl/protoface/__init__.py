import tkinter as tk
import tkinter.font as tkFont

def create_window(w, h, t, r, icon, parent):
    
    if parent == None:
        window = tk.Tk()      
        screenwidth = window.winfo_screenwidth()
        screenheight = window.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (w, h, (screenwidth - w) / 2, (screenheight - h) / 2)
        window.geometry(alignstr)
    else:
        window = tk.Toplevel(parent)
        window.geometry(str(w)+"x"+str(h))
        
    window.config(bg='white')
    window.title(t) 
    window.resizable(width=r, height=r)
    window.iconbitmap(icon) 
    
    return window

def create_background_image(s, image, parent):
    
    img = tk.PhotoImage(file = image)
    img = img.subsample(2) 
    background_label = tk.Label(parent, image=img, bg = 'white')
    background_label.image = img
    background_label.place(x=0, y=70, relwidth=1, relheight=1)            

def create_label(c, f_size, x, y, w, h, t, win):
    
    label  = tk.Label(win)
    label["font"] = tkFont.Font(family='Helvetica',size=f_size)
    label["bg"] = "#ffffff"
    label["fg"] = c
    label["justify"] = "right"
    label["anchor"] = "w"
    label["text"] = t
    label.place(x=x,y=y,width=w,height=h)
    
def create_mutable_label(c, f_size, x, y, w, h, t, win):
    
    label  = tk.Label(win)
    label["font"] = tkFont.Font(family='Helvetica',size=f_size)
    label["bg"] = "#ffffff"
    label["fg"] = c
    label["justify"] = "right"
    label["anchor"] = "w"
    label["text"] = t
    label.place(x=x,y=y,width=w,height=h)

def create_button(c, f, x, y, w, h, t, fun, win):
    
    button = tk.Button(win)
    button["bg"] = c
    button["font"] = tkFont.Font(family='Helvetica',size=f)
    button["fg"] = "#ffffff"
    button["justify"] = "center"
    button["text"] = t
    button.place(x=x,y=y,width=w,height=h)
    button["command"] = fun

def create_entry(c, f, x, y, w, h, win):
    
    v = tk.StringVar()
    v.set("")
    
    entry = tk.Entry(win)
    entry["bg"] = c
    entry["font"] = tkFont.Font(family='Helvetica',size=f)
    entry["textvariable"] = v
    entry.place(x=x,y=y,width=w,height=h)

    return v