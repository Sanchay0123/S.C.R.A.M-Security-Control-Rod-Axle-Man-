#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
import time
import sys

def start_fake_update():
    root = tk.Tk()
    
    # CONFIGURE THE DECEPTION
    # Fullscreen, black background, no borders
    root.attributes('-fullscreen', True)
    root.configure(background='black')
    
    # Trap the mouse and keyboard (Basic level)
    root.bind("<Escape>", lambda e: None) 
    root.config(cursor="none") # Hide the mouse cursor

    # HEADER
    lbl_title = tk.Label(root, text="System Critical Update in Progress", 
                         font=("Courier", 24, "bold"), fg="white", bg="black")
    lbl_title.pack(pady=(200, 20))
    
    # SUBTITLE
    lbl_subtitle = tk.Label(root, text="Do not turn off your computer. This may take a moment...", 
                            font=("Courier", 14), fg="gray", bg="black")
    lbl_subtitle.pack(pady=10)

    # PROGRESS BAR STYLING
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("red.Horizontal.TProgressbar", 
                    foreground='red', 
                    background='red', 
                    troughcolor='#333333',
                    bordercolor='black',
                    lightcolor='red',
                    darkcolor='red')
    
    progress = ttk.Progressbar(root, style="red.Horizontal.TProgressbar", 
                               orient="horizontal", length=800, mode="determinate")
    progress.pack(pady=50)
    
    # THE SIMULATION LOOP
    def simulate_progress():
        current_val = 0
        # Slow crawl to 100% (takes about 90 seconds)
        while current_val < 100:
            time.sleep(0.9) 
            current_val += 1
            progress['value'] = current_val
            root.update_idletasks()
            
    # Start simulation after 1 second
    root.after(1000, simulate_progress)
    root.mainloop()

if __name__ == "__main__":
    start_fake_update()
