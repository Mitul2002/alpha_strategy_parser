grammar Strategy;

// Parser Rules
strategy: orExpr EOF;

orExpr: 
    orExpr OR andExpr    # OrExpression
    | andExpr            # AndExpressionPass
    ;

andExpr: 
    andExpr AND comparisonExpr  # AndExpression
    | comparisonExpr            # ComparisonPass
    ;

comparisonExpr:
    comparison                # ComparisonExpression
    | LPAREN orExpr RPAREN    # ParenthesizedExpression
    ;

comparison:
    function_call operator (NUMBER | function_call)  # FunctionComparison
    | identifier operator (NUMBER | function_call)   # ValueComparison
    ;

function_call:
    identifier LPAREN parameters RPAREN;

parameters:
    parameter (COMMA parameter)*
    | /* empty */
    ;

parameter:
    identifier
    | NUMBER
    ;

operator:
    GT      # GreaterThan
    | LT    # LessThan
    | GTE   # GreaterThanEqual
    | LTE   # LessThanEqual
    | EQ    # Equal
    ;

identifier: IDENTIFIER;

// Lexer Rules
AND: 'AND' | 'and';
OR: 'OR' | 'or';
GT: '>';
LT: '<';
GTE: '>=';
LTE: '<=';
EQ: '==';

LPAREN: '(';
RPAREN: ')';
COMMA: ',';

IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]*;
NUMBER: [0-9]+ ('.' [0-9]+)?;

WHITESPACE: [ \t\r\n]+ -> skip;
COMMENT: '//' ~[\r\n]* -> skip; 