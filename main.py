from tkinter import *
from tkinter import ttk
from tkinter.ttk import Combobox
from tkinter import messagebox
import sqlite3

selected_month = ""

colour1 = "#e4d2bb"
colour2 = "#89CFF0"
colour3 = "#65e7ff"
colour4 = "BLACK"

root = Tk()
root.title("Vila Mika Studios Calendar")
root.geometry("560x300")
root.configure(bg=colour1)

style = ttk.Style()
style.theme_use("default")

style.configure("rooms.TButton", 
                background=colour2, 
                foreground=colour4, 
                activebackground=colour3, 
                activeforeground=colour4, 
                highlightthickness=2, 
                highlightbackground=colour2, 
                highlightcolor="WHITE",
                columnspan=1,
                width=10,
                font=("YaHei", 12)
            )

style.configure("other.TButton",
                backround=colour2,
                foreground=colour2,
                activebackground=colour2,
                activeforeground=colour4,
                highlightthickness=2,
                highlightbackground=colour2,
                highlightcolor="WHITE",
                columnspan=1,
                font=("YaHei", 12)
            )

style.configure("TCombobox",
                background=colour2,
                foreground=colour4,
                highlightthickness=2,
                highlightbackground=colour2,
                highlightcolor="WHITE",
            )

conn = sqlite3.connect(".\calendar.db")
c = conn.cursor()

