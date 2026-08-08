# Generated from grammar/Strategy.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,14,96,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,5,
        1,30,8,1,10,1,12,1,33,9,1,1,2,1,2,1,2,1,2,1,2,1,2,5,2,41,8,2,10,
        2,12,2,44,9,2,1,3,1,3,1,3,1,3,1,3,3,3,51,8,3,1,4,1,4,1,4,1,4,3,4,
        57,8,4,1,4,1,4,1,4,1,4,3,4,63,8,4,3,4,65,8,4,1,5,1,5,1,5,1,5,1,5,
        1,6,1,6,1,6,5,6,75,8,6,10,6,12,6,78,9,6,1,6,3,6,81,8,6,1,7,1,7,3,
        7,85,8,7,1,8,1,8,1,8,1,8,1,8,3,8,92,8,8,1,9,1,9,1,9,0,2,2,4,10,0,
        2,4,6,8,10,12,14,16,18,0,0,98,0,20,1,0,0,0,2,23,1,0,0,0,4,34,1,0,
        0,0,6,50,1,0,0,0,8,64,1,0,0,0,10,66,1,0,0,0,12,80,1,0,0,0,14,84,
        1,0,0,0,16,91,1,0,0,0,18,93,1,0,0,0,20,21,3,2,1,0,21,22,5,0,0,1,
        22,1,1,0,0,0,23,24,6,1,-1,0,24,25,3,4,2,0,25,31,1,0,0,0,26,27,10,
        2,0,0,27,28,5,2,0,0,28,30,3,4,2,0,29,26,1,0,0,0,30,33,1,0,0,0,31,
        29,1,0,0,0,31,32,1,0,0,0,32,3,1,0,0,0,33,31,1,0,0,0,34,35,6,2,-1,
        0,35,36,3,6,3,0,36,42,1,0,0,0,37,38,10,2,0,0,38,39,5,1,0,0,39,41,
        3,6,3,0,40,37,1,0,0,0,41,44,1,0,0,0,42,40,1,0,0,0,42,43,1,0,0,0,
        43,5,1,0,0,0,44,42,1,0,0,0,45,51,3,8,4,0,46,47,5,8,0,0,47,48,3,2,
        1,0,48,49,5,9,0,0,49,51,1,0,0,0,50,45,1,0,0,0,50,46,1,0,0,0,51,7,
        1,0,0,0,52,53,3,10,5,0,53,56,3,16,8,0,54,57,5,12,0,0,55,57,3,10,
        5,0,56,54,1,0,0,0,56,55,1,0,0,0,57,65,1,0,0,0,58,59,3,18,9,0,59,
        62,3,16,8,0,60,63,5,12,0,0,61,63,3,10,5,0,62,60,1,0,0,0,62,61,1,
        0,0,0,63,65,1,0,0,0,64,52,1,0,0,0,64,58,1,0,0,0,65,9,1,0,0,0,66,
        67,3,18,9,0,67,68,5,8,0,0,68,69,3,12,6,0,69,70,5,9,0,0,70,11,1,0,
        0,0,71,76,3,14,7,0,72,73,5,10,0,0,73,75,3,14,7,0,74,72,1,0,0,0,75,
        78,1,0,0,0,76,74,1,0,0,0,76,77,1,0,0,0,77,81,1,0,0,0,78,76,1,0,0,
        0,79,81,1,0,0,0,80,71,1,0,0,0,80,79,1,0,0,0,81,13,1,0,0,0,82,85,
        3,18,9,0,83,85,5,12,0,0,84,82,1,0,0,0,84,83,1,0,0,0,85,15,1,0,0,
        0,86,92,5,3,0,0,87,92,5,4,0,0,88,92,5,5,0,0,89,92,5,6,0,0,90,92,
        5,7,0,0,91,86,1,0,0,0,91,87,1,0,0,0,91,88,1,0,0,0,91,89,1,0,0,0,
        91,90,1,0,0,0,92,17,1,0,0,0,93,94,5,11,0,0,94,19,1,0,0,0,10,31,42,
        50,56,62,64,76,80,84,91
    ]

