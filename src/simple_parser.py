import re
from typing import Dict, Any, List, Optional, Union

class SimpleStrategyParser:
    """Simple regex-based parser for trading strategies"""
    
    def __init__(self):
        # Pattern 1: function calls (e.g., rsi(close, 14) > 30, bbands_upper(close, 20) > 100)
        self.pattern1 = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)\(([^)]+)\)\s*([><=!]+)\s*([^ANDOR\s]+)')
        
        # Pattern 2: direct comparisons (e.g., close > 1000)
        self.pattern2 = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*([><=!]+)\s*([^ANDOR\s]+)')
        
        # Pattern 3: function vs function (e.g., sma(close, 20) > sma(close, 50))
        # Note: This pattern has limitations with nested functions
        self.pattern3 = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)\(([^)]+)\)\s*([><=!]+)\s*([a-zA-Z_][a-zA-Z0-9_]*)\(([^)]+)\)')
        
        # Pattern 4: value vs function (e.g., 50 > rsi(close, 14))
        self.pattern4 = re.compile(r'([^ANDOR\s]+)\s*([><=!]+)\s*([a-zA-Z_][a-zA-Z0-9_]*)\(([^)]+)\)')
        
        # Pattern 5: crossover conditions (e.g., rsi(close, 14) crossover 40)
        self.pattern5 = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)\(([^)]+)\)\s+(crossover)\s+([^ANDOR\s]+)')
        
        # Pattern 6: direct crossover (e.g., close crossover 1000)
        self.pattern6 = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)\s+(crossover)\s+([^ANDOR\s]+)')
        
        # Pattern 7: Bollinger Bands property access (e.g., bbands(close, 20, 2).upper < close)
        self.pattern7 = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)\(([^)]+)\)\.(upper|lower|middle)\s*([><=!]+)\s*([^ANDOR\s]+)')
        
        # Pattern 8: function-to-function crossover (e.g., ema(close, 50) crossover ema(close, 200))
        self.pattern8 = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)\(([^)]+(?:\([^)]*\)[^)]*)*)\)\s+(crossover)\s+([a-zA-Z_][a-zA-Z0-9_]*)\(([^)]+(?:\([^)]*\)[^)]*)*)\)')

        # Pattern 9: arithmetic expression with functions/properties (e.g., A - B < C)
        # Supports bbands(...).upper|lower|middle and generic function calls on both sides of +/-
        self.pattern9 = re.compile(
            r'\s*('
            r'(?:[a-zA-Z_][a-zA-Z0-9_]*)\([^)]*\)(?:\.(?:upper|lower|middle))?'
            r')\s*([+\-])\s*('
            r'(?:[a-zA-Z_][a-zA-Z0-9_]*)\([^)]*\)(?:\.(?:upper|lower|middle))?'
            r')\s*([><=!]+)\s*(.+)\s*$'
        )

        # Pattern 10: bbands property crossover (e.g., bbands(...).lower crossover close | sma(...))
        self.pattern10 = re.compile(
            r'\s*([a-zA-Z_][a-zA-Z0-9_]*)\(([^)]*)\)\.(upper|lower|middle)\s+(crossover)\s+(.+)$'
        )

        # Pattern 11: multi-timeframe conditions (e.g., tf(condition, 'daily'), tf(condition, 'w'))
        self.pattern11 = re.compile(
            r'\s*tf\s*\(\s*(.+?)\s*,\s*[\'"](daily|weekly|monthly|yearly|d|w|m|y)[\'"]\s*\)\s*$'
        )
        
        # Pattern 12: multiplication/division expressions (e.g., A * B, A / B)
        self.pattern12 = re.compile(
            r'\s*('
            r'(?:[a-zA-Z_][a-zA-Z0-9_]*)\([^)]*\)(?:\.(?:upper|lower|middle))?'
            r'|[a-zA-Z_][a-zA-Z0-9_]*'
            r'|\d+\.?\d*'
            r')\s*([*/])\s*('
            r'(?:[a-zA-Z_][a-zA-Z0-9_]*)\([^)]*\)(?:\.(?:upper|lower|middle))?'
            r'|[a-zA-Z_][a-zA-Z0-9_]*'
            r'|\d+\.?\d*'
            r')\s*([><=!]+)\s*(.+)\s*$'
        )
        
        # Pattern 13: MACD property crossover (e.g., macd(...).histogram crossover 0)
        self.pattern13 = re.compile(
            r'\s*([a-zA-Z_][a-zA-Z0-9_]*)\(([^)]*)\)\.(histogram|signal|macd)\s+(crossover)\s+(.+)$'
        )
    
    def parse(self, strategy: str) -> Union[Dict[str, Any], None]:
        """Parse a strategy string into a structured format"""
        if not strategy or not strategy.strip():
            return None
        
        strategy = strategy.strip()
        
        # Split by logical operators
        parts = self._split_by_logical_operators(strategy)
        
        if len(parts) == 1:
            # Single condition
            return self._parse_single_condition(parts[0])
        else:
            # Multiple conditions with logical operators
            return self._parse_logical_expression(parts)
    
    def _split_top_level_comparison(self, text: str) -> Optional[Dict[str, str]]:
        """Find the first top-level comparison operator and split into left/op/right."""
        operators = ['>=', '<=', '==', '!=', '>', '<']
        paren = 0
        i = 0
        while i < len(text):
            c = text[i]
            if c == '(':
                paren += 1
            elif c == ')':
                paren -= 1
            if paren == 0:
                for op in operators:
                    if text.startswith(op, i):
                        left = text[:i].strip()
                        right = text[i+len(op):].strip()
                        return {"left": left, "operator": op, "right": right}
            i += 1
        return None

    def _parse_token_as_operand(self, token: str) -> Any:
        token = token.strip()
        # function call or bbands property
        node = self._parse_operand_token(token)
        if isinstance(node, dict):
            return node
        # fallback: try value/data field
        return self._parse_value(token)

    def _split_by_logical_operators(self, strategy: str) -> List[str]:
        """Split strategy by AND/OR operators, preserving parentheses"""
        # This is a simplified approach - for complex nested expressions,
        # we'd need a more sophisticated parser
        parts = []
        current_part = ""
        paren_count = 0
        
        i = 0
        while i < len(strategy):
            char = strategy[i]
            
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
            
            # Check for AND/OR operators (only when not inside parentheses)
            # Make sure we're not splitting on comparison operators
            if paren_count == 0 and i < len(strategy) - 2:
                # Check for AND (3 characters) - must be a complete word
                if (strategy[i:i+3].upper() == 'AND' and 
                    (i == 0 or not strategy[i-1].isalnum()) and 
                    (i + 3 >= len(strategy) or not strategy[i+3].isalnum())):
                    if current_part.strip():
                        parts.append(current_part.strip())
                    current_part = ""
                    i += 3
                    continue
                # Check for OR (2 characters) - must be a complete word
                elif (strategy[i:i+2].upper() == 'OR' and 
                      (i == 0 or not strategy[i-1].isalnum()) and 
                      (i + 2 >= len(strategy) or not strategy[i+2].isalnum())):
                    if current_part.strip():
                        parts.append(current_part.strip())
                    current_part = ""
                    i += 2
                    continue
            
            current_part += char
            i += 1
        
        if current_part.strip():
            parts.append(current_part.strip())
        
        return parts
    
    def _parse_logical_expression(self, parts: List[str]) -> Dict[str, Any]:
        """Parse logical expressions (AND/OR)"""
        if len(parts) == 1:
            return self._parse_single_condition(parts[0])
        
        # Find the operator between the first two parts
        # This is a simplified approach - assumes left-to-right evaluation
        operator = "AND"  # Default to AND for now
        
        left = self._parse_single_condition(parts[0])
        right = self._parse_logical_expression(parts[1:])
        
        return {
            "type": "logical",
            "operator": operator,
            "left": left,
            "right": right
        }
    
    def _parse_single_condition(self, condition: str) -> Union[Dict[str, Any], None]:
        """Parse a single condition"""
        condition = condition.strip()
        
        # Try multi-timeframe condition first
        match = self.pattern11.match(condition)
        if match:
            inner_condition = match.group(1).strip()
            timeframe = match.group(2)
            # Normalize timeframe code
            normalized_timeframe = self._normalize_timeframe(timeframe)
            # Parse the inner condition recursively
            parsed_condition = self._parse_single_condition(inner_condition)
            if parsed_condition:
                return {
                    "type": "multi_timeframe",
                    "timeframe": normalized_timeframe,
                    "condition": parsed_condition
                }
            return None
        
        # Try function-to-function crossover first
        match = self.pattern8.match(condition)
        if match:
            return self._build_function_to_function_crossover_condition_from_match(match)

        # Try arithmetic comparison (e.g., bbands(...).upper - bbands(...).lower < sma(...))
        match = self.pattern9.match(condition)
        if match:
            return self._build_arithmetic_comparison_from_match(match)
            
        # Try multiplication/division comparison (e.g., sma(volume, 20) * 1.5 > close)
        match = self.pattern12.match(condition)
        if match:
            return self._build_multiplication_comparison_from_match(match)

        # Try bbands property crossover
        match = self.pattern10.match(condition)
        if match:
            func_name, params_str, prop, cross, right_token = match.groups()
            left_node = {
                "type": "bbands_property",
                "function_name": func_name,
                "parameters": self._parse_parameters(params_str),
                "property": prop
            }
            right_node = self._parse_operand_token(right_token)
            return {
                "type": "crossover",
                "left": left_node,
                "crossover_type": cross,
                "right": right_node
            }

        # Try MACD property crossover
        match = self.pattern13.match(condition)
        if match:
            func_name, params_str, prop, cross, right_token = match.groups()
            left_node = {
                "type": "macd_property",
                "function_name": func_name,
                "parameters": self._parse_parameters(params_str),
                "property": prop
            }
            right_node = self._parse_operand_token(right_token)
            return {
                "type": "crossover",
                "left": left_node,
                "crossover_type": cross,
                "right": right_node
            }

        # Generic top-level comparison splitter to handle nested params like count(expr, n) >= k
        split = self._split_top_level_comparison(condition)
        if split:
            left_token = split['left']
            right_token = split['right']
            op = split['operator']
            # left may be function call, bbands property, data field, or literal
            left_node = self._parse_operand_token(left_token)
            right_node = self._parse_operand_token(right_token)
            if isinstance(left_node, dict) and left_node.get('type') == 'function_call':
                return {
                    "type": "function_comparison",
                    "left": left_node,
                    "operator": op,
                    "right": right_node
                }
            if isinstance(left_node, dict) and left_node.get('type') == 'bbands_property':
                return {
                    "type": "bbands_property_comparison",
                    "left": left_node,
                    "operator": op,
                    "right": right_node
                }
            if isinstance(left_node, dict) and left_node.get('type') == 'function_call' and isinstance(right_node, dict) and right_node.get('type') == 'function_call':
                return {
                    "type": "function_vs_function",
                    "left": left_node,
                    "operator": op,
                    "right": right_node
                }
            # fallback to direct comparison
            return {
                "type": "comparison",
                "left": left_node,
                "operator": op,
                "right": right_node
            }

        # Try Bollinger Bands property access first
        match = self.pattern7.match(condition)
        if match:
            return self._build_bbands_property_condition_from_match(match)
        
        # Try crossover patterns first
        match = self.pattern5.match(condition)
        if match:
            return self._build_crossover_condition_from_match(match, True)
        
        match = self.pattern6.match(condition)
        if match:
            return self._build_crossover_condition_from_match(match, False)
        
        # Try custom function vs function parsing for nested functions first
        result = self._try_parse_function_vs_function_nested(condition)
        if result:
            return result
        
        # Try function vs function comparison (regex-based, limited with nested functions)
        match = self.pattern3.match(condition)
        if match:
            return self._build_function_vs_function_condition_from_match(match)
        
        # Try value vs function comparison
        match = self.pattern4.match(condition)
        if match:
            return self._build_value_vs_function_condition_from_match(match)
        
        # Try function call comparison
        match = self.pattern1.match(condition)
        if match:
            return self._build_function_condition_from_match(match)
        
        # Try direct comparison
        match = self.pattern2.match(condition)
        if match:
            return self._build_direct_condition_from_match(match)
        
        return None
    
    def _build_crossover_condition_from_match(self, match, is_function: bool) -> Dict[str, Any]:
        """Build crossover condition from regex match"""
        if is_function:
            groups = match.groups()
            return {
                "type": "crossover",
                "left": {
                    "type": "function_call",
                    "name": groups[0],
                    "parameters": self._parse_parameters(groups[1])
                },
                "crossover_type": groups[2],  # "crosses above" or "crosses below"
                "right": self._parse_value(groups[3])
            }
        else:
            groups = match.groups()
            return {
                "type": "crossover",
                "left": {
                    "type": "identifier",
                    "name": groups[0]
                },
                "crossover_type": groups[1],  # "crosses above" or "crosses below"
                "right": self._parse_value(groups[2])
            }
    
    def _build_function_to_function_crossover_condition_from_match(self, match) -> Dict[str, Any]:
        """Build function-to-function crossover condition from regex match"""
        groups = match.groups()
        return {
            "type": "function_to_function_crossover",
            "left": {
                "type": "function_call",
                "name": groups[0],
                "parameters": self._parse_parameters(groups[1])
            },
            "crossover_type": groups[2],  # "crossover"
            "right": {
                "type": "function_call",
                "name": groups[3],
                "parameters": self._parse_parameters(groups[4])
            }
        }
    
    def _build_function_vs_function_condition_from_match(self, match) -> Dict[str, Any]:
        """Build function vs function comparison from regex match"""
        groups = match.groups()
        return {
            "type": "function_vs_function",
            "left": {
                "type": "function_call",
                "name": groups[0],
                "parameters": self._parse_parameters(groups[1])
            },
            "operator": groups[2],
            "right": {
                "type": "function_call",
                "name": groups[3],
                "parameters": self._parse_parameters(groups[4])
            }
        }
    
    def _build_value_vs_function_condition_from_match(self, match) -> Dict[str, Any]:
        """Build value vs function comparison from regex match"""
        groups = match.groups()
        return {
            "type": "value_vs_function",
            "left": self._parse_value(groups[0]),
            "operator": groups[1],
            "right": {
                "type": "function_call",
                "name": groups[2],
                "parameters": self._parse_parameters(groups[3])
            }
        }
    
    def _build_function_condition_from_match(self, match) -> Dict[str, Any]:
        """Build function comparison from regex match"""
        groups = match.groups()
        return {
            "type": "function_comparison",
            "left": {
                "type": "function_call",
                "name": groups[0],
                "parameters": self._parse_parameters(groups[1])
            },
            "operator": groups[2],
            "right": self._parse_value(groups[3])
        }
    
    def _build_direct_condition_from_match(self, match) -> Dict[str, Any]:
        """Build direct comparison from regex match"""
        groups = match.groups()
        return {
            "type": "comparison",
            "left": {
                "type": "identifier",
                "name": groups[0]
            },
            "operator": groups[1],
            "right": self._parse_value(groups[2])
        }
    
    def _build_bbands_property_condition_from_match(self, match) -> Dict[str, Any]:
        """Build Bollinger Bands property access condition from regex match"""
        groups = match.groups()
        return {
            "type": "bbands_property_comparison",
            "left": {
                "type": "bbands_property",
                "function_name": groups[0],
                "parameters": self._parse_parameters(groups[1]),
                "property": groups[2]  # upper, lower, or middle
            },
            "operator": groups[3],
            "right": self._parse_value(groups[4])
        }

    def _parse_operand_token(self, token: str) -> Dict[str, Any]:
        """Parse an operand token that may be a function call, bbands property, or arithmetic expression."""
        token = token.strip()
        
        # Try to parse as arithmetic expression first (e.g., "sma(volume, 20) * 1.5")
        if any(op in token for op in ['*', '/', '+', '-']):
            # Check if it's a valid arithmetic expression
            for op in ['*', '/', '+', '-']:  # Order matters: multiplication/division first
                if op in token:
                    # Find the operator position, ensuring it's not inside parentheses
                    paren_count = 0
                    for i, char in enumerate(token):
                        if char == '(':
                            paren_count += 1
                        elif char == ')':
                            paren_count -= 1
                        elif char == op and paren_count == 0:
                            # Found arithmetic operator at top level
                            left_part = token[:i].strip()
                            right_part = token[i+1:].strip()
                            
                            # Skip if this is just a negative number (e.g., "-5")
                            if op == '-' and (not left_part or left_part.endswith('(')):
                                continue
                            
                            # Parse both parts recursively
                            left_node = self._parse_operand_token(left_part)
                            right_node = self._parse_operand_token(right_part)
                            
                            return {
                                "type": "arithmetic_expression",
                                "left": left_node,
                                "operator": op,
                                "right": right_node
                            }
                    break
        
        # bbands property like bbands(...).upper
        m = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\(([^)]*)\)\.(upper|lower|middle)$', token)
        if m:
            return {
                "type": "bbands_property",
                "function_name": m.group(1),
                "parameters": self._parse_parameters(m.group(2)),
                "property": m.group(3)
            }
        
        # MACD property like macd(...).histogram
        m = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\(([^)]*)\)\.(histogram|signal|macd)$', token)
        if m:
            return {
                "type": "macd_property",
                "function_name": m.group(1),
                "parameters": self._parse_parameters(m.group(2)),
                "property": m.group(3)
            }
        
        # generic function call
        func = self._parse_function_call_string(token)
        if func:
            return func
        # data field
        if token.lower() in ['open', 'high', 'low', 'close', 'volume', 'hl2', 'hlc3']:
            return {"type": "data_field", "name": token.lower()}
        # literal
        return {"type": "literal", "value": self._parse_value(token)}

    def _build_arithmetic_comparison_from_match(self, match) -> Dict[str, Any]:
        """Build arithmetic comparison node from regex match (left1 +/- left2 <op> right)."""
        left1_token, arith_op, left2_token, comp_op, right_token = match.groups()
        return {
            "type": "arithmetic_comparison",
            "left1": self._parse_operand_token(left1_token),
            "arith_op": arith_op,
            "left2": self._parse_operand_token(left2_token),
            "operator": comp_op,
            "right": self._parse_operand_token(right_token)
        }
    
    def _build_multiplication_comparison_from_match(self, match) -> Dict[str, Any]:
        """Build multiplication/division comparison node from regex match (left1 * / left2 <op> right)."""
        left1_token, arith_op, left2_token, comp_op, right_token = match.groups()
        return {
            "type": "multiplication_comparison",
            "left1": self._parse_operand_token(left1_token),
            "arith_op": arith_op,
            "left2": self._parse_operand_token(left2_token),
            "operator": comp_op,
            "right": self._parse_operand_token(right_token)
        }
    
    def _parse_parameters(self, param_str: str) -> List[Any]:
        """Parse function parameters"""
        params = []
        current_param = ""
        paren_count = 0
        bracket_count = 0
        
        i = 0
        while i < len(param_str):
            char = param_str[i]
            
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
            elif char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
            elif char == ',' and paren_count == 0 and bracket_count == 0:
                # Only split on comma if we're not inside parentheses or brackets
                params.append(self._parse_parameter_value(current_param.strip()))
                current_param = ""
                i += 1
                continue
            
            current_param += char
            i += 1
        
        if current_param.strip():
            params.append(self._parse_parameter_value(current_param.strip()))
        
        return params
    
    def _parse_parameter_value(self, value: str) -> Any:
        """Parse a single parameter value"""
        value = value.strip()
        # tolerate trailing comma fragments in nested contexts
        if value.endswith(','):
            value = value[:-1].strip()

        # Try to parse as arithmetic expression first (e.g., "bb_upper(close, 20, 2) - close", "sma(volume, 20) * 1.5")
        if any(op in value for op in ['+', '-', '*', '/']):
            # Check if it's a valid arithmetic expression (not just a negative number)
            # Look for arithmetic operators that are not inside parentheses
            for op in ['*', '/', '+', '-']:  # Order matters: multiplication/division first
                if op in value:
                    # Find the operator position, ensuring it's not inside parentheses
                    paren_count = 0
                    for i, char in enumerate(value):
                        if char == '(':
                            paren_count += 1
                        elif char == ')':
                            paren_count -= 1
                        elif char == op and paren_count == 0:
                            # Found arithmetic operator at top level
                            left_part = value[:i].strip()
                            right_part = value[i+1:].strip()
                            # Skip if this is just a negative number (e.g., "-5" or "> -5")
                            if op == "-" and (not left_part or left_part.endswith("(") or left_part.endswith(">") or left_part.endswith("<") or left_part.endswith("=")):
                                continue
                            
                            # Parse both parts recursively
                            left_node = self._parse_parameter_value(left_part)
                            right_node = self._parse_parameter_value(right_part)
                            
                            return {
                                "type": "arithmetic_expression",
                                "left": left_node,
                                "operator": op,
                                "right": right_node
                            }
                    break

        # Try to parse as nested expression (comparison/logical) to support count/countstreak
        try:
            parsed_expr = self.parse(value)
            if isinstance(parsed_expr, dict) and parsed_expr.get('type'):
                return parsed_expr
        except Exception:
            pass
        
        # Try to parse as number
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Check if it's a data field
        if value.lower() in ['open', 'high', 'low', 'close', 'volume', 'hl2', 'hlc3']:
            return {
                "type": "data_field",
                "name": value.lower()
            }
        
        # Check if it's a function call (e.g., "obv(close, volume)")
        if '(' in value and value.endswith(')'):
            # Extract function name and parameters
            func_name = value[:value.find('(')]
            params_str = value[value.find('(')+1:value.rfind(')')]
            
            # Check if it's a valid function name
            if func_name in self.get_supported_functions():
                return {
                    "type": "function_call",
                    "name": func_name,
                    "parameters": self._parse_parameters(params_str)
                }
        
        # Return as string
        return value
    
    def _parse_value(self, value: str) -> Any:
        """Parse a value (number, string, or identifier)"""
        value = value.strip()
        if value.endswith(','):
            value = value[:-1].strip()

        # Try to parse as number
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Check if it's a data field
        if value.lower() in ['open', 'high', 'low', 'close', 'volume', 'hl2', 'hlc3']:
            return {
                "type": "data_field",
                "name": value.lower()
            }
        
        # Return as string
        return value
    
    def _try_parse_function_vs_function_nested(self, condition: str) -> Union[Dict[str, Any], None]:
        """Custom parser for function vs function comparisons with nested functions"""
        # Look for comparison operators
        operators = ['>', '<', '>=', '<=', '==', '!=']
        op_pos = -1
        op_found = None
        
        for op in operators:
            pos = condition.find(op)
            if pos != -1:
                # Check if this operator is not inside parentheses
                paren_count = 0
                for i in range(pos):
                    if condition[i] == '(':
                        paren_count += 1
                    elif condition[i] == ')':
                        paren_count -= 1
                
                if paren_count == 0:
                    op_pos = pos
                    op_found = op
                    break
        
        if op_pos == -1:
            return None
        
        # Split by the operator
        left_part = condition[:op_pos].strip()
        right_part = condition[op_pos + len(op_found):].strip()
        
        # Check if both parts look like function calls
        if (left_part.endswith(')') and '(' in left_part and 
            right_part.endswith(')') and '(' in right_part):
            
            # Parse left function
            left_func = self._parse_function_call_string(left_part)
            if not left_func:
                return None
            
            # Parse right function
            right_func = self._parse_function_call_string(right_part)
            if not right_func:
                return None
            
            return {
                "type": "function_vs_function",
                "left": left_func,
                "operator": op_found,
                "right": right_func
            }
        
        return None
    
    def _parse_function_call_string(self, func_str: str) -> Union[Dict[str, Any], None]:
        """Parse a function call string into a structured format"""
        func_str = func_str.strip()
        
        if not func_str.endswith(')'):
            return None
        
        # Find the opening parenthesis
        paren_pos = func_str.find('(')
        if paren_pos == -1:
            return None
        
        func_name = func_str[:paren_pos].strip()
        params_str = func_str[paren_pos + 1:-1].strip()
        
        # Check if it's a valid function name
        if func_name not in self.get_supported_functions():
            return None
        
        # Parse parameters
        params = self._parse_parameters(params_str)
        
        return {
            "type": "function_call",
            "name": func_name,
            "parameters": params
        }
    
    def _normalize_timeframe(self, timeframe: str) -> str:
        """Normalize timeframe codes to full names"""
        timeframe_map = {
            'd': 'daily',
            'w': 'weekly', 
            'm': 'monthly',
            'y': 'yearly'
        }
        return timeframe_map.get(timeframe.lower(), timeframe.lower())
    
    def get_supported_functions(self) -> List[str]:
        """Get list of supported function names"""
        return [
            # Original functions
            'rsi', 'sma', 'ema', 'macd', 'bbands', 'bbands_upper', 'bbands_lower', 'bbands_middle',
            # New simple BB functions
            'bb_upper', 'bb_lower', 'bb_middle',
            'stoch', 'stoch_k', 'stoch_d', 'stochrsi', 'stochrsi_k', 'stochrsi_d',
            'adx', 'dx', 'minus_di', 'plus_di', 'minus_dm', 'plus_dm',
            'cci', 'mfi', 'willr', 'sar', 'atr', 'natr', 'trange', 'obv',
            'mom', 'roc', 'cmo', 'ultosc', 'ppo', 'stddev', 'var', 'linearreg',
            'ma', 'wma', 'macd_signal', 'macd_hist',
            # Custom series functions
            'cum', 'cumulative',
            # Aggregation functions
            'min', 'max', 'count', 'countstreak', 'abs', 'ceil', 'floor', 'round', 'square',
            # Historical access functions
            'n_days_ago', 'n_weeks_ago', 'n_months_ago', 'n_years_ago',
            # Ehlers indicators
            'fisher_transform', 'instantaneous_trendline', 'cg_oscillator', 'relative_vigor_index',
            'cyber_cycle_oscillator', 'decycler', 'band_pass_filter', 'super_smoother', 'roofing_filter',
            # Ehlers transformations
            'stochasticization', 'fisherization', 'combined_transformation'
        ]
    
    def validate_strategy(self, strategy: str) -> bool:
        """Validate if a strategy string can be parsed"""
        return self.parse(strategy) is not None 