def create_room_buttons(window):
    buttons = []
    c.execute("SELECT COUNT(DISTINCT room) FROM June")
    num_rooms = c.fetchone()[0]

    for i in range(1, num_rooms + 1):
        button = ttk.Button(window, text=f"Room {i}", command=lambda room=i: show_calendar(room), style="rooms.TButton")
        button.grid(column=(i-1)%5, row=(i-1)//5, padx=5, pady=5, sticky="w")
        buttons.append(button)

    return buttons

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    
    x_offset = (window.winfo_screenwidth() - width) // 2
    y_offset = (window.winfo_screenheight() - height) // 2

    window.geometry(f"+{x_offset}+{y_offset}")

def center_calendar(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    
    x_offset = (window.winfo_screenwidth() - width) // 6
    y_offset = (window.winfo_screenheight() - height) // 2

    window.geometry(f"+{x_offset}+{y_offset}")

def show_calendar(room):
    global selected_month

    month_name = selected_month

    if(month_name == ""):
        messagebox.showerror("Error", "Please select a month.")
    else:
        c.execute(f"SELECT * FROM {month_name} WHERE room = ?", (room,))
        record = c.fetchone() 

        calendar_window = Toplevel(root)
        calendar_window.title(f"Calendar for Room {room} in {month_name}")
        calendar_window.configure(bg=colour1)
        center_calendar(calendar_window)

        def day_button_click(month_name, room, day):
            c.execute(f"SELECT day_{day} FROM {month_name} WHERE room = ?", (room,))
            availability = c.fetchone()[0]
            if availability == 0:
                answer = messagebox.askyesno("Change availability and delete note", "Do you want to change the availability of the room?\n This will result in deleting the note.")
                if answer == True:
                    c.execute(f"UPDATE {month_name} SET day_{day} = ? WHERE room = ?", (1 - availability, room))
                    conn.commit()

                    conn_2 = sqlite3.connect("details.db")
                    c_2 = conn_2.cursor()
                    c_2.execute(f"UPDATE {month_name} SET day_{day} = ? WHERE room = ?", ("", room))
                    conn_2.commit()
                    conn_2.close()
                else:
                    messagebox.showinfo("Cancelling", f"Availability for Day {day} not changed.")          
            else:
                c.execute(f"UPDATE {month_name} SET day_{day} = ? WHERE room = ?", (1 - availability, room))
                conn.commit()

            calendar_window.destroy()
            show_calendar(room)

        for j, availability in enumerate(record[1:], start=1):
            color = "green" if availability else "red"
            label = Button(calendar_window, text=f"{j}", bg=color, width=5, height=2, font="YaHei 12", command = lambda day=j: day_button_click(month_name, room, day))
            label.grid(row=1, column=j, padx=5, pady=5)

            note_button = ttk.Button(calendar_window, width=5, text="Note", command=lambda day=j: add_note(month_name, room, day, calendar_window), style="rooms.TButton")
            note_button.grid(row=2, column=j, padx=5, pady=5)

        back_button = Button(calendar_window, background=colour1, foreground=colour4, activebackground=colour2, activeforeground=colour4, highlightthickness=2, highlightbackground=colour2, highlightcolor="WHITE",  text="Back to Main Page", command=calendar_window.destroy)
        back_button.grid(row=3, column=1, columnspan=len(record), pady=10)

def add_note(month_name, room, day, calendar_window):
            conn = sqlite3.connect("details.db")
            c = conn.cursor()
            c.execute(f"SELECT day_{day} FROM {month_name} WHERE room = ?", (room,))
            note = c.fetchone()[0]

            def save_note():
                note_text = note_entry.get()
                
                c.execute(f"UPDATE {month_name} SET day_{day} = ? WHERE room = ?", (note_text, room))
                conn.commit()
                messagebox.showinfo("Note Saved", f"Note added for Day {day}: {note_text}")
               
                note_window.destroy()
                calendar_window.destroy()
                show_calendar(room)
            
            def delete_note():
                c.execute(f"UPDATE {month_name} SET day_{day} = ? WHERE room = ?", ("", room))
                conn.commit()
                messagebox.showinfo("Note Deleted", f"Note for Day {day} deleted.")
                note_window.destroy()
                calendar_window.destroy()
                show_calendar(room)

            def change_note():
                note_window_1 = Toplevel()
                note_window_1.title(f"Add Note for Day {day}")
                
                note_entry = Entry(note_window_1, width=30)
                note_entry.grid(row=0, column=0, padx=10, pady=10)

                def save_note_1():
                    note_text = note_entry.get()
                    
                    c.execute(f"UPDATE {month_name} SET day_{day} = ? WHERE room = ?", (note_text, room))
                    conn.commit()
                    messagebox.showinfo("Note Saved", f"Note added for Day {day}: {note_text}")

                    note_window_1.destroy()

                save_button = Button(note_window_1, text="Save Note", command=save_note_1)
                save_button.grid(row=1, column=0, padx=10, pady=10)
                
                note_window.destroy()

            if note == "" or note is None:
                note_window = Toplevel(calendar_window)
                note_window.title(f"Add Note for Day {day}")
                center_window(note_window)

                note_entry = Entry(note_window, width=30)
                note_entry.grid(row=0, column=0, padx=10, pady=10)

                save_button = Button(note_window, text="Save Note", command=save_note)
                save_button.grid(row=1, column=0, padx=10, pady=10)

            else:
                result = messagebox.askyesno("Note", f"Note for Day {day}: {note}\nDo you want to delete or change this note?")
                if result == True:
                    note_window = Toplevel()
                    note_window.title(f"Note for Day {day}")
                    center_window(note_window)

                    note_label = Label(note_window, text=f"Note for Day {day}: {note}")
                    note_label.grid(row=0, column=0, padx=10, pady=10)

                    change_button = ttk.Button(note_window, text="Change Note", command=lambda: change_note())
                    change_button.grid(row=1, column=0, padx=10, pady=10)

                    delete_button = ttk.Button(note_window, text="Delete Note", command=lambda: delete_note())
                    delete_button.grid(row=2, column=0, padx=10, pady=10)


def add_new_room():
    months = {
        "June": 30,
        "July": 31,
        "August": 31
    }

    c.execute(f"SELECT COUNT(DISTINCT room) FROM June")
    num_rooms = c.fetchone()[0]

    for month_name, num_days in months.items():
        availability = [1 for _ in range(num_days)] 
        values = tuple([num_rooms + 1] + availability)
        c.execute(f"INSERT INTO {month_name} VALUES ({','.join(['?'] * (num_days + 1))})", values)

    conn.commit()

    conn_2 = sqlite3.connect("details.db")
    c_2 = conn_2.cursor()

    for month_name, num_days in months.items():
        details = ["" for _ in range(num_days)]
        values = tuple([num_rooms + 1] + details)
        c_2.execute(f"INSERT INTO {month_name} VALUES ({','.join(['?'] * (num_days + 1))})", values)

    conn_2.commit()

    create_room_buttons(root)

def del_room():
    months = {
        "June": 30,
        "July": 31,
        "August": 31
    }

    conn = sqlite3.connect(".\calendar.db")
    c = conn.cursor()
    c.execute(f"SELECT COUNT(DISTINCT room) FROM June")
    num_room = c.fetchone()[0]

    if num_room == 1:
        messagebox.showerror("Error", "Cannot delete the last room.")
    else:
        confirm_delete = messagebox.askyesno("Delete Room", f"Are you sure you want to delete Room {num_room}?")
        if confirm_delete:
            for month_name in months:
                c.execute(f"DELETE FROM {month_name} WHERE room = ?", (num_room,))
        
            conn.commit()

            conn_2 = sqlite3.connect("details.db")
            c_2 = conn_2.cursor()
            for month_name in months:
                c_2.execute(f"DELETE FROM {month_name} WHERE room = ?", (num_room,))

            conn_2.commit()

            for widget in root.winfo_children():
                if isinstance(widget, ttk.Button) and widget.cget("text").startswith("Room "):
                    widget.destroy()
                    
            create_room_buttons(root)

        else:
            messagebox.showinfo("Delete Room", "Room deletion cancelled.")

def select_room(month):
    global selected_month
    selected_month = month

    room_selection_window = Toplevel(root)
    room_selection_window.title(f"Select Room for {month}")
    
    def on_room_select(room):
        room_selection_window.destroy()
        show_calendar(room, month)

    buttons = create_room_buttons(room_selection_window)

    for i, button in enumerate(buttons, start=1):
        button.config(command=lambda room=i: on_room_select(room))

def select_month(month):
    global selected_month
    selected_month = month

buttons = create_room_buttons(root)

month_label = Label(root, background=colour1, foreground=colour4, font="YaHei 14", text="Month:")
month_label.grid(row=10, column=0, pady=10)

months = ["June", "July", "August"]
month_combobox = ttk.Combobox(root, width=10, font="YaHei 12", values=months, style="TCombobox")
month_combobox.current(0)  
month_combobox.grid(row=10, column=1, pady=10)

select_month_btn = ttk.Button(root, text="Select Month", command=lambda: select_month(month_combobox.get()), style="rooms.TButton")
select_month_btn.grid(row=10, column=2, columnspan=1, pady=10)

add_room_btn = ttk.Button(root, text="Add Room", command=lambda: add_new_room(), style="rooms.TButton")
add_room_btn.grid(row=12, column=0, pady=10)

del_room_btn = ttk.Button(root,text="Delete Room", width=11, command=lambda: del_room(), style="rooms.TButton")
del_room_btn.grid(row=12, column=1, pady=10)

center_window(root)

root.mainloop()