class StrategyParser ( Parser ):

    grammarFileName = "Strategy.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "'>'", "'<'", 
                     "'>='", "'<='", "'=='", "'('", "')'", "','" ]

    symbolicNames = [ "<INVALID>", "AND", "OR", "GT", "LT", "GTE", "LTE", 
                      "EQ", "LPAREN", "RPAREN", "COMMA", "IDENTIFIER", "NUMBER", 
                      "WHITESPACE", "COMMENT" ]

    RULE_strategy = 0
    RULE_orExpr = 1
    RULE_andExpr = 2
    RULE_comparisonExpr = 3
    RULE_comparison = 4
    RULE_function_call = 5
    RULE_parameters = 6
    RULE_parameter = 7
    RULE_operator = 8
    RULE_identifier = 9

    ruleNames =  [ "strategy", "orExpr", "andExpr", "comparisonExpr", "comparison", 
                   "function_call", "parameters", "parameter", "operator", 
                   "identifier" ]

    EOF = Token.EOF
    AND=1
    OR=2
    GT=3
    LT=4
    GTE=5
    LTE=6
    EQ=7
    LPAREN=8
    RPAREN=9
    COMMA=10
    IDENTIFIER=11
    NUMBER=12
    WHITESPACE=13
    COMMENT=14

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class StrategyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def orExpr(self):
            return self.getTypedRuleContext(StrategyParser.OrExprContext,0)


        def EOF(self):
            return self.getToken(StrategyParser.EOF, 0)

        def getRuleIndex(self):
            return StrategyParser.RULE_strategy

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStrategy" ):
                listener.enterStrategy(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStrategy" ):
                listener.exitStrategy(self)




    def strategy(self):

        localctx = StrategyParser.StrategyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_strategy)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 20
            self.orExpr(0)
            self.state = 21
            self.match(StrategyParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OrExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return StrategyParser.RULE_orExpr

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class AndExpressionPassContext(OrExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a StrategyParser.OrExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def andExpr(self):
            return self.getTypedRuleContext(StrategyParser.AndExprContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAndExpressionPass" ):
                listener.enterAndExpressionPass(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAndExpressionPass" ):
                listener.exitAndExpressionPass(self)


    class OrExpressionContext(OrExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a StrategyParser.OrExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def orExpr(self):
            return self.getTypedRuleContext(StrategyParser.OrExprContext,0)

        def OR(self):
            return self.getToken(StrategyParser.OR, 0)
        def andExpr(self):
            return self.getTypedRuleContext(StrategyParser.AndExprContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOrExpression" ):
                listener.enterOrExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOrExpression" ):
                listener.exitOrExpression(self)



    def orExpr(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = StrategyParser.OrExprContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 2
        self.enterRecursionRule(localctx, 2, self.RULE_orExpr, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            localctx = StrategyParser.AndExpressionPassContext(self, localctx)
            self._ctx = localctx
            _prevctx = localctx

            self.state = 24
            self.andExpr(0)
            self._ctx.stop = self._input.LT(-1)
            self.state = 31
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,0,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = StrategyParser.OrExpressionContext(self, StrategyParser.OrExprContext(self, _parentctx, _parentState))
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_orExpr)
                    self.state = 26
                    if not self.precpred(self._ctx, 2):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                    self.state = 27
                    self.match(StrategyParser.OR)
                    self.state = 28
                    self.andExpr(0) 
                self.state = 33
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,0,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class AndExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return StrategyParser.RULE_andExpr

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class AndExpressionContext(AndExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a StrategyParser.AndExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def andExpr(self):
            return self.getTypedRuleContext(StrategyParser.AndExprContext,0)

        def AND(self):
            return self.getToken(StrategyParser.AND, 0)
        def comparisonExpr(self):
            return self.getTypedRuleContext(StrategyParser.ComparisonExprContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAndExpression" ):
                listener.enterAndExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAndExpression" ):
                listener.exitAndExpression(self)


    class ComparisonPassContext(AndExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a StrategyParser.AndExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def comparisonExpr(self):
            return self.getTypedRuleContext(StrategyParser.ComparisonExprContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterComparisonPass" ):
                listener.enterComparisonPass(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitComparisonPass" ):
                listener.exitComparisonPass(self)



    def andExpr(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = StrategyParser.AndExprContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 4
        self.enterRecursionRule(localctx, 4, self.RULE_andExpr, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            localctx = StrategyParser.ComparisonPassContext(self, localctx)
            self._ctx = localctx
            _prevctx = localctx

            self.state = 35
            self.comparisonExpr()
            self._ctx.stop = self._input.LT(-1)
            self.state = 42
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,1,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = StrategyParser.AndExpressionContext(self, StrategyParser.AndExprContext(self, _parentctx, _parentState))
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_andExpr)
                    self.state = 37
                    if not self.precpred(self._ctx, 2):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                    self.state = 38
                    self.match(StrategyParser.AND)
                    self.state = 39
                    self.comparisonExpr() 
                self.state = 44
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class ComparisonExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return StrategyParser.RULE_comparisonExpr

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class ParenthesizedExpressionContext(ComparisonExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a StrategyParser.ComparisonExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def LPAREN(self):
            return self.getToken(StrategyParser.LPAREN, 0)
        def orExpr(self):
            return self.getTypedRuleContext(StrategyParser.OrExprContext,0)

        def RPAREN(self):
            return self.getToken(StrategyParser.RPAREN, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParenthesizedExpression" ):
                listener.enterParenthesizedExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParenthesizedExpression" ):
                listener.exitParenthesizedExpression(self)


    class ComparisonExpressionContext(ComparisonExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a StrategyParser.ComparisonExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def comparison(self):
            return self.getTypedRuleContext(StrategyParser.ComparisonContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterComparisonExpression" ):
                listener.enterComparisonExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitComparisonExpression" ):
                listener.exitComparisonExpression(self)



    def comparisonExpr(self):

        localctx = StrategyParser.ComparisonExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_comparisonExpr)
        try:
            self.state = 50
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [11]:
                localctx = StrategyParser.ComparisonExpressionContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 45
                self.comparison()
                pass
            elif token in [8]:
                localctx = StrategyParser.ParenthesizedExpressionContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 46
                self.match(StrategyParser.LPAREN)
                self.state = 47
                self.orExpr(0)
                self.state = 48
                self.match(StrategyParser.RPAREN)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ComparisonContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return StrategyParser.RULE_comparison

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class FunctionComparisonContext(ComparisonContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a StrategyParser.ComparisonContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def function_call(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(StrategyParser.Function_callContext)
            else:
                return self.getTypedRuleContext(StrategyParser.Function_callContext,i)

        def operator(self):
            return self.getTypedRuleContext(StrategyParser.OperatorContext,0)

        def NUMBER(self):
            return self.getToken(StrategyParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFunctionComparison" ):
                listener.enterFunctionComparison(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFunctionComparison" ):
                listener.exitFunctionComparison(self)


    class ValueComparisonContext(ComparisonContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a StrategyParser.ComparisonContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def identifier(self):
            return self.getTypedRuleContext(StrategyParser.IdentifierContext,0)

        def operator(self):
            return self.getTypedRuleContext(StrategyParser.OperatorContext,0)

        def NUMBER(self):
            return self.getToken(StrategyParser.NUMBER, 0)
        def function_call(self):
            return self.getTypedRuleContext(StrategyParser.Function_callContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterValueComparison" ):
                listener.enterValueComparison(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitValueComparison" ):
                listener.exitValueComparison(self)



    def comparison(self):

        localctx = StrategyParser.ComparisonContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_comparison)
        try:
            self.state = 64
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,5,self._ctx)
            if la_ == 1:
                localctx = StrategyParser.FunctionComparisonContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 52
                self.function_call()
                self.state = 53
                self.operator()
                self.state = 56
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [12]:
                    self.state = 54
                    self.match(StrategyParser.NUMBER)
                    pass
                elif token in [11]:
                    self.state = 55
                    self.function_call()
                    pass
                else:
                    raise NoViableAltException(self)

                pass

            elif la_ == 2:
                localctx = StrategyParser.ValueComparisonContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 58
                self.identifier()
                self.state = 59
                self.operator()
                self.state = 62
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [12]:
                    self.state = 60
                    self.match(StrategyParser.NUMBER)
                    pass
                elif token in [11]:
                    self.state = 61
                    self.function_call()
                    pass
                else:
                    raise NoViableAltException(self)

                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Function_callContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier(self):
            return self.getTypedRuleContext(StrategyParser.IdentifierContext,0)


        def LPAREN(self):
            return self.getToken(StrategyParser.LPAREN, 0)

        def parameters(self):
            return self.getTypedRuleContext(StrategyParser.ParametersContext,0)


        def RPAREN(self):
            return self.getToken(StrategyParser.RPAREN, 0)

        def getRuleIndex(self):
            return StrategyParser.RULE_function_call

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFunction_call" ):
                listener.enterFunction_call(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFunction_call" ):
                listener.exitFunction_call(self)




    def function_call(self):

        localctx = StrategyParser.Function_callContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_function_call)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 66
            self.identifier()
            self.state = 67
            self.match(StrategyParser.LPAREN)
            self.state = 68
            self.parameters()
            self.state = 69
            self.match(StrategyParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ParametersContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def parameter(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(StrategyParser.ParameterContext)
            else:
                return self.getTypedRuleContext(StrategyParser.ParameterContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(StrategyParser.COMMA)
            else:
                return self.getToken(StrategyParser.COMMA, i)

        def getRuleIndex(self):
            return StrategyParser.RULE_parameters

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParameters" ):
                listener.enterParameters(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParameters" ):
                listener.exitParameters(self)




    def parameters(self):

        localctx = StrategyParser.ParametersContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_parameters)
        self._la = 0 # Token type
        try:
            self.state = 80
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [11, 12]:
                self.enterOuterAlt(localctx, 1)
                self.state = 71
                self.parameter()
                self.state = 76
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==10:
                    self.state = 72
                    self.match(StrategyParser.COMMA)
                    self.state = 73
                    self.parameter()
                    self.state = 78
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass
            elif token in [9]:
                self.enterOuterAlt(localctx, 2)

                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ParameterContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier(self):
            return self.getTypedRuleContext(StrategyParser.IdentifierContext,0)


        def NUMBER(self):
            return self.getToken(StrategyParser.NUMBER, 0)

        def getRuleIndex(self):
            return StrategyParser.RULE_parameter

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParameter" ):
                listener.enterParameter(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParameter" ):
                listener.exitParameter(self)




    def parameter(self):

        localctx = StrategyParser.ParameterContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_parameter)
        try:
            self.state = 84
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [11]:
                self.enterOuterAlt(localctx, 1)
                self.state = 82
                self.identifier()
                pass
            elif token in [12]:
                self.enterOuterAlt(localctx, 2)
                self.state = 83
                self.match(StrategyParser.NUMBER)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OperatorContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return StrategyParser.RULE_operator

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class LessThanContext(OperatorContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a StrategyParser.OperatorContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def LT(self):
            return self.getToken(StrategyParser.LT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLessThan" ):
                listener.enterLessThan(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLessThan" ):
                listener.exitLessThan(self)


    class GreaterThanContext(OperatorContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a StrategyParser.OperatorContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def GT(self):
            return self.getToken(StrategyParser.GT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGreaterThan" ):
                listener.enterGreaterThan(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGreaterThan" ):
                listener.exitGreaterThan(self)


    class EqualContext(OperatorContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a StrategyParser.OperatorContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def EQ(self):
            return self.getToken(StrategyParser.EQ, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEqual" ):
                listener.enterEqual(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEqual" ):
                listener.exitEqual(self)


    class GreaterThanEqualContext(OperatorContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a StrategyParser.OperatorContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def GTE(self):
            return self.getToken(StrategyParser.GTE, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGreaterThanEqual" ):
                listener.enterGreaterThanEqual(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGreaterThanEqual" ):
                listener.exitGreaterThanEqual(self)


    class LessThanEqualContext(OperatorContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a StrategyParser.OperatorContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def LTE(self):
            return self.getToken(StrategyParser.LTE, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLessThanEqual" ):
                listener.enterLessThanEqual(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLessThanEqual" ):
                listener.exitLessThanEqual(self)



    def operator(self):

        localctx = StrategyParser.OperatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_operator)
        try:
            self.state = 91
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [3]:
                localctx = StrategyParser.GreaterThanContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 86
                self.match(StrategyParser.GT)
                pass
            elif token in [4]:
                localctx = StrategyParser.LessThanContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 87
                self.match(StrategyParser.LT)
                pass
            elif token in [5]:
                localctx = StrategyParser.GreaterThanEqualContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 88
                self.match(StrategyParser.GTE)
                pass
            elif token in [6]:
                localctx = StrategyParser.LessThanEqualContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 89
                self.match(StrategyParser.LTE)
                pass
            elif token in [7]:
                localctx = StrategyParser.EqualContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 90
                self.match(StrategyParser.EQ)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IdentifierContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(StrategyParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return StrategyParser.RULE_identifier

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIdentifier" ):
                listener.enterIdentifier(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIdentifier" ):
                listener.exitIdentifier(self)




    def identifier(self):

        localctx = StrategyParser.IdentifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_identifier)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 93
            self.match(StrategyParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[1] = self.orExpr_sempred
        self._predicates[2] = self.andExpr_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def orExpr_sempred(self, localctx:OrExprContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 2)
         

    def andExpr_sempred(self, localctx:AndExprContext, predIndex:int):
            if predIndex == 1:
                return self.precpred(self._ctx, 2)
         




