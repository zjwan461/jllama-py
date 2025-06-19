import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
from queue import Queue


class TextViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("系统输出")
        self.root.geometry("1000x600")
        self.root.minsize(800, 400)

        # 设置中文字体支持
        self.font = ('微软雅黑', 12)

        # 创建UI
        self._create_ui()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.log_queue = Queue(maxsize=0)
        self.max_save_line = 500
        self.text_line = 0
        threading.Thread(target=self.append_from_queue, daemon=True, name="log_text_viewer").start()

    def on_close(self):
        """处理窗口关闭事件"""
        self.root.withdraw()

    def _create_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 状态栏
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

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
        if not text.endswith('\n'):
            text += '\n'
        """设置文本内容"""
        self.root.deiconify()
        self.text_area.config(state=tk.NORMAL)  # 启用编辑
        self.text_area.delete(1.0, tk.END)  # 清除现有内容
        self.text_area.insert(tk.END, text)  # 插入新文本
        self.text_line = text.count('\n')
        self.text_area.see(tk.END)  # 滚动到底部
        self.text_area.config(state=tk.DISABLED)  # 禁用编辑

    def append_text(self, text):
        if not text.endswith('\n'):
            text += '\n'

        self.root.deiconify()
        """设置文本内容"""
        self.text_area.config(state=tk.NORMAL)  # 启用编辑
        self.text_area.insert(tk.END, text)  # 插入新文本
        line_count = text.count('\n')
        self.text_line += line_count
        num = self.text_line - self.max_save_line
        if num > 0:
            self.text_area.delete(1.0, str(num + 1) + ".0")  # 删除多余行
            # print(f"删除num={num}")
            self.text_line = self.text_line - num
        self.text_area.see(tk.END)  # 滚动到底部
        self.text_area.config(state=tk.DISABLED)  # 禁用编辑

    def push_text(self, text):
        self.log_queue.put(text)

    def append_from_queue(self):
        while True:
            text = self.log_queue.get()
            self.append_text(text)
