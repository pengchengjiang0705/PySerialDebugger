# PySerialDebugger  
一个功能强大的 Python 串口调试工具，支持实时监控、智能数据过滤、灵活日志记录和交互式调试。专为嵌入式开发、硬件调试和串口通信分析场景设计。

## ✨ 核心功能

### 🎯 智能数据过滤
- 支持 `AND / OR / NOT` 逻辑表达式组合过滤  
- 正则表达式：`/pattern/`  
- 字符串匹配：`"exact_match"`  
- 示例：`AND("Error", "/0x[0-9A-F]{2}/")`

### 📝 日志管理
- 自动日志轮转（按文件大小）  
- 时间戳标记每条记录  
- 双模式记录：  
  - **文本模式**：UTF-8 解码  
  - **十六进制模式**：`A1 B2 C3` 格式

### 🖥️ 交互式终端
- 实时彩色显示收发数据：  
  - **TX**：蓝色高亮  
  - **RX**：绿色高亮  
- 多种数据发送模式：  
  - 直接文本发送  
  - 十六进制发送

### ⚙️ 多线程架构
- 独立接收线程保证实时性  
- 安全线程终止机制  
- 非阻塞式数据处理

### 🌐 跨平台支持
- 兼容 Windows / Linux / macOS  
- 自动处理串口访问权限问题  
- 智能错误诊断（如 Access Denied）

---

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install pyserial configparser
```
### 2. 配置设置
根据需要修改config.ini 文件
```ini
[SERIAL]
Port = COM3
Baudrate = 921600
Bytesize = 8
Parity = N
Stopbits = 1
Timeout = 0.5

[LOG]
FilePath = debug.log
MaxSizeMB = 5
MatchLogic = AND("Debug"," ")
HexMode = false
```
### 3. 运行程序
```bash
python main.py
```

---

## 🛠️ 使用指南
### 命令行操作
| 命令 | 功能描述   | 示例 |
|:------:|:------:|:------:|
| send  | 发送文本数据  | send HelloWorld  | 
| hexsend  | 发送十六进制数据  | hexsend A1 B2 C3 |
| match  | 设置逻辑匹配表达式  | match OR("ERR","WARN")  |
| config  | 重载配置文件  | config  |
| exit  | 安全退出程序  | exit  |

### 逻辑匹配语法
#### 逻辑组合
    AND(cond1, cond2) - 同时满足两个条件
    OR(cond1, cond2) - 满足任一条件
    NOT(cond) - 排除指定条件
#### 嵌套表达式
    AND(OR("A","B"), NOT("C")) - (包含A或B) 且 不包含C
#### 使用示例
```bash
match AND("/0x[0-9A-F]{2}/", NOT("DEBUG"))
```
匹配所有包含十六进制数字（如0xA1）且不含"DEBUG"的消息

---

## 🤝 贡献指南
欢迎通过GitHub提交Issues和Pull Requests：

通过pylint进行代码检查
添加对新功能的单元测试
更新相关文档

​​### 贡献前请确保​​：
遵循现有代码风格
更新测试用例
修改影响用户的功能时更新文档

---

## 📜 许可证
MIT License - 详情见 LICENSE 文件

---

## 项目持续开发中，欢迎Star & Fork！​
