import logging
from py.tk.log_viewer import TextViewer

textViewer: TextViewer


class LogViewHandler(logging.Handler):
    """自定义日志处理器，将日志输出到控制台并添加时间戳前缀"""

    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        """处理日志记录"""
        try:
            # 获取格式化后的日志消息
            msg = self.format(record)
            # print(msg)
            if textViewer:
                # textViewer.append_text(msg + "\n") # 每次都往tk的log text viewer ui组件里写性能较差
                textViewer.push_text(msg + "\n")
        except Exception:
            # 处理异常，避免日志处理失败导致程序崩溃
            self.handleError(record)
