# Generated from grammar/Strategy.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .StrategyParser import StrategyParser
else:
    from StrategyParser import StrategyParser

# This class defines a complete listener for a parse tree produced by StrategyParser.
class StrategyListener(ParseTreeListener):

    # Enter a parse tree produced by StrategyParser#strategy.
    def enterStrategy(self, ctx:StrategyParser.StrategyContext):
        pass

    # Exit a parse tree produced by StrategyParser#strategy.
    def exitStrategy(self, ctx:StrategyParser.StrategyContext):
        pass


    # Enter a parse tree produced by StrategyParser#AndExpressionPass.
    def enterAndExpressionPass(self, ctx:StrategyParser.AndExpressionPassContext):
        pass

    # Exit a parse tree produced by StrategyParser#AndExpressionPass.
    def exitAndExpressionPass(self, ctx:StrategyParser.AndExpressionPassContext):
        pass


    # Enter a parse tree produced by StrategyParser#OrExpression.
    def enterOrExpression(self, ctx:StrategyParser.OrExpressionContext):
        pass

    # Exit a parse tree produced by StrategyParser#OrExpression.
    def exitOrExpression(self, ctx:StrategyParser.OrExpressionContext):
        pass


    # Enter a parse tree produced by StrategyParser#AndExpression.
    def enterAndExpression(self, ctx:StrategyParser.AndExpressionContext):
        pass

    # Exit a parse tree produced by StrategyParser#AndExpression.
    def exitAndExpression(self, ctx:StrategyParser.AndExpressionContext):
        pass


    # Enter a parse tree produced by StrategyParser#ComparisonPass.
    def enterComparisonPass(self, ctx:StrategyParser.ComparisonPassContext):
        pass

    # Exit a parse tree produced by StrategyParser#ComparisonPass.
    def exitComparisonPass(self, ctx:StrategyParser.ComparisonPassContext):
        pass


    # Enter a parse tree produced by StrategyParser#ComparisonExpression.
    def enterComparisonExpression(self, ctx:StrategyParser.ComparisonExpressionContext):
        pass

    # Exit a parse tree produced by StrategyParser#ComparisonExpression.
    def exitComparisonExpression(self, ctx:StrategyParser.ComparisonExpressionContext):
        pass


    # Enter a parse tree produced by StrategyParser#ParenthesizedExpression.
    def enterParenthesizedExpression(self, ctx:StrategyParser.ParenthesizedExpressionContext):
        pass

    # Exit a parse tree produced by StrategyParser#ParenthesizedExpression.
    def exitParenthesizedExpression(self, ctx:StrategyParser.ParenthesizedExpressionContext):
        pass


    # Enter a parse tree produced by StrategyParser#FunctionComparison.
    def enterFunctionComparison(self, ctx:StrategyParser.FunctionComparisonContext):
        pass

    # Exit a parse tree produced by StrategyParser#FunctionComparison.
    def exitFunctionComparison(self, ctx:StrategyParser.FunctionComparisonContext):
        pass


    # Enter a parse tree produced by StrategyParser#ValueComparison.
    def enterValueComparison(self, ctx:StrategyParser.ValueComparisonContext):
        pass

    # Exit a parse tree produced by StrategyParser#ValueComparison.
    def exitValueComparison(self, ctx:StrategyParser.ValueComparisonContext):
        pass


    # Enter a parse tree produced by StrategyParser#function_call.
    def enterFunction_call(self, ctx:StrategyParser.Function_callContext):
        pass

    # Exit a parse tree produced by StrategyParser#function_call.
    def exitFunction_call(self, ctx:StrategyParser.Function_callContext):
        pass


    # Enter a parse tree produced by StrategyParser#parameters.
    def enterParameters(self, ctx:StrategyParser.ParametersContext):
        pass

    # Exit a parse tree produced by StrategyParser#parameters.
    def exitParameters(self, ctx:StrategyParser.ParametersContext):
        pass


    # Enter a parse tree produced by StrategyParser#parameter.
    def enterParameter(self, ctx:StrategyParser.ParameterContext):
        pass

    # Exit a parse tree produced by StrategyParser#parameter.
    def exitParameter(self, ctx:StrategyParser.ParameterContext):
        pass


    # Enter a parse tree produced by StrategyParser#GreaterThan.
    def enterGreaterThan(self, ctx:StrategyParser.GreaterThanContext):
        pass

    # Exit a parse tree produced by StrategyParser#GreaterThan.
    def exitGreaterThan(self, ctx:StrategyParser.GreaterThanContext):
        pass


    # Enter a parse tree produced by StrategyParser#LessThan.
    def enterLessThan(self, ctx:StrategyParser.LessThanContext):
        pass

    # Exit a parse tree produced by StrategyParser#LessThan.
    def exitLessThan(self, ctx:StrategyParser.LessThanContext):
        pass


    # Enter a parse tree produced by StrategyParser#GreaterThanEqual.
    def enterGreaterThanEqual(self, ctx:StrategyParser.GreaterThanEqualContext):
        pass

    # Exit a parse tree produced by StrategyParser#GreaterThanEqual.
    def exitGreaterThanEqual(self, ctx:StrategyParser.GreaterThanEqualContext):
        pass


    # Enter a parse tree produced by StrategyParser#LessThanEqual.
    def enterLessThanEqual(self, ctx:StrategyParser.LessThanEqualContext):
        pass

    # Exit a parse tree produced by StrategyParser#LessThanEqual.
    def exitLessThanEqual(self, ctx:StrategyParser.LessThanEqualContext):
        pass


    # Enter a parse tree produced by StrategyParser#Equal.
    def enterEqual(self, ctx:StrategyParser.EqualContext):
        pass

    # Exit a parse tree produced by StrategyParser#Equal.
    def exitEqual(self, ctx:StrategyParser.EqualContext):
        pass


    # Enter a parse tree produced by StrategyParser#identifier.
    def enterIdentifier(self, ctx:StrategyParser.IdentifierContext):
        pass

    # Exit a parse tree produced by StrategyParser#identifier.
    def exitIdentifier(self, ctx:StrategyParser.IdentifierContext):
        pass



del StrategyParser