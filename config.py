import configparser
from dataclasses import dataclass

@dataclass
class SerialConfig:
    port: str = 'COM1'
    baudrate: int = 9600
    bytesize: int = 8
    parity: str = 'N'
    stopbits: float = 1
    timeout: float = 0.1
    rtscts: bool = False
    dsrdtr: bool = False

@dataclass
class LogConfig:
    filepath: str = 'serial.log'
    max_size: int = 10  # MB
    match_logic: str = ''  # 新增匹配逻辑配置
    hex_mode: bool = False

def load_config(filename='config.ini'):
    """加载或创建配置文件"""
    config = configparser.ConfigParser()
    config.read(filename, encoding='utf-8')
    
    # 串口配置
    serial_cfg = SerialConfig(
        port=config.get('SERIAL', 'Port', fallback='COM1'),
        baudrate=config.getint('SERIAL', 'Baudrate', fallback=9600),
        bytesize=config.getint('SERIAL', 'Bytesize', fallback=8),
        parity=config.get('SERIAL', 'Parity', fallback='N'),
        stopbits=config.getfloat('SERIAL', 'Stopbits', fallback=1),
        timeout=config.getfloat('SERIAL', 'Timeout', fallback=0.1),
        rtscts=config.getboolean('SERIAL', 'Rtscts', fallback=False),
        dsrdtr=config.getboolean('SERIAL', 'Dsrdtr', fallback=False)
    )
    
    # 日志配置
    log_cfg = LogConfig(
        filepath=config.get('LOG', 'FilePath', fallback='serial.log'),
        max_size=config.getint('LOG', 'MaxSizeMB', fallback=10),
        hex_mode=config.getboolean('LOG', 'HexMode', fallback=False),
        match_logic=config.get('LOG', 'MatchLogic', fallback='')
    )
    
    return serial_cfg, log_cfg