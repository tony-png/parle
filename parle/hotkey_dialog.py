import tkinter as tk
from tkinter import messagebox
import keyboard
from .config import Config


class HotkeyDialog:
    def __init__(self):
        self.config = Config()
        self.recording = False
        self.recorded_keys = []
        
        self.root = tk.Tk()
        self.root.title("Change Hotkey")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (200 // 2)
        self.root.geometry(f"400x200+{x}+{y}")
        
        # Current hotkey label
        current = self.config.get('hotkey', 'ctrl+shift+r')
        tk.Label(self.root, text="Current Hotkey:", font=("Arial", 10)).pack(pady=10)
        self.current_label = tk.Label(self.root, text=current.upper().replace('+', ' + '), 
                                      font=("Arial", 12, "bold"))
        self.current_label.pack()
        
        # New hotkey section
        tk.Label(self.root, text="Press your new hotkey combination:", 
                font=("Arial", 10)).pack(pady=(20, 5))
        
        self.hotkey_entry = tk.Entry(self.root, font=("Arial", 12), width=30, 
                                     justify='center', state='readonly')
        self.hotkey_entry.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        self.record_button = tk.Button(button_frame, text="Record Hotkey", 
                                       command=self.toggle_recording, width=15)
        self.record_button.pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Save", command=self.save_hotkey, 
                 width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Cancel", command=self.root.destroy, 
                 width=15).pack(side=tk.LEFT, padx=5)
        
        self.root.bind('<Escape>', lambda e: self.root.destroy())
    
    def toggle_recording(self):
        if not self.recording:
            self.recording = True
            self.recorded_keys = []
            self.record_button.config(text="Stop Recording", bg="red", fg="white")
            self.hotkey_entry.config(state='normal')
            self.hotkey_entry.delete(0, tk.END)
            self.hotkey_entry.insert(0, "Press keys...")
            self.hotkey_entry.config(state='readonly')
            
            # Start listening for keys
            keyboard.hook(self.on_key_event)
        else:
            self.stop_recording()
    
    def stop_recording(self):
        self.recording = False
        keyboard.unhook_all()
        self.record_button.config(text="Record Hotkey", bg="SystemButtonFace", fg="black")
        
        if self.recorded_keys:
            # Format the hotkey
            hotkey = '+'.join(self.recorded_keys)
            self.hotkey_entry.config(state='normal')
            self.hotkey_entry.delete(0, tk.END)
            self.hotkey_entry.insert(0, hotkey.upper().replace('+', ' + '))
            self.hotkey_entry.config(state='readonly')
    
    def on_key_event(self, event):
        if not self.recording:
            return
        
        if event.event_type == 'down':
            key_name = event.name.lower()
            
            # Map common key names
            key_map = {
                'control': 'ctrl',
                'alternate': 'alt',
                'windows': 'win',
                'escape': 'esc',
                'return': 'enter',
                'space': 'space'
            }
            
            key_name = key_map.get(key_name, key_name)
            
            # Add to recorded keys if not already there
            if key_name not in self.recorded_keys:
                self.recorded_keys.append(key_name)
                
                # Update display
                self.hotkey_entry.config(state='normal')
                self.hotkey_entry.delete(0, tk.END)
                self.hotkey_entry.insert(0, ' + '.join(self.recorded_keys).upper())
                self.hotkey_entry.config(state='readonly')
        
        elif event.event_type == 'up':
            # Stop recording after keys are released
            if len(self.recorded_keys) >= 2:
                self.root.after(100, self.stop_recording)
    
    def save_hotkey(self):
        hotkey_display = self.hotkey_entry.get()
        if hotkey_display and hotkey_display != "Press keys...":
            # Convert display format back to keyboard format
            hotkey = '+'.join(self.recorded_keys) if self.recorded_keys else ''
            
            if hotkey:
                self.config.set('hotkey', hotkey)
                messagebox.showinfo("Success", 
                                  f"Hotkey changed to: {hotkey_display}\n\nPlease restart Voice Input for changes to take effect.")
                self.root.destroy()
            else:
                messagebox.showerror("Error", "Please record a valid hotkey combination")
    
    def run(self):
        self.root.mainloop()


def main():
    """Run the hotkey configuration dialog"""
    app = HotkeyDialog()
    app.run()


if __name__ == "__main__":
    main()