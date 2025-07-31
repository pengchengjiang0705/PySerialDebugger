import os
import re
from datetime import datetime
from logic_matcher import LogicMatcher

class SerialLogger:
    def __init__(self, config):
        self.config = config
        self.current_file = None
        self.current_size = 0
        self.logic_matcher = LogicMatcher(config.match_logic)
        self._open_log_file()
    
    def _open_log_file(self):
        """创建或轮转日志文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.config.filepath.rsplit('.', 1)[0]}_{timestamp}.log"
        self.current_file = open(filename, 'a', encoding='utf-8')
        self.current_size = os.path.getsize(filename)
    
    def _should_rotate(self):
        """检查日志文件大小"""
        return self.current_size > self.config.max_size * 1024 * 1024
    
    def _matches_logic(self, data_str):
        """使用新逻辑匹配器检查"""
        return self.logic_matcher.matches(data_str)

    def log(self, timestamp, direction, data):
        """记录日志并过滤"""
        # 十六进制格式化
        if self.config.hex_mode:
            data_str = ' '.join(f"{b:02X}" for b in data)
        else:
            try:
                data_str = data.decode('utf-8', errors='replace')
            except UnicodeDecodeError:
                data_str = ' '.join(f"{b:02X}" for b in data)
        
        # 关键字过滤
        if not self._matches_logic(data_str):
            return False
        
        # 写入日志
        log_entry = f"[{timestamp}] {direction}: {data_str}\n"
        self.current_file.write(log_entry)
        self.current_file.flush()
        self.current_size += len(log_entry)
        
        # 文件轮转
        if self._should_rotate():
            self.current_file.close()
            self._open_log_file()
        
        return True