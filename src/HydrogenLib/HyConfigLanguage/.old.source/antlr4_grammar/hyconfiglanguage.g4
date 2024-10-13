grammar hyconfiglanguage;

configFile: (definition)* EOF;
definition: tableDef | varDef | importStmt;
tableDef: '[' NAME ']';
varDef: NAME '=' VALUE;
importStmt: ('from' NAME)? 'import' NAME;

NAME: [a-zA-Z_][a-zA-Z_0-9]*;
VALUE: .+?;
WS: [ \t\r\n]+ -> skip;

INDENT: '\n' (' ')+;
