import tkinter as tk
from tkinter import ttk, scrolledtext


class TextViewer:
    def  __init__(self, root):
        self.root = root
        self.root.title("系统输出")
        self.root.geometry("1000x600")
        self.root.minsize(800, 400)

        # 设置中文字体支持
        self.font = ('微软雅黑', 12)

        # 创建UI
        self._create_ui()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """处理窗口关闭事件"""
        self.root.withdraw()

    def _create_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 顶部菜单栏
        # menu_bar = tk.Menu(self.root)
        # self.root.config(menu=menu_bar)

        # 状态栏
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # self.status_var = tk.StringVar()
        # self.status_var.set("就绪")
        # status_label = ttk.Label(status_frame, textvariable=self.status_var, anchor=tk.W)
        # status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        # 文本显示区域
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        # 创建滚动文本框
        self.text_area = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=self.font,
            state=tk.DISABLED,
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

    def set_text(self, text):
        """设置文本内容"""
        self.root.deiconify()
        self.text_area.config(state=tk.NORMAL)  # 启用编辑
        self.text_area.delete(1.0, tk.END)      # 清除现有内容
        self.text_area.insert(tk.END, text)     # 插入新文本
        self.text_area.see(tk.END)  # 滚动到底部
        self.text_area.config(state=tk.DISABLED)  # 禁用编辑

    def append_text(self, text):
        self.root.deiconify()
        """设置文本内容"""
        self.text_area.config(state=tk.NORMAL)  # 启用编辑
        self.text_area.insert(tk.END, text)  # 插入新文本
        self.text_area.see(tk.END) # 滚动到底部
        self.text_area.config(state=tk.DISABLED)  # 禁用编辑

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = TextViewer(root)
#     app.set_text("Hello, World!")
#     root.mainloop()