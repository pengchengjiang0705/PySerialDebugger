# 文档4修改后的代码
import serial
import threading
import queue
from datetime import datetime

class SerialMonitor:
    def __init__(self, serial_cfg, logger):
        self.serial_cfg = serial_cfg
        self.logger = logger
        self.serial = None
        self.running = False
        self.receive_queue = queue.Queue()
        self.auto_send_queue = queue.Queue()
        self.receiver_thread = None
        
    def _open_serial(self):
        """打开串口连接"""
        try:
            self.serial = serial.Serial(
                port=self.serial_cfg.port,
                baudrate=self.serial_cfg.baudrate,
                bytesize=self.serial_cfg.bytesize,
                parity=self.serial_cfg.parity,
                stopbits=self.serial_cfg.stopbits,
                timeout=self.serial_cfg.timeout,
                rtscts=self.serial_cfg.rtscts,
                dsrdtr=self.serial_cfg.dsrdtr
            )
            # 清除缓冲区
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            return True
        except serial.SerialException as e:
            print(f"🚨🚨🚨🚨 串口错误: {str(e)}")
            if "Access Denied" in str(e):
                print(f"➡➡➡➡️ 解决方案: 关闭其他占用{self.serial_cfg.port}的程序")
            return False
        except Exception as e:  # 捕获其他异常
            print(f"⚠️ 未知错误: {str(e)}")
            return False
    
    def _receiver_thread(self):
        """接收线程核心"""
        while self.running:
            try:
                # 使用超时读取避免CPU空转
                data = self.serial.read_until(b'\n')  # 使用初始化时设置的超时
                if data:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    self.receive_queue.put((timestamp, data))
                    # # 根据实际长度打印数据
                    # preview = repr(data) if len(data) <= 180 else repr(data[:180]) + '...'
                    # print(f"收到{len(data)}字节: {preview}")
            except (serial.SerialException, TypeError) as e:  # 修改：捕获更多异常
                if self.running:  # 仅当仍在运行时才打印错误
                    print(f"接收错误: {str(e)}")
                break  # 退出线程循环
            except Exception as e:  # 捕获其他所有异常
                if self.running:
                    print(f"未知接收错误: {str(e)}")
                break
    
    def process_received_data(self):
        """阻塞式处理队列数据"""
        try:
            timestamp, data = self.receive_queue.get(timeout=0.1)
            # 先检查是否匹配逻辑
            if self.logger.log(timestamp, "RX", data):
                data_str = data.decode('utf-8', errors='replace') 
                print(f"\033[92m[{timestamp}] RX: {data_str}\033[0m")
                # 根据实际长度打印数据
                # preview = repr(data) if len(data) <= 180 else repr(data[:180]) + '...'
                # print(f"处理{len(data)}字节: {preview}")
        except queue.Empty:
            pass
    
    def send_data(self, data):
        """发送数据并记录"""
        if not self.serial or not self.serial.is_open:
            print("❌❌ 串口未连接")
            return False
        
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            self.serial.write(data)
            self.logger.log(timestamp, "TX", data)
            print(f"\033[94m[{timestamp}] TX: {data.decode()}\033[0m")
            return True
        except Exception as e:
            print(f"发送失败: {str(e)}")
            return False
    
    def do_match(self, arg):
        """设置匹配逻辑: match <逻辑表达式>
        示例: 
        match AND("0x","111") - 同时包含0x和111
        match OR("ERR","WARN") - 包含ERR或WARN
        match NOT("DEBUG") - 不包含DEBUG
        """
        if not arg:
            print("当前匹配逻辑:", self.logger.logic_matcher.logic_str or "无")
            return
        
        try:
            # 测试编译逻辑
            test_matcher = LogicMatcher(arg)
            test_matcher.matches("test")  # 验证是否可执行
            
            # 更新配置
            self.logger.logic_matcher = test_matcher
            print(f"匹配逻辑更新为: {arg}")
        except Exception as e:
            print(f"无效的逻辑表达式: {str(e)}\n格式示例: AND(\"0x\",\"111\")")

    def start(self):
        """启动监控"""
        if not self._open_serial():
            return False
        
        self.running = True
        # 启动接收线程并保存引用
        self.receiver_thread = threading.Thread(target=self._receiver_thread, daemon=True)
        self.receiver_thread.start()
        
        print(f"✅ 串口监控已启动 @ {self.serial_cfg.port}")
        return True
    
    def stop(self):
        """停止监控"""
        self.running = False
        
        # 先关闭串口（会触发接收线程异常）
        if self.serial and self.serial.is_open:
            self.serial.close()
        
        # 等待所有线程结束
        threads_to_join = []
        if self.receiver_thread:
            threads_to_join.append(self.receiver_thread)
        
        # 可选：添加其他需要等待的线程
        
        # 等待线程结束（最多1秒）
        for t in threads_to_join:
            t.join(timeout=1.0)
            if t.is_alive():
                print(f"⚠️ 线程{t.name}未正常结束")
        
        print("🛑串口监控已完全停止")