# Work Clock App
from datetime import datetime, timedelta
import time
import customtkinter as ctk
from PIL import Image

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Work Clock")
        self.geometry("300x200")
        self.grid_columnconfigure((0, 1, 2), weight=1)
        #self.grid_rowconfigure(0, weight=1)

        # Load icon
        gear_image = ctk.CTkImage(
        light_image=Image.open("icons\Gear-icon-black.png"),
        dark_image=Image.open("icons\Gear-icon-white.png"),
        size=(20, 20)
        )

        data = self.load_data()
        self._data = []
        for x in data:
            self._data.append(x.replace("\n", ""))
        self.date = datetime.now().strftime("%d.%m.%Y")
        if self._data[2] != self.date:
            box = ctk.CTkInputDialog(text="Enter work start time")
            _s_time = box.get_input()
            self.start_time = datetime.strptime(_s_time, "%H:%M")
            data[2] = self.date + "\n"
            data[3] = _s_time + "\n"
            data[4] = datetime.strftime(self.start_time + timedelta(hours=int(data[1])), "%H:%M")
            f = open("data.txt",'w')
            f.writelines(data)
            f.close()
        else:
            self.start_time = datetime.strptime(self._data[3], "%H:%M")
        print(self.start_time)
        self.end_time = self.start_time + timedelta(hours=int(self._data[1]))
        
        #Settings button
        self.setting_Btn = ctk.CTkButton(self, text="", image=gear_image, width=20, height=20, fg_color="transparent", corner_radius=8, command=self.button_callback)
        self.setting_Btn.grid(row=0, column=0, padx=0, pady=0, sticky="w")
        #Big Clock
        self.clock_Lbl = ctk.CTkLabel(self, text="", font=("Old English Text MT", 60))
        self.clock_Lbl.grid(row=1, column=0, padx=0, pady=0, sticky="ew", columnspan=3)
        #Grettings
        self.greetings_Lbl = ctk.CTkLabel(self, text="", font=("Old English Text MT", 30), text_color="#FFFFFF")
        self.greetings_Lbl.configure(text="Greetings " + self._data[0])
        self.greetings_Lbl.grid(row=2, column=0, padx=0, pady=0, sticky="ew", columnspan=3)
        #Work time
        self.remainingTime_Lbl = ctk.CTkLabel(self, text="", font=("Old English Text MT", 30), text_color="#FFFFFF")
        self.remainingTime_Lbl.grid(row=3, column=0, padx=0, pady=0, sticky="ew", columnspan=3)
        #ProgresssBar
        self.time_PB = ctk.CTkProgressBar(self, height=15, corner_radius=7, progress_color="#680000", orientation="horizontal")
        self.time_PB.grid(row=4, column=0, padx=(15,15), pady=(5,5), sticky="ew", columnspan=3)
        self.time_PB.set(0) #Initial value 0-1
        #
        self.update_time()
    
    def load_data(self):
        try:
            f = open("data.txt")
            data = f.readlines()
            f.close()
        except:
            print("Error Loading data.\nPelase enter info")
            f = open("data.txt", 'x')
            data = ['name\n','9\n','22.04.2026\n','8:00\n','17:00']
            f.write(data)
            f.close
        return data
        
    def button_callback(self):
        print("button pressed")
        SettingsWindow(self)
        
    
    def update_time(self):
        current_time = datetime.now().strftime("%H:%M")
        #remaining_time = self.end_time - timedelta(hours=datetime.now().hour, minutes=datetime.now().minute)
        elapsed_time = datetime.now() - timedelta(hours=self.start_time.hour, minutes=self.start_time.minute)
        #print(elapsed_time)
        total_min = 60 * int(self._data[1])
        #remain_min = int(remaining_time.hour)*60 + int(remaining_time.minute)
        elapsed_min = elapsed_time.hour*60 + elapsed_time.minute
        #progress = 100 - int(remain_min*100/total_min)
        _progress =  int(elapsed_min*100/total_min) if int(elapsed_min*100/total_min) <= 100 else 100
        #print(remaining_time)
        self.clock_Lbl.configure(text=current_time)
        self.remainingTime_Lbl.configure(text= str(_progress) + "%")
        self.time_PB.set(_progress/100)
        self.after(1000, self.update_time)

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Settings")
        self.geometry("250x300")
        self.grid_columnconfigure((0,1,2), weight=1)
        #self.transient(master) # keeps it linked to main window
        self.grab_set() #blocks interaction with main window

        self.name_Lbl = ctk.CTkLabel(self, text="Name:", text_color="#FFFFFF" )
        self.name_Lbl.grid(row=0, column=0, padx=0, pady=0, sticky="w", columnspan=3)
        self.name_Entry = ctk.CTkEntry(self, placeholder_text="Your name")
        self.name_Entry.grid(row=1, column=0, padx=(5,5), sticky="ew", columnspan=3)

        self.hours_Lbl = ctk.CTkLabel(self, text="Daily work hours:", text_color="#FFFFFF" )
        self.hours_Lbl.grid(row=2, column=0, padx=0, pady=0, sticky="w", columnspan=3)
        self.hours_Entry = ctk.CTkEntry(self, placeholder_text="")
        self.hours_Entry.grid(row=3, column=0, padx=(5,5), sticky="ew", columnspan=3)

        self.look_Lbl = ctk.CTkLabel(self, text="Dark mode:", height=20,)
        self.look_Lbl.grid(row=4, column=0, sticky="w", columnspan=2)
        self.switch_var = ctk.IntVar(value=1) #default switch state
        self.look_swt = ctk.CTkSwitch(self, text="", command=self.swt_theme_fnc, variable=self.switch_var, onvalue=1, offvalue=0)
        self.look_swt.grid(row=4, column=2, sticky="e")

        self.ok_Btn = ctk.CTkButton(self, text="Ok", width=40, height=30, fg_color="#6449DD", corner_radius=15, text_color="#FFFFFF", command=self.set_Callback)
        self.ok_Btn.grid(row=5, column=1, padx=10, pady=0, sticky="ew")
        self.cancel_Btn = ctk.CTkButton(self, text="Cancel", width=40, height=30, fg_color="#6449DD", corner_radius=15, text_color="#FFFFFF", command=self.cancel_Callback)
        self.cancel_Btn.grid(row=5, column=2, padx=5, pady=0, sticky="ew")
    
    def set_Callback(self):
        name = self.name_Entry.get()
        self.name_Entry.delete(0, END)
        if name != "":
            print(name)
        else:
            print("No name")
    
    def cancel_Callback(self):
        pass

    def swt_theme_fnc(self):
        pass

app = App()
app.mainloop()