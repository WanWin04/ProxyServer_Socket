import tkinter as tk
from tkinter import messagebox
from ProxyModule import main_proxy_module

class ProxyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Proxy GUI")

        # Các biến lưu giá trị từ giao diện
        self.proxy_host_var = tk.StringVar()
        self.proxy_port_var = tk.StringVar()
        self.target_host_var = tk.StringVar()
        self.target_port_var = tk.StringVar()
        self.allowed_time_var = tk.StringVar()
        self.whitelist_var = tk.StringVar()
        self.cache_time_var = tk.StringVar()

        # Gọi hàm tạo giao diện
        self.create_gui()

    def create_gui(self):
        # Tạo và định dạng các widget
        tk.Label(self.root, text="Proxy Host:").grid(row=0, column=0, sticky="e")
        tk.Entry(self.root, textvariable=self.proxy_host_var).grid(row=0, column=1)

        tk.Label(self.root, text="Proxy Port:").grid(row=1, column=0, sticky="e")
        tk.Entry(self.root, textvariable=self.proxy_port_var).grid(row=1, column=1)

        tk.Label(self.root, text="Target Host:").grid(row=2, column=0, sticky="e")
        tk.Entry(self.root, textvariable=self.target_host_var).grid(row=2, column=1)

        tk.Label(self.root, text="Target Port:").grid(row=3, column=0, sticky="e")
        tk.Entry(self.root, textvariable=self.target_port_var).grid(row=3, column=1)

        tk.Label(self.root, text="Allowed Time List:").grid(row=4, column=0, sticky="e")
        tk.Entry(self.root, textvariable=self.allowed_time_var).grid(row=4, column=1)

        tk.Label(self.root, text="Whitelist:").grid(row=5, column=0, sticky="e")
        tk.Entry(self.root, textvariable=self.whitelist_var).grid(row=5, column=1)

        tk.Label(self.root, text="Cache Time:").grid(row=6, column=0, sticky="e")
        tk.Entry(self.root, textvariable=self.cache_time_var).grid(row=6, column=1)

        start_button = tk.Button(self.root, text="Start Proxy", command=self.start_proxy)
        start_button.grid(row=7, column=0, columnspan=2)

    def start_proxy(self):
        # Lấy giá trị từ các biến StringVar
        proxy_host = self.proxy_host_var.get()
        proxy_port = self.proxy_port_var.get()
        target_host = self.target_host_var.get()
        target_port = self.target_port_var.get()
        allowed_time_list = self.allowed_time_var.get()
        whitelist = self.whitelist_var.get()
        cache_time = self.cache_time_var.get()

        # Gọi hàm main_proxy_module với các giá trị vừa lấy
        proxy_config = {
            "proxy_host": proxy_host,
            "proxy_port": proxy_port,
            "target_host": target_host,
            "target_port": target_port,
            "allowed_time_list": allowed_time_list,
            "whitelist": whitelist,
            "cache_time": cache_time,
        }

        try:
            main_proxy_module(proxy_config)
            messagebox.showinfo("Proxy Started", "Proxy server started successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Error starting proxy server:\n{str(e)}")

def main_gui():
    root = tk.Tk()
    app = ProxyGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main_gui()
