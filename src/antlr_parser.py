import sys
import os
from typing import Dict, Any, Optional, Union
import numpy as np

# Import generated ANTLR4 classes
from grammar.StrategyLexer import StrategyLexer
from grammar.StrategyParser import StrategyParser
from grammar.StrategyListener import StrategyListener
from antlr4 import InputStream, CommonTokenStream, ParseTreeWalker

class StrategyListenerImpl(StrategyListener):
    """Custom listener to build the parsed strategy structure"""
    
    def __init__(self):
        self.result = None
        self.current_node = None
        self.node_stack = []
    
    def enterStrategy(self, ctx):
        """Entry point for strategy parsing"""
        pass
    
    def exitStrategy(self, ctx):
        """Exit point - result is the root expression"""
        self.result = self.current_node
    
    def enterOrExpression(self, ctx):
        """Handle OR expressions"""
        if ctx.OR():  # Only create node if there's an OR operator
            node = {
                'type': 'or',
                'left': None,
                'right': None
            }
            self.node_stack.append(node)
            self.current_node = node
    
    def exitOrExpression(self, ctx):
        """Complete OR expression"""
        if ctx.OR() and len(self.node_stack) > 1:
            parent = self.node_stack[-2]
            if parent.get('left') is None:
                parent['left'] = self.current_node
            else:
                parent['right'] = self.current_node
            self.current_node = self.node_stack.pop()
    
    def enterAndExpression(self, ctx):
        """Handle AND expressions"""
        if ctx.AND():  # Only create node if there's an AND operator
            node = {
                'type': 'and',
                'left': None,
                'right': None
            }
            self.node_stack.append(node)
            self.current_node = node
    
    def exitAndExpression(self, ctx):
        """Complete AND expression"""
        if ctx.AND() and len(self.node_stack) > 1:
            parent = self.node_stack[-2]
            if parent.get('left') is None:
                parent['left'] = self.current_node
            else:
                parent['right'] = self.current_node
            self.current_node = self.node_stack.pop()
    
    def enterComparisonExpression(self, ctx):
        """Handle comparison expressions"""
        pass
    
    def exitComparisonExpression(self, ctx):
        """Complete comparison expression"""
        pass
    
    def enterAndExpressionPass(self, ctx):
        """Handle AND expression pass through"""
        pass
    
    def exitAndExpressionPass(self, ctx):
        """Complete AND expression pass through"""
        pass
    
    def enterOrExpressionPass(self, ctx):
        """Handle OR expression pass through"""
        pass
    
    def exitOrExpressionPass(self, ctx):
        """Complete OR expression pass through"""
        pass
    
    def enterComparisonPass(self, ctx):
        """Handle comparison pass through"""
        pass
    
    def exitComparisonPass(self, ctx):
        """Complete comparison pass through"""
        pass
    
    def enterFunctionComparison(self, ctx):
        """Handle function vs function comparisons"""
        node = {
            'type': 'function_comparison',
            'left_function': ctx.function_call(0).identifier().getText(),
            'left_parameters': self._extract_parameters(ctx.function_call(0).parameters()),
            'operator': ctx.operator().getText(),
            'right_function': None,
            'right_parameters': None,
            'right_value': None
        }
        
        # Check if right side is function or value
        if ctx.function_call(1):
            node['right_function'] = ctx.function_call(1).identifier().getText()
            node['right_parameters'] = self._extract_parameters(ctx.function_call(1).parameters())
        else:
            node['right_value'] = float(ctx.NUMBER().getText())
        
        self.current_node = node
    
    def enterValueComparison(self, ctx):
        """Handle value vs function comparisons"""
        node = {
            'type': 'value_comparison',
            'value_name': ctx.identifier().getText(),
            'operator': ctx.operator().getText(),
            'function': None,
            'parameters': None,
            'value': None
        }
        
        # Check if right side is function or value
        if ctx.function_call():
            node['function'] = ctx.function_call().identifier().getText()
            node['parameters'] = self._extract_parameters(ctx.function_call().parameters())
        else:
            node['value'] = float(ctx.NUMBER().getText())
        
        self.current_node = node
    
    def enterParenthesizedExpression(self, ctx):
        """Handle parenthesized expressions"""
        pass
    
    def exitParenthesizedExpression(self, ctx):
        """Complete parenthesized expression"""
        pass
    
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

class ANTLRStrategyParser:
    """ANTLR4-based strategy parser with AND/OR logic support"""
    
    def __init__(self):
        self.lexer = None
        self.parser = None
        self.walker = ParseTreeWalker()
    
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
            
            # Create listener and walk the tree
            listener = StrategyListenerImpl()
            self.walker.walk(listener, tree)
            
            return listener.result
            
        except Exception as e:
            print(f"ANTLR4 parsing error: {e}")
            return None
    
    def validate(self, strategy: str) -> bool:
        """Validate if strategy can be parsed"""
        try:
            result = self.parse(strategy)
            return result is not None
        except:
            return False

def test_antlr_parser():
    """Test the ANTLR4 parser with various strategies"""
    parser = ANTLRStrategyParser()
    
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
    
    print("🧪 Testing ANTLR4 Parser")
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
    
    print(f"\n🎉 ANTLR4 Parser Test Complete!")

if __name__ == "__main__":
    test_antlr_parser() 