import cmd
import threading
from config import load_config
from serial_monitor import SerialMonitor
from logger import SerialLogger
from logic_matcher import LogicMatcher

class SerialDebugShell(cmd.Cmd):
    intro = "🚀 Python串口调试工具 (输入help查看命令)"
    prompt = "SERIAL> "
    
    def __init__(self, serial_cfg, log_cfg):
        super().__init__()
        self.logger = SerialLogger(log_cfg)
        self.monitor = SerialMonitor(serial_cfg, self.logger)
        self._start_monitor()
        
    def _start_monitor(self):
        if not self.monitor.start():
            print("❗ 按任意键返回命令界面...")
            return
        
        # 显式创建非守护线程
        self.process_thread = threading.Thread(target=self._process_data)
        self.process_thread.daemon = True  # 主线程退出时不会强制终止
        self.process_thread.start()
    
    def _process_data(self):
        while self.monitor.running:
            self.monitor.process_received_data()  # 调用新方法
    
    def do_send(self, arg):
        """发送数据: send <数据>"""
        if not arg:
            print("请输入要发送的数据")
            return
        self.monitor.send_data(arg.encode())
    
    def do_hexsend(self, arg):
        """发送十六进制数据: hexsend <A1 B2 C3>"""
        try:
            data = bytes.fromhex(arg.replace(' ', ''))
            self.monitor.send_data(data)
        except ValueError:
            print("无效的十六进制格式")
    
    def do_filter(self, arg):
        """更新过滤关键字: filter <关键字1,关键字2>"""
        self.logger.keywords = [re.compile(k.strip(), re.I) for k in arg.split(',')]
        print(f"更新过滤关键字: {arg}")
    
    def do_exit(self, arg):
        """退出程序"""
        self.monitor.stop()
        print("感谢使用!")
        return True
    
    def do_config(self, arg):
        """重新加载配置: config"""
        global serial_cfg, log_cfg
        serial_cfg, log_cfg = load_config()
        print("配置已重新加载")

if __name__ == "__main__":
    # 加载初始配置
    serial_cfg, log_cfg = load_config()
    shell = SerialDebugShell(serial_cfg, log_cfg)  # 先创建实例
    
    try:
        shell.cmdloop()
    except KeyboardInterrupt:
        print("\n捕获Ctrl+C，正在停止程序...")
        # 关键修复：停止监控线程
        shell.monitor.stop()  # 设置running=False
        
        # 确保所有线程结束
        if hasattr(shell, 'process_thread'):
            shell.process_thread.join(timeout=1.0)  # 等待线程结束
        
        print("程序已安全终止")