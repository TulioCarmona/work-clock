# Work Clock App
from datetime import datetime, timedelta
import time
import customtkinter as ctk
from PIL import Image
import json
from pathlib import Path

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Work Clock")
        self.geometry("300x200")
        self.grid_columnconfigure((0, 1, 2), weight=1)
        #self.grid_rowconfigure(0, weight=1)

        #Load path
        BASE_DIR = Path(__file__).resolve().parent
        self.CONFIG_FILE = BASE_DIR / "config.json"
        #self.ICONS_DIR = BASE_DIR / "icons"

        # Load icon
        b_img_path = Path("icons") / "Gear-icon-black.png"
        w_img_path = Path("icons") / "Gear-icon-white.png"
        self.gear_image = ctk.CTkImage(
        light_image=Image.open(b_img_path),
        dark_image=Image.open(w_img_path),
        size=(20, 20)
        )

        with open(self.CONFIG_FILE, "r") as f:
            self.data = json.load(f)

        self.date = datetime.now().strftime("%d.%m.%Y")
        if self.data["last_run_date"] != self.date:
            box = ctk.CTkInputDialog(text="Enter work start time")
            _s_time = box.get_input()
            self.start_time = datetime.strptime(_s_time, "%H:%M")
            self.data["last_run_date"] = self.date
            self.data["start_time"] = datetime.strftime(self.start_time, "%H:%M")
            self.data["end_time"] = datetime.strftime(self.start_time + timedelta(hours=int(self.data["work_hours"])), "%H:%M")
            with open(self.CONFIG_FILE, "w") as f:
                json.dump(self.data, f, indent=4)
        else:
            self.start_time = datetime.strptime(self.data["start_time"], "%H:%M")
        print(self.start_time)
        self.end_time = self.start_time + timedelta(hours=int(self.data["work_hours"]))
        
        #Settings button
        self.setting_Btn = ctk.CTkButton(self, text="", image=self.gear_image, width=20, height=20, fg_color="transparent", corner_radius=8, command=self.button_callback)
        self.setting_Btn.grid(row=0, column=0, padx=0, pady=0, sticky="w")
        #Big Clock
        self.clock_Lbl = ctk.CTkLabel(self, text="", font=("Old English Text MT", 60))
        self.clock_Lbl.grid(row=1, column=0, padx=0, pady=0, sticky="ew", columnspan=3)
        #Grettings
        self.greetings_Lbl = ctk.CTkLabel(self, text="", font=("Old English Text MT", 30), text_color="#FFFFFF")
        self.greetings_Lbl.configure(text="Greetings " + self.data["user_name"])
        self.greetings_Lbl.grid(row=2, column=0, padx=0, pady=0, sticky="ew", columnspan=3)
        #Work time
        self.remainingTime_Lbl = ctk.CTkLabel(self, text="", font=("Old English Text MT", 30), text_color="#FFFFFF")
        self.remainingTime_Lbl.grid(row=3, column=0, padx=0, pady=0, sticky="ew", columnspan=3)
        #ProgresssBar
        self.time_PB = ctk.CTkProgressBar(self, height=15, corner_radius=8, progress_color="#680000", orientation="horizontal")
        self.time_PB.grid(row=4, column=0, padx=(15,15), pady=(5,5), sticky="ew", columnspan=3)
        self.time_PB.set(0) #Initial value 0-1
        #
        self.update_time()
        
    def button_callback(self):
        SettingsWindow(self)
        print("window closed...")
        
    
    def update_time(self):
        current_time = datetime.now().strftime("%H:%M")
        #remaining_time = self.end_time - timedelta(hours=datetime.now().hour, minutes=datetime.now().minute)
        elapsed_time = datetime.now() - timedelta(hours=self.start_time.hour, minutes=self.start_time.minute)
        #print(elapsed_time)
        total_min = 60 * int(self.data["work_hours"])
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
        #self.geometry("230x300")
        self.grid_columnconfigure((0,1,2,3), weight=1)
        #self.transient(master) # keeps it linked to main window
        self.grab_set() #blocks interaction with main window
        self.resizable(False, False)

        #load data
        BASE_DIR = Path(__file__).resolve().parent
        self.CONFIG_FILE = BASE_DIR / "config.json"
        with open(self.CONFIG_FILE, "r") as f:
            self.data = json.load(f)
        # Load icon
        b_img_path = Path("icons") / "dark-drop.png"
        w_img_path = Path("icons") / "light-drop.png"
        self.drop_image = ctk.CTkImage(
        light_image=Image.open(w_img_path),
        dark_image=Image.open(b_img_path),
        size=(20, 20)
        )

        #Name
        self.name_Lbl = ctk.CTkLabel(self, text="Name:", text_color="#FFFFFF" )
        self.name_Lbl.grid(row=0, column=0, padx=5, pady=0, sticky="w", columnspan=3)
        self.name_Entry = ctk.CTkEntry(self, placeholder_text=self.data["user_name"], height=30)
        self.name_Entry.grid(row=1, column=0, padx=(5,5), sticky="ew", columnspan=4)
        #Work hours
        self.hours_Lbl = ctk.CTkLabel(self, text="Daily work hours:", text_color="#FFFFFF")
        self.hours_Lbl.grid(row=2, column=0, padx=0, pady=0, sticky="w", columnspan=3)
        self.hours_Entry = ctk.CTkEntry(self, placeholder_text=self.data["work_hours"], height=30, width=50)
        self.hours_Entry.grid(row=3, column=0, padx=(5,5), sticky="ew")
        self.mode_var = ctk.IntVar(value=0)
        self.hours_cbx = ctk.CTkCheckBox(self, text="Use fix number of hours", variable=self.mode_var, onvalue=1, offvalue=0,
                                         checkbox_height=20, checkbox_width=20, border_width=2, fg_color="#680000", hover_color="#680000", 
                                         command=self.cbx_callback)
        self.hours_cbx.grid(row=3, column=2,  padx=(5,5), sticky="ew", columnspan=2)
        #Start time
        self.start_time_Lbl = ctk.CTkLabel(self, text="Start time:")
        self.start_time_Lbl.grid(row=4, column=0, padx=0, sticky="w", columnspan=3)
        self.start_h_Entry = ctk.CTkEntry(self, placeholder_text=self.data["start_time"].split(":")[0], width=50, height=30)
        self.start_h_Entry.grid(row=5, column=0, padx=(5,5), sticky="ew")
        self.lbl1 = ctk.CTkLabel(self,text=":", height=30, anchor="center", font=('default',25))
        self.lbl1.grid(row=5, column=1, padx=(2,2))
        self.start_m_Entry = ctk.CTkEntry(self, placeholder_text=self.data["start_time"].split(":")[1], width=50, height=30)
        self.start_m_Entry.grid(row=5, column=2, padx=(5,5), sticky="ew")
        #End time
        self.end_time_Lbl = ctk.CTkLabel(self, text="End time:")
        self.end_time_Lbl.grid(row=6, column=0, padx=0, sticky="w", columnspan=3)
        self.end_h_Entry = ctk.CTkEntry(self, placeholder_text=self.data["end_time"].split(":")[0], width=50, height=30)
        self.end_h_Entry.grid(row=7, column=0, padx=(5,5), sticky="ew")
        self.lbl2 = ctk.CTkLabel(self,text=":", height=30, anchor="center", font=('default',25))
        self.lbl2.grid(row=7, column=1, padx=(2,2))
        self.end_m_Entry = ctk.CTkEntry(self, placeholder_text=self.data["end_time"].split(":")[1], width=50, height=30)
        self.end_m_Entry.grid(row=7, column=2, padx=(5,5), sticky="ew")
        #Appearance
        self.look_Lbl = ctk.CTkLabel(self, text="Dark mode:", height=20,)
        self.look_Lbl.grid(row=8, column=0, pady=(5,5), sticky="w", columnspan=2)
        self.switch_var = ctk.IntVar(value=1) #default switch state
        #self.look_swt = ctk.CTkSwitch(self, text="", command=self.swt_theme_fnc, variable=self.switch_var, onvalue=1, offvalue=0,
        #                              switch_width=40, corner_radius=20, progress_color="#680000")
        #self.look_swt.grid(row=8, column=2, pady=(5,5), sticky="e")
        self.look_Btn = ctk.CTkButton(self, text="", image=self.drop_image, width=30, height=20, fg_color="transparent",corner_radius=10, command=self.swt_theme_fnc)
        self.look_Btn.grid(row=8, column=2, padx=(5,5), pady=(5,5), sticky="ew")

        #self.ok_Btn = ctk.CTkButton(self, text="Ok", width=40, height=30, fg_color="#6449DD", corner_radius=15, text_color="#FFFFFF", command=self.set_Callback)
        self.ok_Btn = ctk.CTkButton(self, text="Ok", width=40, height=30, fg_color="#680000", corner_radius=20, text_color="#FFFFFF", command=self.set_Callback)
        self.ok_Btn.grid(row=9, column=2, padx=10, pady=(0,5), sticky="ew")
        self.cancel_Btn = ctk.CTkButton(self, text="Cancel", width=40, height=30, fg_color="#680000", corner_radius=20, text_color="#FFFFFF", command=self.cancel_Callback)
        self.cancel_Btn.grid(row=9, column=3, padx=5, pady=(0,5), sticky="ew")
    
    def set_Callback(self):
        name = self.name_Entry.get()
        work_hours = self.hours_Entry.get()
        start_time_h = self.start_h_Entry.get()
        start_time_m = self.start_m_Entry.get()
        end_time_h = self.end_h_Entry.get()
        end_time_m = self.end_m_Entry.get()
        mode = self.mode_var.get()
        start_time = start_time_h + ":" + start_time_m
        end_time = end_time_h + ":" + end_time_m
        
        if name != "":
            self.data["user_name"] = name
        if work_hours != '' and int(work_hours) >= 0:
            self.data["work_hours"] = int(work_hours)
        if start_time != ":":
            try:
                st = datetime.strptime(start_time, "%H:%M")
                self.data["start_time"] = datetime.strftime(st, "%H:%M")
            except:
                pass
        if end_time != ":":
            try:
                et = datetime.strptime(end_time, "%H:%M")
                self.data["end_time"] = datetime.strftime(et, "%H:%M")
            except:
                pass
        self.data["time_mode"] = mode

        with open(self.CONFIG_FILE, "w") as f:
            json.dump(self.data, f, indent=4)
        
        self.destroy()
    
    def cancel_Callback(self):
        self.destroy()
    
    def cbx_callback(self):
        if self.mode_var.get() == 1:
            self.end_h_Entry.configure(state="disabled")
            self.end_m_Entry.configure(state="disabled")
        else:
            self.end_h_Entry.configure(state="normal")
            self.end_m_Entry.configure(state="normal")

    def swt_theme_fnc(self):
        theme = self._get_appearance_mode() # 'dark' or 'light'
        if theme == "dark":
            self._set_appearance_mode("light")
            #self.look_Btn.configure(image=self.drop_image)
        else:
            self._set_appearance_mode("dark")
            #self.look_Btn.configure(image=self.drop_image)
        

app = App()
app.mainloop()