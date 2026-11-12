import threading
import time
import tkinter as tk
from tkinter import messagebox, scrolledtext
from pynput.keyboard import Controller, Key
import pynput.keyboard as pynput_keyboard

class AutoTyperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Floating Auto-Typer")
        self.root.geometry("450x480")
        self.root.attributes('-topmost', True)  # Keeps window always on top
        
        self.keyboard = Controller()
        self.is_typing = False
        
        # Global background listener for emergency stop (ESC key)
        self.listener = pynput_keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        
        self.create_widgets()

    def create_widgets(self):
        # Title
        tk.Label(self.root, text="Auto-Typer Utility", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Text input area
        tk.Label(self.root, text="Paste your document text below:").pack(anchor="w", padx=15)
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=50, height=14)
        self.text_area.pack(padx=15, pady=5)
        
        # Speed control frame
        speed_frame = tk.Frame(self.root)
        speed_frame.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(speed_frame, text="Typing Speed (Chars/sec):").pack(side=tk.LEFT)
        self.speed_spin = tk.Spinbox(speed_frame, from_=1, to=100, width=8)
        self.speed_spin.delete(0, tk.END)
        self.speed_spin.insert(0, "30")  # Default 30 characters per second
        self.speed_spin.pack(side=tk.LEFT, padx=10)
        
        # Status Label
        self.status_label = tk.Label(self.root, text="Status: Ready (Press ESC anytime to stop)", fg="blue")
        self.status_label.pack(pady=5)
        
        # Buttons Frame
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        self.start_btn = tk.Button(btn_frame, text="Start (3s Countdown)", bg="#2e7d32", fg="white", font=("Arial", 10, "bold"), command=self.start_countdown_thread)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(btn_frame, text="Stop", bg="#c62828", fg="white", font=("Arial", 10, "bold"), command=self.stop_typing, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

    def on_press(self, key):
        # Emergency abort via ESC key
        if key == Key.esc and self.is_typing:
            self.stop_typing()

    def start_countdown_thread(self):
        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showerror("Error", "Please paste or type text into the box first!")
            return
        
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.is_typing = True
        
        # Run countdown and typing in a background thread to keep UI responsive
        threading.Thread(target=self.run_countdown_and_type, args=(text,), daemon=True).start()

    def run_countdown_and_type(self, text):
        try:
            cps = int(self.speed_spin.get())
            delay = 1.0 / max(cps, 1)
        except ValueError:
            delay = 1.0 / 30

        # 3-Second Countdown (gives you time to click into your browser text field)
        for i in range(3, 0, -1):
            if not self.is_typing:
                break
            self.root.after(0, lambda c=i: self.status_label.config(text=f"Starting in {c}s... Click target field now!"))
            time.sleep(1.0)
        
        if not self.is_typing:
            self.reset_ui()
            return

        self.root.after(0, lambda: self.status_label.config(text="Typing in progress... (Press ESC to abort)"))
        
        # Character-by-character typing loop
        for char in text:
            if not self.is_typing:
                break
            
            if char == '\n':
                self.keyboard.press(Key.enter)
                self.keyboard.release(Key.enter)
            else:
                self.keyboard.type(char)
            
            time.sleep(delay)
        
        self.root.after(0, self.reset_ui)

    def stop_typing(self):
        self.is_typing = False
        self.root.after(0, self.reset_ui)

    def reset_ui(self):
        self.is_typing = False
        self.status_label.config(text="Status: Stopped / Ready (ESC to abort)")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoTyperApp(root)
    root.mainloop()