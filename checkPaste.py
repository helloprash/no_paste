import tkinter as tk

def handle_clipboard(event):
    #self.CFnum.delete(0, "end")
    lines = root.clipboard_get().split("\n")

    lines = [eachCF for eachCF in lines if len(eachCF) != 0]
    print(lines)
    print(len(lines))

    if len(lines) == 1:
        CFnum['text'] = lines[-1]

    else:
        for each_line in lines:
            if len(each_line) == 0:
                continue

            each_line = str(each_line)+','
            CFnum['text'] += each_line
            #CFnum.insert('end', str(each_line)+',')
            #CFnum.insert('end', ',')
            print(CFnum.get())

def validate(possible_new_value):
    if re.match(r'^[0-9,]*$', possible_new_value):
        return True
    return False



root = tk.Tk()
root.geometry("468x460")

CF_number = tk.Label(root, text="Complaint Folder:")
CF_number.config(font = ('Helvetica','10','bold'), foreground="#112D25", background="#FFFFFF")

CFnum = tk.Entry(root, validate="key", validatecommand=(validate, '%P'))
CFnum.bind("<<Paste>>", handle_clipboard)
CFnum.focus()
CF_number.pack()
CFnum.place(x=50, y=30, width=400)

root.mainloop()
