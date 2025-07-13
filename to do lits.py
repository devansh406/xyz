import tkinter as tk
from tkinter import messagebox, filedialog

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List")
        self.root.geometry("400x450")
        self.root.configure(bg="#f0f0f0")

        self.tasks = []

        # Title
        tk.Label(self.root, text="My To-Do List", font=("Helvetica", 18, "bold"), bg="#f0f0f0").pack(pady=10)

        # Task Entry
        self.task_entry = tk.Entry(self.root, font=("Helvetica", 14))
        self.task_entry.pack(pady=5, padx=10, fill="x")

        # Add Button
        tk.Button(self.root, text="Add Task", font=("Helvetica", 12), command=self.add_task).pack(pady=5)

        # Task Listbox
        self.task_listbox = tk.Listbox(self.root, font=("Helvetica", 12), selectmode=tk.SINGLE)
        self.task_listbox.pack(pady=10, padx=10, fill="both", expand=True)

        # Button Frame
        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Delete Task", font=("Helvetica", 12), command=self.delete_task).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Save List", font=("Helvetica", 12), command=self.save_tasks).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Load List", font=("Helvetica", 12), command=self.load_tasks).grid(row=0, column=2, padx=5)

    def add_task(self):
        task = self.task_entry.get().strip()
        if task:
            self.tasks.append(task)
            self.update_listbox()
            self.task_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "Task cannot be empty!")

    def delete_task(self):
        selected = self.task_listbox.curselection()
        if selected:
            index = selected[0]
            del self.tasks[index]
            self.update_listbox()
        else:
            messagebox.showwarning("Selection Error", "No task selected!")

    def update_listbox(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            self.task_listbox.insert(tk.END, task)

    def save_tasks(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w") as f:
                for task in self.tasks:
                    f.write(task + "\n")
            messagebox.showinfo("Saved", "Tasks saved successfully!")

    def load_tasks(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "r") as f:
                self.tasks = f.read().splitlines()
            self.update_listbox()
            messagebox.showinfo("Loaded", "Tasks loaded successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()
