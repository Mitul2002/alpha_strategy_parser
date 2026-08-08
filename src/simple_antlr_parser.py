#!/usr/bin/env python3
"""
Simple ANTLR4-based strategy parser
"""

import sys
import os
from typing import Dict, Any, Optional
import numpy as np

# Import generated ANTLR4 classes
from grammar.StrategyLexer import StrategyLexer
from grammar.StrategyParser import StrategyParser
from antlr4 import InputStream, CommonTokenStream

class SimpleANTLRParser:
    """Simple ANTLR4-based strategy parser"""
    
    def __init__(self):
        self.lexer = None
        self.parser = None
    
    def parse(self, strategy: str) -> Optional[Dict[str, Any]]:
        """Parse strategy string using ANTLR4"""
        try:
            # Create input stream
            input_stream = InputStream(strategy)
            
            # Create lexer
            self.lexer = StrategyLexer(input_stream)
            stream = CommonTokenStream(self.lexer)
            
            # Create parser
            self.parser = StrategyParser(stream)
            
            # Parse the input
            tree = self.parser.strategy()
            
            # Build the strategy structure
            result = self._build_strategy(tree)
            return result
            
        except Exception as e:
            print(f"ANTLR4 parsing error: {e}")
            return None
    
    def _build_strategy(self, tree) -> Dict[str, Any]:
        """Build strategy structure from parse tree"""
        if hasattr(tree, 'orExpr'):
            return self._build_or_expr(tree.orExpr())
        return None
    
    def _build_or_expr(self, ctx) -> Dict[str, Any]:
        """Build OR expression"""
        if hasattr(ctx, 'OR') and ctx.OR():
            # This is an OR expression
            left = self._build_and_expr(ctx.andExpr(0))
            right = self._build_and_expr(ctx.andExpr(1))
            
            return {
                'type': 'or',
                'left': left,
                'right': right
            }
        else:
            # This is just an AND expression
            return self._build_and_expr(ctx.andExpr(0))
    
    def _build_and_expr(self, ctx) -> Dict[str, Any]:
        """Build AND expression"""
        if hasattr(ctx, 'AND') and ctx.AND():
            # This is an AND expression
            left = self._build_comparison_expr(ctx.comparisonExpr(0))
            right = self._build_comparison_expr(ctx.comparisonExpr(1))
            
            return {
                'type': 'and',
                'left': left,
                'right': right
            }
        else:
            # This is just a comparison expression
            return self._build_comparison_expr(ctx.comparisonExpr(0))
    
    def _build_comparison_expr(self, ctx) -> Dict[str, Any]:
        """Build comparison expression"""
        if hasattr(ctx, 'LPAREN') and ctx.LPAREN():
            # This is a parenthesized expression
            return self._build_or_expr(ctx.orExpr())
        else:
            # This is a comparison
            return self._build_comparison(ctx.comparison())
    
    def _build_comparison(self, ctx) -> Dict[str, Any]:
        """Build comparison"""
        if hasattr(ctx, 'function_call') and len(ctx.function_call()) == 2:
            # Function vs function comparison
            left_func = ctx.function_call(0)
            right_func = ctx.function_call(1)
            
            return {
                'type': 'function_comparison',
                'left_function': left_func.identifier().getText(),
                'left_parameters': self._extract_parameters(left_func.parameters()),
                'operator': ctx.operator().getText(),
                'right_function': right_func.identifier().getText(),
                'right_parameters': self._extract_parameters(right_func.parameters()),
                'right_value': None
            }
        elif hasattr(ctx, 'function_call') and len(ctx.function_call()) == 1:
            # Function vs value comparison
            func = ctx.function_call(0)
            value = float(ctx.NUMBER().getText())
            
            return {
                'type': 'function_comparison',
                'left_function': func.identifier().getText(),
                'left_parameters': self._extract_parameters(func.parameters()),
                'operator': ctx.operator().getText(),
                'right_function': None,
                'right_parameters': None,
                'right_value': value
            }
        else:
            # Value vs function comparison
            value_name = ctx.identifier().getText()
            func = ctx.function_call(0)
            
            return {
                'type': 'value_comparison',
                'value_name': value_name,
                'operator': ctx.operator().getText(),
                'function': func.identifier().getText(),
                'parameters': self._extract_parameters(func.parameters()),
                'value': None
            }
    
    def _extract_parameters(self, params_ctx) -> list:
        """Extract parameters from parameters context"""
        if not params_ctx:
            return []
        
        params = []
        for param in params_ctx.parameter():
            if param.identifier():
                params.append(param.identifier().getText())
            elif param.NUMBER():
                params.append(float(param.NUMBER().getText()))
        
        return params

def test_simple_antlr_parser():
    """Test the simple ANTLR4 parser"""
    parser = SimpleANTLRParser()
    
    # Test strategies
    test_strategies = [
        "rsi(close, 14) > 30",
        "sma(close, 20) > sma(close, 50)",
        "close > bbands_lower(close, 20, 2.0)",
        "rsi(close, 14) > 30 AND sma(close, 20) > sma(close, 50)",
        "rsi(close, 14) > 30 OR close > 100",
        "(rsi(close, 14) > 30) AND (sma(close, 20) > sma(close, 50))",
        "rsi(close, 14) > 30 AND sma(close, 20) > sma(close, 50) OR volume > sma(volume, 20)"
    ]
    
    print("🧪 Testing Simple ANTLR4 Parser")
    print("=" * 50)
    
    for i, strategy in enumerate(test_strategies, 1):
        print(f"\nStrategy {i}: {strategy}")
        
        # Parse
        parsed = parser.parse(strategy)
        if parsed:
            print(f"✅ Parsed successfully")
            print(f"   Structure: {parsed}")
        else:
            print(f"❌ Failed to parse")
    
    print(f"\n🎉 Simple ANTLR4 Parser Test Complete!")

if __name__ == "__main__":
    test_simple_antlr_parser() 