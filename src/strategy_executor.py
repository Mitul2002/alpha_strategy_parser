import numpy as np
from typing import Dict, Any, List, Optional, Union
from function_registry import FunctionRegistry
from simple_parser import SimpleStrategyParser

class StrategyExecutor:
    """Executes parsed strategy structures on market data"""
    
    def __init__(self):
        self.function_registry = FunctionRegistry()
        self._parser = SimpleStrategyParser()
    
    def execute(self, parsed_strategy: Dict[str, Any], data: Dict[str, np.ndarray]) -> np.ndarray:
        """Execute a parsed strategy on market data"""
        if not parsed_strategy:
            return np.array([])
        
        # Provide context (dates) to registry for tf buckets
        try:
            self.function_registry.set_context(data)
        except Exception:
            pass
        
        strategy_type = parsed_strategy.get('type')
        
        if strategy_type == 'logical':
            return self._execute_logical_expression(parsed_strategy, data)
        elif strategy_type == 'crossover':
            return self._execute_crossover_condition(parsed_strategy, data)
        elif strategy_type == 'function_to_function_crossover':
            return self._execute_function_to_function_crossover_condition(parsed_strategy, data)
        elif strategy_type == 'bbands_property_comparison':
            return self._execute_bbands_property_comparison(parsed_strategy, data)
        elif strategy_type == 'arithmetic_comparison':
            return self._execute_arithmetic_comparison(parsed_strategy, data)
        elif strategy_type == 'multiplication_comparison':
            return self._execute_multiplication_comparison(parsed_strategy, data)
        elif strategy_type == 'multi_timeframe':
            return self._execute_multi_timeframe_condition(parsed_strategy, data)
        elif strategy_type == 'function_comparison':
            return self._execute_function_comparison(parsed_strategy, data)
        elif strategy_type == 'function_vs_function':
            return self._execute_function_vs_function_comparison(parsed_strategy, data)
        elif strategy_type == 'value_vs_function':
            return self._execute_value_vs_function_comparison(parsed_strategy, data)
        elif strategy_type == 'comparison':
            return self._execute_comparison(parsed_strategy, data)
        else:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
    
    def _execute_logical_expression(self, parsed: Dict[str, Any], data: Dict[str, np.ndarray]) -> np.ndarray:
        """Execute logical expressions (AND/OR)"""
        operator = parsed.get('operator', 'AND')
        left_result = self.execute(parsed['left'], data)
        right_result = self.execute(parsed['right'], data)
        
        if operator.upper() == 'AND':
            return left_result & right_result
        elif operator.upper() == 'OR':
            return left_result | right_result
        else:
            raise ValueError(f"Unknown logical operator: {operator}")
    
    def _execute_crossover_condition(self, parsed: Dict[str, Any], data: Dict[str, np.ndarray]) -> np.ndarray:
        """Execute crossover conditions (crossover)"""
        left = parsed['left']
        crossover_type = parsed['crossover_type']
        right_value = parsed['right']
        
        # Get the left operand value
        if left['type'] == 'function_call':
            left_values = self._execute_function_call(left, data)
        elif left['type'] == 'identifier':
            left_values = self._get_data_field(left['name'], data)
        elif left['type'] == 'bbands_property':
            left_values = self._get_operand_value(left, data)
        elif left['type'] == 'macd_property':
            left_values = self._get_operand_value(left, data)
        else:
            raise ValueError(f"Invalid left operand type for crossover: {left['type']}")
        
        # Get the right operand value
        right_values = self._resolve_operand_node(right_value, data)
        
        # Calculate crossover signals - when previous bar was below/equal and current bar is above
        # This detects when the condition crosses above the threshold
        return (left_values > right_values) & (np.roll(left_values, 1) <= np.roll(right_values, 1))
    
    def _execute_function_to_function_crossover_condition(self, parsed: Dict[str, Any], data: Dict[str, np.ndarray]) -> np.ndarray:
        """Execute function-to-function crossover conditions (e.g., ema(close, 50) crossover ema(close, 200))"""
        left = parsed['left']
        right = parsed['right']
        
        # Execute both function calls to get the series
        left_values = self._execute_function_call(left, data)
        right_values = self._execute_function_call(right, data)
        
        # Calculate crossover signals - when left series crosses above right series
        # This detects when the left series was below/equal to the right series on the previous bar
        # and is now above the right series on the current bar
        return (left_values > right_values) & (np.roll(left_values, 1) <= np.roll(right_values, 1))
    
    def _execute_bbands_property_comparison(self, parsed: Dict[str, Any], data: Dict[str, np.ndarray]) -> np.ndarray:
        """Execute Bollinger Bands property comparisons (e.g., bbands(close, 20, 2).upper < close)"""
        left = parsed['left']
        operator = parsed['operator']
        right_values = self._get_operand_value(parsed['right'], data)
        
        # Get the Bollinger Bands property value
        if left['function_name'] == 'bbands':
            # Resolve parameters to actual data arrays
            resolved_params = []
            for param in left['parameters']:
                if isinstance(param, dict) and param['type'] == 'data_field':
                    resolved_params.append(self._get_data_field(param['name'], data))
                else:
                    resolved_params.append(param)
            
            # Call the appropriate bbands function based on the property
            if left['property'] == 'upper':
                left_values = self.function_registry.get_function('bbands_upper')(*resolved_params)
            elif left['property'] == 'lower':
                left_values = self.function_registry.get_function('bbands_lower')(*resolved_params)
            elif left['property'] == 'middle':
                left_values = self.function_registry.get_function('bbands_middle')(*resolved_params)
            else:
                raise ValueError(f"Unknown Bollinger Bands property: {left['property']}")
        else:
            raise ValueError(f"Expected 'bbands' function, got: {left['function_name']}")
        
        return self._apply_operator(left_values, operator, right_values)

    def _resolve_operand_node(self, node: Any, data: Dict[str, np.ndarray]) -> np.ndarray:
        """Resolve an operand node produced by parser into a numeric numpy array."""
        if isinstance(node, dict):
            ntype = node.get('type')
            if ntype == 'data_field':
                return self._get_data_field(node['name'], data)
            if ntype == 'function_call':
                return self._execute_function_call(node, data)
            if ntype == 'bbands_property':
                # reuse bbands property execution on left side by building a minimal parsed structure
                tmp = {
                    'left': node,
                    'operator': '==',
                    'right': {'type': 'literal', 'value': 0},
                    'type': 'bbands_property_comparison'
                }
                # hack to get the bbands series; we won't use comparison result.
                # Instead, directly compute here mirroring _execute_bbands_property_comparison without operator
                resolved_params = []
                for param in node['parameters']:
                    if isinstance(param, dict) and param.get('type') == 'data_field':
                        resolved_params.append(self._get_data_field(param['name'], data))
                    elif isinstance(param, dict) and param.get('type') == 'function_call':
                        resolved_params.append(self._execute_function_call(param, data))
                    elif isinstance(param, dict) and param.get('type') == 'bbands_property':
                        # Handle nested bbands properties
                        resolved_params.append(self._resolve_operand_node(param, data))
                    else:
                        resolved_params.append(param)
                
                # Ensure any *data* parameters (price series) are numpy arrays.
                # bbands_upper/lower/middle(close, period, nbdevup, nbdevdn) takes
                # period/nbdevup/nbdevdn as plain scalars, passed straight through to
                # talib.BBANDS(timeperiod=..., nbdevup=..., nbdevdn=...) -- broadcasting
                # them into full-length arrays here (as this used to do) makes talib
                # raise "only 0-dimensional arrays can be converted to Python scalars",
                # since a TA-Lib timeperiod must be a real scalar, not an array. Leave
                # int/float params untouched; only arrays of data need normalizing.
                for i, param in enumerate(resolved_params):
                    if isinstance(param, (int, float)):
                        continue
                    if not isinstance(param, np.ndarray):
                        if isinstance(param, (list, tuple)):
                            resolved_params[i] = np.asarray(param, dtype=np.float64)
                        elif hasattr(param, 'to_numpy'):
                            # bbands sub-property results (e.g. bbands(...).upper) come
                            # back as pandas Series when the input price data is a
                            # Series, which it always is when called from a DataFrame
                            # column -- not just a corner case of one index type.
                            resolved_params[i] = param.to_numpy(dtype=np.float64)
                        else:
                            raise ValueError(f"Invalid parameter type for bbands: {type(param)}")
                
                prop = node['property']
                if prop == 'upper':
                    result = self.function_registry.get_function('bbands_upper')(*resolved_params)
                elif prop == 'lower':
                    result = self.function_registry.get_function('bbands_lower')(*resolved_params)
                elif prop == 'middle':
                    result = self.function_registry.get_function('bbands_middle')(*resolved_params)
                else:
                    raise ValueError(f"Unknown Bollinger Bands property: {prop}")
                
                # Ensure result is a numpy array
                if not isinstance(result, np.ndarray):
                    raise ValueError(f"bbands_{prop} returned {type(result)}, expected numpy array")
                
                return result
            if ntype == 'macd_property':
                # Handle MACD property access (histogram, signal, macd)
                resolved_params = []
                for param in node['parameters']:
                    if isinstance(param, dict) and param.get('type') == 'data_field':
                        resolved_params.append(self._get_data_field(param['name'], data))
                    elif isinstance(param, dict) and param.get('type') == 'function_call':
                        resolved_params.append(self._execute_function_call(param, data))
                    else:
                        resolved_params.append(param)
                
                # Ensure all parameters are numpy arrays
                for i, param in enumerate(resolved_params):
                    if not isinstance(param, np.ndarray):
                        if isinstance(param, (list, tuple)):
                            resolved_params[i] = np.asarray(param, dtype=np.float64)
                        elif isinstance(param, (int, float)):
                            resolved_params[i] = np.full(len(data.get('close', [])), param, dtype=np.float64)
                        else:
                            raise ValueError(f"Invalid parameter type for MACD: {type(param)}")
                
                # Call the specific MACD function for the requested property
                prop = node['property']
                if prop == 'histogram':
                    result = self.function_registry.get_function('macd_hist')(*resolved_params)
                elif prop == 'signal':
                    result = self.function_registry.get_function('macd_signal')(*resolved_params)
                elif prop == 'macd':
                    result = self.function_registry.get_function('macd')(*resolved_params)
                else:
                    raise ValueError(f"Unknown MACD property: {prop}")
                
                return result
            if ntype == 'literal':
                return self._get_operand_value(node['value'], data)
            if ntype == 'arithmetic_expression':
                return self._execute_arithmetic_expression(node, data)
            # nested comparisons/logicals: evaluate to boolean array
            return self.execute(node, data)
        # plain literal
        return self._get_operand_value(node, data)

    def _execute_arithmetic_comparison(self, parsed: Dict[str, Any], data: Dict[str, np.ndarray]) -> np.ndarray:
        """Execute arithmetic comparison like (A +/- B) <op> C."""
        left1 = self._resolve_operand_node(parsed['left1'], data)
        left2 = self._resolve_operand_node(parsed['left2'], data)
        right = self._resolve_operand_node(parsed['right'], data)
        if parsed['arith_op'] == '+':
            left_expr = left1 + left2
        else:
            left_expr = left1 - left2
        return self._apply_operator(left_expr, parsed['operator'], right)
    
    def _execute_multiplication_comparison(self, parsed: Dict[str, Any], data: Dict[str, np.ndarray]) -> np.ndarray:
        """Execute multiplication/division comparison like (A * / B) <op> C."""
        left1 = self._resolve_operand_node(parsed['left1'], data)
        left2 = self._resolve_operand_node(parsed['left2'], data)
        right = self._resolve_operand_node(parsed['right'], data)
        
        if parsed['arith_op'] == '*':
            left_expr = left1 * left2
        elif parsed['arith_op'] == '/':
            # Avoid division by zero
            left_expr = np.where(left2 != 0, left1 / left2, np.nan)
        else:
            raise ValueError(f"Unsupported arithmetic operator: {parsed['arith_op']}")
            
        return self._apply_operator(left_expr, parsed['operator'], right)
    
    def _execute_function_comparison(self, parsed: Dict[str, Any], data: Dict[str, np.ndarray]) -> np.ndarray:
        """Execute function comparisons (e.g., rsi(close, 14) > 30)"""
        left_values = self._execute_function_call(parsed['left'], data)
        right_values = self._get_operand_value(parsed['right'], data)
        
        return self._apply_operator(left_values, parsed['operator'], right_values)
    
    def _execute_function_vs_function_comparison(self, parsed: Dict[str, Any], data: Dict[str, np.ndarray]) -> np.ndarray:
        """Execute function vs function comparisons (e.g., sma(close, 20) > sma(close, 50))"""
        left_values = self._execute_function_call(parsed['left'], data)
        right_values = self._execute_function_call(parsed['right'], data)
        
        return self._apply_operator(left_values, parsed['operator'], right_values)
    
    def _execute_value_vs_function_comparison(self, parsed: Dict[str, Any], data: Dict[str, np.ndarray]) -> np.ndarray:
        """Execute value vs function comparisons (e.g., 50 > rsi(close, 14))"""
        left_values = self._get_operand_value(parsed['left'], data)
        right_values = self._execute_function_call(parsed['right'], data)
        
        return self._apply_operator(left_values, parsed['operator'], right_values)
    
    def _execute_comparison(self, parsed: Dict[str, Any], data: Dict[str, np.ndarray]) -> np.ndarray:
        """Execute direct comparisons (e.g., close > 1000)"""
        left_values = self._get_operand_value(parsed['left'], data)
        right_values = self._get_operand_value(parsed['right'], data)
        
        return self._apply_operator(left_values, parsed['operator'], right_values)
    
    def _execute_arithmetic_expression(self, expr: Dict[str, Any], data: Dict[str, np.ndarray]) -> np.ndarray:
        """Execute an arithmetic expression like 'bb_upper(close, 20, 2) - close'"""
        left = expr['left']
        operator = expr['operator']
        right = expr['right']
        
        # Resolve left operand
        if isinstance(left, dict):
            if left['type'] == 'data_field':
                left_data = self._get_data_field(left['name'], data)
            elif left['type'] == 'function_call':
                left_data = self._execute_function_call(left, data)
            elif left['type'] == 'arithmetic_expression':
                left_data = self._execute_arithmetic_expression(left, data)
            else:
                left_data = self._resolve_operand_node(left, data)
        else:
            left_data = left
        
        # Resolve right operand
        if isinstance(right, dict):
            if right['type'] == 'data_field':
                right_data = self._get_data_field(right['name'], data)
            elif right['type'] == 'function_call':
                right_data = self._execute_function_call(right, data)
            elif right['type'] == 'arithmetic_expression':
                right_data = self._execute_arithmetic_expression(right, data)
            else:
                right_data = self._resolve_operand_node(right, data)
        else:
            right_data = right
        
        # Ensure both operands are numpy arrays
        if not isinstance(left_data, np.ndarray):
            left_data = np.asarray(left_data, dtype=np.float64)
        if not isinstance(right_data, np.ndarray):
            right_data = np.asarray(right_data, dtype=np.float64)
        
        # Align lengths if needed
        # Handle scalar values and 0-dimensional numpy arrays
        def safe_len(arr):
            if hasattr(arr, '__len__'):
                try:
                    return len(arr)
                except TypeError:
                    # Handle 0-dimensional numpy arrays
                    return 1
            return 1
        
        left_len = safe_len(left_data)
        right_len = safe_len(right_data)
        max_len = max(left_len, right_len)
        
        if left_len < max_len:
            left_data = np.pad(left_data, (max_len - left_len, 0), mode='constant', constant_values=np.nan)
        if right_len < max_len:
            right_data = np.pad(right_data, (max_len - right_len, 0), mode='constant', constant_values=np.nan)
        
        # Apply arithmetic operator
        if operator == '+':
            return left_data + right_data
        elif operator == '-':
            return left_data - right_data
        elif operator == '*':
            return left_data * right_data
        elif operator == '/':
            # Avoid division by zero
            return np.where(right_data != 0, left_data / right_data, np.nan)
        else:
            raise ValueError(f"Unsupported arithmetic operator: {operator}")
    
    def _execute_function_call(self, func_call: Dict[str, Any], data: Dict[str, np.ndarray]) -> np.ndarray:
        """Execute a function call"""
        func_name = func_call['name']
        parameters = func_call['parameters']
        
        # Resolve parameters to actual data
        resolved_params = []
        for param in parameters:
            if isinstance(param, dict):
                if param['type'] == 'data_field':
                    resolved_params.append(self._get_data_field(param['name'], data))
                elif param['type'] == 'function_call':
                    # Recursively execute nested function calls
                    resolved_params.append(self._execute_function_call(param, data))
                elif param['type'] == 'arithmetic_expression':
                    # Handle arithmetic expressions like "bb_upper(close, 20, 2) - close"
                    resolved_params.append(self._execute_arithmetic_expression(param, data))
                else:
                    # If param is a nested parsed node (comparison/logical), evaluate to boolean/series
                    resolved_params.append(self._resolve_operand_node(param, data))
            else:
                resolved_params.append(param)
        
        # Call the function
        if not self.function_registry.has_function(func_name):
            raise ValueError(f"Unknown function: {func_name}")
        
        # Special handling for aggregations expecting boolean/numeric series
        if func_name in ('count', 'countstreak') and resolved_params:
            # First parameter can be a boolean condition expression; ensure array
            first = resolved_params[0]
            # If the first param is a parsed condition like crossover/logical/comparison, resolve to boolean array
            if isinstance(parameters[0], dict) and parameters[0].get('type') in (
                'crossover','function_to_function_crossover','logical','function_comparison','function_vs_function','value_vs_function','comparison','bbands_property_comparison','arithmetic_comparison'
            ):
                first = self.execute(parameters[0], data)
            # If first looks like indices, convert to boolean mask
            data_len = len(self._get_data_field('close', data)) if 'close' in data else len(next(iter(data.values())))
            if isinstance(first, (list, tuple, np.ndarray)):
                arr = np.asarray(first)
                if arr.ndim == 1 and arr.dtype.kind in 'iu' and len(arr) < data_len and np.nanmax(arr) < data_len:
                    mask = np.zeros(data_len, dtype=bool)
                    mask[arr.astype(int)] = True
                    first = mask
                elif arr.ndim == 1 and arr.dtype == bool and len(arr) != data_len:
                    # pad to right-align with data length
                    padded = np.zeros(data_len, dtype=bool)
                    padded[-len(arr):] = arr
                    first = padded
            if isinstance(first, (int, float)):
                # broadcast scalar
                first = np.full(data_len, first)
            resolved_params[0] = first

        # Coerce any stray string/list params
        normalized_params = []
        for p in resolved_params:
            if isinstance(p, str):
                name = p.strip().lower()
                if name in ('open','high','low','close','volume'):
                    normalized_params.append(self._get_data_field(name, data))
                else:
                    # Try to parse as a function call string and execute it
                    func_match = None
                    try:
                        # balance parentheses if truncated
                        s = p
                        if s.count('(') > s.count(')'):
                            s = s + ')' * (s.count('(') - s.count(')'))
                        parsed = self._parser._parse_function_call_string(s)
                        if parsed and parsed.get('type') == 'function_call':
                            normalized_params.append(self._execute_function_call(parsed, data))
                            continue
                    except Exception:
                        pass
                    try:
                        # keep numeric params as scalars (int if possible)
                        val_num = float(p)
                        if p.strip().isdigit() or (p.strip().startswith('-') and p.strip()[1:].isdigit()):
                            normalized_params.append(int(val_num))
                        else:
                            normalized_params.append(val_num)
                    except Exception:
                        # leave as-is; function may accept it
                        normalized_params.append(p)
            elif isinstance(p, (list, tuple)):
                try:
                    arr = np.asarray(p, dtype=np.float64)
                    normalized_params.append(arr)
                except Exception:
                    normalized_params.append(p)
            else:
                normalized_params.append(p)
        resolved_params = normalized_params
        func = self.function_registry.get_function(func_name)
        # Fast path for count over boolean series
        if func_name == 'count' and len(resolved_params) >= 2:
            series = np.asarray(resolved_params[0])
            period = int(resolved_params[1])
            if series.dtype == bool and period > 0:
                kernel = np.ones(period, dtype=np.int32)
                conv = np.convolve(series.astype(np.int32), kernel, mode='full')[:len(series)]
                # shift to exclude current by default (exclude_current=True behavior)
                shifted = np.concatenate(([0], conv[:-1]))
                result = shifted.astype(np.float64)
            else:
                result = func(*resolved_params)
        else:
            result = func(*resolved_params)
        # ensure numpy array dtype is numeric where applicable
        if isinstance(result, np.ndarray) and result.dtype.kind == 'O':
            try:
                result = result.astype(np.float64)
            except Exception:
                pass
        return result
    
    def _get_operand_value(self, operand: Any, data: Dict[str, np.ndarray]) -> np.ndarray:
        """Get the value of an operand (data field, literal, or function call)"""
        if isinstance(operand, (int, float)):
            # Use a reliable numeric field to determine the data length
            # Prefer 'close' as it's always present and numeric
            if 'close' in data:
                data_length = len(data['close'])
            else:
                # Fallback to any numeric array field
                for key, value in data.items():
                    if isinstance(value, np.ndarray) and value.dtype.kind in 'fc':
                        data_length = len(value)
                        break
                else:
                    # Last resort: use the first array field
                    data_length = len(next(iter(data.values())))
            
            return np.full(data_length, operand)
        elif isinstance(operand, str):
            name = operand.strip()
            # Direct data field references
            lname = name.lower()
            if lname in ('open','high','low','close','volume'):
                return self._get_data_field(lname, data)
            # Try to parse function call strings like "cum(volume)"
            try:
                # balance parentheses if truncated
                s = name
                if s.count('(') > s.count(')'):
                    s = s + ')' * (s.count('(') - s.count(')'))
                parsed = self._parser._parse_function_call_string(s)
                if parsed and parsed.get('type') == 'function_call':
                    return self._execute_function_call(parsed, data)
            except Exception:
                pass
            # Fallback: broadcast numeric-like strings
            try:
                val = float(name)
                return self._get_operand_value(val, data)
            except Exception:
                raise ValueError(f"Invalid operand: {operand}")
        elif isinstance(operand, dict):
            if operand['type'] == 'data_field':
                return self._get_data_field(operand['name'], data)
            elif operand['type'] == 'identifier':
                # Try to interpret identifier name as a function call string (e.g., "cum(volume)")
                name = str(operand.get('name', '')).strip()
                try:
                    s = name
                    if s.count('(') > s.count(')'):
                        s = s + ')' * (s.count('(') - s.count(')'))
                    parsed = self._parser._parse_function_call_string(s)
                    if parsed and parsed.get('type') == 'function_call':
                        return self._execute_function_call(parsed, data)
                except Exception:
                    pass
                # Fallback to data field access by lowercasing common fields
                lname = name.lower()
                if lname in ('open','high','low','close','volume'):
                    return self._get_data_field(lname, data)
                raise ValueError(f"Invalid operand: {name}")
            elif operand['type'] == 'function_call':
                return self._execute_function_call(operand, data)
            elif operand['type'] == 'literal':
                return self._get_operand_value(operand['value'], data)
            elif operand['type'] == 'bbands_property':
                # compute the requested band series
                resolved_params = []
                for param in operand['parameters']:
                    if isinstance(param, dict) and param.get('type') == 'data_field':
                        resolved_params.append(self._get_data_field(param['name'], data))
                    elif isinstance(param, dict) and param.get('type') == 'function_call':
                        resolved_params.append(self._execute_function_call(param, data))
                    else:
                        resolved_params.append(param)
                prop = operand['property']
                if prop == 'upper':
                    return self.function_registry.get_function('bbands_upper')(*resolved_params)
                if prop == 'lower':
                    return self.function_registry.get_function('bbands_lower')(*resolved_params)
                if prop == 'middle':
                    return self.function_registry.get_function('bbands_middle')(*resolved_params)
                raise ValueError(f"Unknown Bollinger Bands property: {prop}")
            elif operand['type'] == 'macd_property':
                # Handle MACD property access (histogram, signal, macd)
                resolved_params = []
                for param in operand['parameters']:
                    if isinstance(param, dict) and param.get('type') == 'data_field':
                        resolved_params.append(self._get_data_field(param['name'], data))
                    elif isinstance(param, dict) and param.get('type') == 'function_call':
                        resolved_params.append(self._execute_function_call(param, data))
                    else:
                        resolved_params.append(param)
                
                # Call the specific MACD function for the requested property
                prop = operand['property']
                if prop == 'histogram':
                    result = self.function_registry.get_function('macd_hist')(*resolved_params)
                elif prop == 'signal':
                    result = self.function_registry.get_function('macd_signal')(*resolved_params)
                elif prop == 'macd':
                    result = self.function_registry.get_function('macd')(*resolved_params)
                else:
                    raise ValueError(f"Unknown MACD property: {prop}")
                
                return result
            elif operand['type'] == 'arithmetic_expression':
                return self._execute_arithmetic_expression(operand, data)
            else:
                raise ValueError(f"Unknown operand type: {operand['type']}")
        else:
            raise ValueError(f"Invalid operand: {operand}")
    
    def _get_data_field(self, field_name: str, data: Dict[str, np.ndarray]) -> np.ndarray:
        """Get a data field from the data dictionary"""
        if field_name in data:
            return data[field_name]
        # Derived fields
        if field_name == 'hl2':
            return (self._get_data_field('high', data) + self._get_data_field('low', data)) / 2.0
        if field_name == 'hlc3':
            return (self._get_data_field('high', data) + self._get_data_field('low', data) + self._get_data_field('close', data)) / 3.0
            raise ValueError(f"Data field not found: {field_name}")
    
    def _apply_operator(self, left: np.ndarray, operator: str, right: np.ndarray) -> np.ndarray:
        """Apply a comparison operator to two arrays"""
        # Align lengths if different
        if hasattr(left, '__len__') and hasattr(right, '__len__'):
            len_l = len(left)
            len_r = len(right)
            if len_l != len_r:
                max_len = max(len_l, len_r)
                def pad(arr, target):
                    if len(arr) == target:
                        return arr
                    out = np.full(target, np.nan)
                    out[-len(arr):] = arr
                    return out
                left = pad(left, max_len)
                right = pad(right, max_len)
        if operator == '>':
            return left > right
        elif operator == '<':
            return left < right
        elif operator == '>=':
            return left >= right
        elif operator == '<=':
            return left <= right
        elif operator == '==':
            return left == right
        elif operator == '!=':
            return left != right
        else:
            raise ValueError(f"Unknown operator: {operator}")
    
    def validate_strategy(self, parsed_strategy: Dict[str, Any]) -> bool:
        """Validate a parsed strategy structure"""
        try:
            # This is a basic validation - we could add more sophisticated checks
            if not parsed_strategy or 'type' not in parsed_strategy:
                return False
            
            strategy_type = parsed_strategy['type']
            if strategy_type == 'logical':
                return ('operator' in parsed_strategy and 
                       'left' in parsed_strategy and 
                       'right' in parsed_strategy)
            elif strategy_type in ['crossover', 'function_comparison', 'function_vs_function', 
                                 'value_vs_function', 'comparison']:
                return True
            else:
                return False
        except Exception:
            return False
    
    def _execute_multi_timeframe_condition(self, parsed: Dict[str, Any], data: Dict[str, Any]) -> np.ndarray:
        """Execute multi-timeframe conditions (e.g., tf(condition, 'weekly')).

        Evaluates the inner condition on the daily series, then OR-reduces it inside
        each calendar bucket (week/month/year) and broadcasts that back out to a
        daily boolean mask, via FunctionRegistry._tf. 'daily' is a no-op pass-through
        by design. This previously just returned the daily result unchanged for every
        timeframe -- tf() was parsed correctly but never actually applied."""
        timeframe = parsed['timeframe']
        inner_condition = parsed['condition']

        result = self.execute(inner_condition, data)

        tf_func = self.function_registry.get_function('tf')
        return tf_func(result, timeframe) 