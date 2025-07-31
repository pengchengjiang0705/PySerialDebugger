import re

class LogicMatcher:
    def __init__(self, logic_str):
        """
        初始化逻辑匹配器
        
        参数:
            logic_str: 逻辑表达式字符串，如 'AND("0x","111")'
        """
        self.logic_str = logic_str.strip()
        self.compiled_rules = self._compile_logic()
    
    def _parse_condition(self, cond_str):
        """解析单个条件"""
        cond_str = cond_str.strip()
        # 处理引号包裹的字符串
        if cond_str.startswith('"') and cond_str.endswith('"'):
            return re.compile(re.escape(cond_str[1:-1]), re.IGNORECASE)
        # 处理正则表达式
        elif cond_str.startswith('/') and cond_str.endswith('/'):
            pattern = cond_str[1:-1]
            return re.compile(pattern, re.IGNORECASE)
        # 默认按普通字符串处理
        return re.compile(re.escape(cond_str), re.IGNORECASE)
    
    def _compile_logic(self):
        """编译逻辑表达式为可执行函数"""
        if not self.logic_str:
            return lambda data: True
        
        # 递归解析逻辑表达式
        def parse_expr(expr):
            expr = expr.strip()
            # 处理AND表达式
            if expr.upper().startswith("AND(") and expr.endswith(")"):
                inner = expr[4:-1]
                conditions = [parse_expr(c.strip()) for c in self._split_conditions(inner)]
                return lambda data: all(cond(data) for cond in conditions)
            
            # 处理OR表达式
            elif expr.upper().startswith("OR(") and expr.endswith(")"):
                inner = expr[3:-1]
                conditions = [parse_expr(c.strip()) for c in self._split_conditions(inner)]
                return lambda data: any(cond(data) for cond in conditions)
            
            # 处理NOT表达式
            elif expr.upper().startswith("NOT(") and expr.endswith(")"):
                inner = expr[4:-1]
                condition = parse_expr(inner)
                return lambda data: not condition(data)
            
            # 处理基础条件
            return lambda data: bool(self._parse_condition(expr).search(data))
        
        return parse_expr(self.logic_str)
    
    def _split_conditions(self, inner_str):
        """分割内部条件"""
        conditions = []
        current = ""
        depth = 0
        
        for char in inner_str:
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            
            if char == ',' and depth == 0:
                conditions.append(current)
                current = ""
            else:
                current += char
        
        if current:
            conditions.append(current)
        
        return conditions
    
    def matches(self, data):
        """
        检查数据是否匹配逻辑
        
        参数:
            data: 要检查的字符串数据
        返回:
            bool: 是否匹配逻辑条件
        """
        return self.compiled_rules(data)