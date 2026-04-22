# Work Clock App
from datetime import datetime, timedelta
import time
import customtkinter as ctk
from PIL import Image

name = ""
starting_time = []

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Work Clock")
        self.geometry("300x200")
        self.grid_columnconfigure((0, 1), weight=1)

        # Load icon
        gear_image = ctk.CTkImage(
        light_image=Image.open("Gear-icon-black.png"),
        dark_image=Image.open("Gear-icon-white.png"),
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
            f = open("data.txt",'w')
            f.writelines(data)
            f.close()
        else:
            self.start_time = datetime.strptime(self._data[3], "%H:%M")
        print(self.start_time)
        self.end_time = self.start_time + timedelta(hours=int(self._data[1]))
        
        #Settings button
        self.setting_Btn = ctk.CTkButton(self, text="", image=gear_image, width=25, height=25, fg_color="transparent", corner_radius=8, command=self.button_callback)
        self.setting_Btn.grid(row=0, column=0, padx=0, pady=0, sticky="w")
        #Big Clock
        self.clock_Lbl = ctk.CTkLabel(self, text="", font=("Old English Text MT", 60), text_color="#FFFFFF")
        self.clock_Lbl.grid(row=1, column=0, padx=0, pady=0, sticky="ew", columnspan=3)
        #Grettings
        self.greetings_Lbl = ctk.CTkLabel(self, text="", font=("Old English Text MT", 30), text_color="#FFFFFF")
        self.greetings_Lbl.configure(text="Greetings " + self._data[0])
        self.greetings_Lbl.grid(row=2, column=0, padx=0, pady=0, sticky="ew", columnspan=3)
        #Work time
        self.remainingTime_Lbl = ctk.CTkLabel(self, text="", font=("Old English Text MT", 30), text_color="#FFFFFF")
        self.remainingTime_Lbl.grid(row=3, column=0, padx=0, pady=0, sticky="ew", columnspan=3)
        #self.checkbox_1.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")
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
    
    def update_time(self):
        current_time = datetime.now().strftime("%H:%M")
        remaining_time = self.end_time - timedelta(hours=datetime.now().hour, minutes=datetime.now().minute)
        total_min = 60 * int(self._data[1])
        remain_min = int(remaining_time.hour)*60 + int(remaining_time.minute)
        progress = 100 - int(remain_min*100/total_min)
        print(remaining_time)
        self.clock_Lbl.configure(text=current_time)
        self.remainingTime_Lbl.configure(text= str(progress) + "%")
        self.after(1000, self.update_time)



app = App()
app.mainloop()