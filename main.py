from curses.ascii import isdigit
import sys
import re
symbols = []
class PreProcessor:
    # def __init__(self,source):
    #     self.source = source
    @staticmethod
    def filter(input):
        input = re.sub(r'//.*', '', input)
        input = re.sub(r'/\*.*?\*/', '', input, flags=re.DOTALL)
        return input
    @staticmethod
    def remove_spaces(source):
        source = re.sub(r'[^\S\n]+', '', source)
        return source
    @staticmethod
    def remove_newlines(source):
        source = source.replace('\n','')
        return source
    
class SymbolTable:
    def __init__(self):
        self.symbols = {}
    def get(self, identifier):
        if identifier not in self.symbols:
            raise Exception(f"Identifier {identifier} not declared")
        return self.symbols[identifier][0]
    def set(self, identifier, value, _type):
        if identifier not in self.symbols:
            raise Exception(f"Identifier {identifier} not declared")
        if self.symbols[identifier][1] != _type:
            raise Exception(f"Type mismatch: {self.symbols[identifier][1]} and {_type}")
        self.symbols[identifier] = (value, _type)
    def create(self,identifier, _type):
        if identifier in self.symbols:
            raise Exception(f"Identifier {identifier} already declared")
        self.symbols[identifier] = (None, _type)

class FuncTable:
    def __init__(self):
        self.functions = {}
    def get(self, identifier):
        if identifier not in self.functions:
            raise Exception(f"Function {identifier} not declared")
        return self.functions[identifier]
    def create(self, identifier, value, _type):
        if identifier in self.functions:
            raise Exception(f"Function {identifier} already declared")
        self.functions[identifier] = value
        self.functions[identifier + "return"] = _type

        return self.functions

class Node:
    def __init__(self, value):
        self.value = value
        self.children = []
    def Evaluate(self, symbol_table, func_table=None):
        pass
        # return self.value

class FuncDec(Node):
    def __init__(self, nodes, block, _type):
        super().__init__(None)
        self.children = [ nodes, block]
        self.type = _type
    def Evaluate(self, func_table, symbol_table= None):
        func_table.create(self.children[0][0].value, self.children, self.type)
        symbol_table.create(self.children[0][0].value, 'func')
        symbols.append(self.children[0][0].value)

class FuncCall(Node):
    def __init__(self, identifiers):
        super().__init__(None)
        self.children = identifiers

    def Evaluate(self, func_table, symbol_table = None):
        func_name = self.children[0].value
        dec = func_table.get(func_name)
        if len(dec[0]) != len(self.children):
            raise Exception(f"Expected {len(dec[0])} arguments, got {len(self.children)}")
        local_symbol_table = SymbolTable()
        for i in range(1, len(self.children)):
            result = self.children[i].value
            if (isinstance(self.children[i], StringVal) and  dec[0][i].type != 'string') :
                raise Exception("Type mismatch")
            if (isinstance(self.children[i], IntVal) and  dec[0][i].type != 'int'): 
                raise Exception("Type mismatch")
            

            if not isinstance(self.children[i], Identifier) and not isinstance(self.children[i], Token):
                _result = self.children[i].Evaluate(symbol_table, func_table)
                result = _result[0]
                if _result[1] != dec[0][i].type:
                    raise Exception("Type mismatch")
            if result in symbol_table.symbols:
                result = symbol_table.get(result)[0]
            local_symbol_table.create(dec[0][i].value, dec[0][i].type)
            local_symbol_table.set(dec[0][i].value, (result ,dec[0][i].type), dec[0][i].type)
        if func_name == 'main':
            res = dec[-1].Evaluate(symbol_table, func_table)
        else:   
            res = dec[-1].Evaluate(local_symbol_table, func_table)
        if res != None and res[1] != func_table.get(func_name + "return"):
            raise Exception("Type mismatch")
        return res

class ReturnOP(Node):
    def __init__(self, expression):
        super().__init__(None)
        self.children = expression
    def Evaluate(self, symbol_table,func_table=None):
        if isinstance(self.children, Scanln):
            return self.children.EvaluateReturn(symbol_table)
        # if 
        return self.children.Evaluate(symbol_table)
    
class Block(Node):
    def __init__(self, statements=None):
        super().__init__(None)
        self.children = statements if statements is not None else []
    def Evaluate(self, symbol_table, func_table=None):
        for statement in self.children:
            if statement is not None:
                if isinstance(statement, ReturnOP):
                    return statement.Evaluate(symbol_table, func_table)
            statement.Evaluate(symbol_table=symbol_table, func_table=func_table)
        return

class Assignment(Node):
    def __init__(self, identifier, expression):
        super().__init__(None)
        self.children = [identifier, expression]

    def Evaluate(self, symbol_table, func_table=None):
        identifier = self.children[0].value if isinstance(self.children[0], Identifier) else self.children[0]
        if isinstance(self.children[1], FuncCall):
            value = self.children[1].Evaluate(func_table, symbol_table)
            symbol_table.set(identifier, value, value[1])
        else:
            value = self.children[1].Evaluate(symbol_table)
            symbol_table.set(identifier, value, value[1])
        # printf'Assigning: {identifier} = {value}')

class VarDec(Node):
    def __init__(self, identifier, _type):
        super().__init__(None)
        self.children = [identifier, _type]

    def Evaluate(self, symbol_table, func_table=None):
        identifier = self.children[0].value if isinstance(self.children[0], Identifier) else self.children[0]
        _type = self.children[1].value if isinstance(self.children[1], Identifier) else self.children[1]
        symbol_table.create(identifier, _type)
        #print(f'Assigning: {identifier} = {value}')

class Println(Node):
    def __init__(self, expression):
        super().__init__(None)
        self.children = [expression]

    def Evaluate(self, symbol_table, func_table=None):
        expression_value = self.children[0].Evaluate(symbol_table = symbol_table, func_table = func_table)[0]
        print(expression_value)
        return None
class Scanln(Node):
    def __init__(self, identifier):
        super().__init__(None)
        self.children = [identifier]

    def Evaluate(self, symbol_table):
        identifier = self.children[0].value if isinstance(self.children[0], Identifier) else self.children[0]
        value = (int(input()), 'int')
        symbol_table.set(identifier, value, value[1])
        #printf'Assigning: {identifier} = {value}')
        return None
    def EvaluateReturn(self, symbol_table):
        value = (int(input()), 'int')
        return value
class For(Node):
    def __init__(self, assignment, condition, increment, block):
        super().__init__(None)
        self.children = [assignment, condition, increment, block]

    def Evaluate(self, symbol_table, func_table=None):
        self.children[0].Evaluate(symbol_table=symbol_table, func_table=func_table)
        while self.children[1].Evaluate(symbol_table, func_table)[0]:
            self.children[3].Evaluate(symbol_table, func_table)
            self.children[2].Evaluate(symbol_table, func_table)
        return None

class If(Node):
    def __init__(self, condition, block, else_block=None):
        super().__init__(None)
        self.children = [condition, block, else_block]
    def Evaluate(self, symbol_table, func_table=None):
        if isinstance(self.children[0].children[0], IntVal) and isinstance(self.children[0].children[1], IntVal):
            raise Exception("Invalid operation")
        if self.children[0].Evaluate(symbol_table):
            self.children[1].Evaluate(symbol_table)
        elif self.children[2] is not None:
            self.children[2].Evaluate(symbol_table)
        return None
    
class BinOp(Node):
    def __init__(self, value, left, right):
        super().__init__(value)
        self.children = [left, right]

    def Evaluate(self, symbol_table, func_table=None):
        left = self.children[0].Evaluate(symbol_table=symbol_table, func_table=func_table)
        right = self.children[1].Evaluate(symbol_table=symbol_table, func_table=func_table)
        left_value = left[0]
        right_value = right[0]
        
        #print(f'Operation: {left_value} {self.value.type} {right_value}')
        if self.value.type == 'DOT':
            return (str(left_value) + str(right_value), 'string')
        if left[1] != right[1]:
            raise Exception("Type mismatch")
        if self.value.type == 'LESS_THAN':
            return (int(left_value < right_value), 'int')
        elif self.value.type == 'GREATER_THAN':
            return (int(left_value > right_value), 'int')
        elif self.value.type == 'EQUALS':
            return (int(left_value == right_value), 'int')
        elif self.value.type == 'LOGICAL_AND':
            return (int(left_value and right_value), 'int')
        elif self.value.type == 'LOGICAL_OR':
            return (int(left_value or right_value), 'int')
        if left[1] != 'int' or right[1] != 'int':
            raise Exception("Invalid operation")
        if self.value.type == 'PLUS':
            return (int(left_value + right_value), 'int')
        elif self.value.type == 'MINUS':
            return (int(left_value - right_value), 'int')
        elif self.value.type == 'MULT':
            return (int(left_value * right_value), 'int')
        elif self.value.type == 'DIV':
            if right_value == 0:
                raise Exception("Division by zero")
            return (int(left_value / right_value), 'int')
        else:
            raise Exception("Invalid operation")

class UnOp(Node):
    def __init__(self, value, child):
        super().__init__(value)
        self.value = value
        self.children = [child]

    def Evaluate(self, symbol_table, func_table=None):
        child_value = self.children[0].Evaluate(symbol_table)[0]
        if self.value.type == 'PLUS':
            return (child_value, 'int')
        elif self.value.type == 'MINUS':
            return (-child_value, 'int')
        elif self.value.type == 'LOGICAL_NOT':
            return (not child_value, 'int')
        else:
            raise Exception("Invalid operation")
        
class IntVal(Node):
    def __init__(self, value):
        super().__init__(value)
        self.value = value
    def Evaluate(self, symbol_table, func_table=None):
        return (int(self.value), 'int')
    
class StringVal(Node):
    def __init__(self, value):
        super().__init__(value)
        self.value = value
    def Evaluate(self, symbol_table, func_table=None):
        return (self.value, 'string')
    
class NoOp(Node):
    def __init__(self):
        super().__init__(None)
    def Evaluate(self, symbol_table, func_table=None):
        return None

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

class Identifier(Node):
    def __init__(self, value=None,type=None):
        super().__init__(value)
        self.type = type

    def Evaluate(self, symbol_table, func_table=None):
        identifier_value = self.value
        # identifier_value = self.value if isinstance(self.value, Identifier) else self.value
        value = symbol_table.get(identifier_value)
        # print(f'Fetching value for identifier {identifier_value}: {value}')
        return value
reserved_words = ['stampa', 'se', 'altro', 'per', 'ingresso', 'variabile', 'intero', 'corda', 'bool']
reserved_tokens = [word.upper() for word in reserved_words]
class Tokenizer:
    def __init__(self,source):
        self.source = source
        self.position = 0
        self.next = None
        self.prev_type = None  
    def select_next(self):
        while self.position < len(self.source) and (self.source[self.position] == ' ' or self.source[self.position] == '\n'):
            self.position += 1
        if self.position < len(self.source):
            if self.source[self.position] == '+':
                if self.prev_type is None or self.prev_type in ['PLUS', 'MINUS', 'MULT', 'DIV', 'LPAREN']:
                    self.next = Token('PLUS', None)
                else:
                    self.next = Token('UNARY_PLUS', None)
                self.position += 1
            elif self.source[self.position] == '-':
                if self.prev_type is None or self.prev_type in ['PLUS', 'MINUS', 'MULT', 'DIV', 'LPAREN']:
                    self.next = Token('MINUS', None)
                else:
                    self.next = Token('UNARY_MINUS', None)
                self.position += 1
            elif self.source[self.position] == '*':
                self.next = Token('MULT',None)
                self.position += 1
            elif self.source[self.position] == '/':
                self.next = Token('DIV',None)
                self.position += 1
            elif self.source[self.position] == '(':
                self.next = Token('LPAREN',None)
                self.position += 1
            elif self.source[self.position] == ')':
                self.next = Token('RPAREN',None)
                self.position += 1
            elif self.source[self.position] == '{':
                self.next = Token('LBRACE',None)
                self.position += 1
            elif self.source[self.position] == '}':
                self.next = Token('RBRACE',None)
                self.position += 1
            elif self.source[self.position] == '<':
                self.next = Token('LESS_THAN',None)
                self.position += 1
            elif self.source[self.position] == '>':
                self.next = Token('GREATER_THAN',None)
                self.position += 1
            elif self.source[self.position:self.position + 2] == '&&':
                self.next = Token('LOGICAL_AND', None)
                self.position += 2
            elif self.source[self.position:self.position + 3] == 'and':
                self.next = Token('LOGICAL_AND', None)
                self.position += 3
            elif self.source[self.position:self.position + 2] == '||':
                self.next = Token('LOGICAL_OR', None)
                self.position += 2
            elif self.source[self.position:self.position + 1] == '!':
                self.next = Token('LOGICAL_NOT', None)
                self.position += 1
            elif self.source[self.position:self.position + 4] == 'pari':
                self.next = Token('EQUALS', None)
                self.position += 4
            elif self.source[self.position] == '=':
                self.next = Token('ASSIGN',None)
                self.position += 1
            elif self.source[self.position] == ';':
                self.next = Token('SEMICOLON',None)
                self.position += 1
            elif self.source[self.position]== '.':
                self.next = Token('DOT', None)
                self.position += 1
            elif self.source[self.position] == ',':
                self.next = Token('COMMA', None)
                self.position += 1
            elif isdigit(self.source[self.position]):
                self.next = Token('INT',int(self.source[self.position]))
                initial_pos = self.position
                while self.position < len(self.source) and isdigit(self.source[self.position]):
                    self.position += 1
                    self.next = Token('INT',int(self.source[initial_pos : self.position]))
            elif self.source[self.position].isalpha():
                identifier = self.source[self.position]
                self.position += 1
                self.next = Token('IDENTIFIER', identifier)
                while self.position < len(self.source) and (self.source[self.position].isalnum() or self.source[self.position] == '_'):
                    identifier += self.source[self.position]
                    self.position += 1
                    if identifier == 'stampa':
                        self.next = Token('PRINTLN', None)
                        break
                    elif identifier == 'se':
                        self.next = Token('IF', None)
                        break
                    elif identifier == 'altro':
                        self.next = Token('ELSE', None)
                        break
                    elif identifier == 'per':
                        self.next = Token('FOR', None)
                        break
                    elif identifier == 'ingresso':
                        self.next = Token('SCANLN', None)
                        break
                    elif identifier == 'variabile':
                        self.next = Token('VAR', None)
                        break
                    elif identifier == 'intero':
                        self.next = Token('TYPE', 'int')
                        break
                    elif identifier == 'corda':
                        self.next = Token('TYPE', 'string')
                        break
                    elif identifier == 'bool':
                        self.next = Token('TYPE', 'bool')
                        break
                    elif identifier == 'return':
                        self.next = Token('RETURN', None)
                        break
                    elif identifier == 'funzione':
                        self.next = Token('FUNC', None)
                        break
                    else:
                        self.next = Token('IDENTIFIER', identifier)
                        if "intero" in identifier and identifier != "Print"  and identifier != "Printl" and identifier != "Println":
                            self.next = Token('IDENTIFIER', identifier.split("intero")[0])
                            self.position -= 6
                            break
                        elif "corda" in identifier:
                            self.next = Token('IDENTIFIER', identifier.split("corda")[0])
                            self.position -= 5
                            break
                        elif "bool" in identifier:
                            self.next = Token('IDENTIFIER', identifier.split("bool")[0])
                            self.position -= 4
                            break

            elif self.source[self.position] == '"':
                self.position += 1
                string = ''
                while self.position < len(self.source) and self.source[self.position] != '"':
                    string += self.source[self.position]
                    self.position += 1
                if self.position == len(self.source):
                    raise Exception("Expected closing quote")
                self.next = Token('STRING', string)
                self.position += 1
        else:  
            self.next = Token('EOF',None)
        # print(self.next.type)
        return self.next
        
class Parser:
    PrePro = None
    tokenizer = None

    @staticmethod
    def parse_factor(tokenizer, symbol_table):
        if tokenizer.next.type == 'INT':
            result = IntVal(tokenizer.next.value)
            tokenizer.select_next()
            return result
        elif tokenizer.next.type == 'IDENTIFIER':
            identifier = Identifier(tokenizer.next.value)
            tokenizer.select_next()
            if tokenizer.next.type == 'LPAREN':
                tokenizer.select_next()
                if tokenizer.next.type == 'RPAREN':
                    tokenizer.select_next()
                    return FuncCall([identifier])
                arg = Parser.parse_relational_expression(tokenizer, symbol_table)
                args = [arg]
                while tokenizer.next.type == 'COMMA':
                    tokenizer.select_next()
                    arg = Parser.parse_relational_expression(tokenizer, symbol_table)
                    args.append(arg)
                # tokenizer.select_next()
                if tokenizer.next.type == 'RPAREN':
                    tokenizer.select_next()
                    return FuncCall([identifier] + args)
                else:
                    raise Exception(f"Expected closing parenthesis, got {tokenizer.next.type}")
            return identifier
        
        elif tokenizer.next.type == 'LPAREN':
            tokenizer.select_next()
            result = Parser.parse_relational_expression(tokenizer, symbol_table)
            # tokenizer.select_next()
            if tokenizer.next.type == 'RPAREN':
                tokenizer.select_next()
                return result
            else:
                raise Exception(f"Expected closing parenthesis, got {tokenizer.next.type}")     
        elif tokenizer.next.type == 'PLUS':
            tokenizer.select_next()
            child = Parser.parse_factor(tokenizer, symbol_table)
            result = UnOp(Token('PLUS', None), child)
            return result
        elif tokenizer.next.type == 'MINUS':
            tokenizer.select_next()
            child = Parser.parse_factor(tokenizer, symbol_table)
            result = UnOp(Token('MINUS', None), child)
            return result
        elif tokenizer.next.type == 'LOGICAL_NOT':
            tokenizer.select_next()
            child = Parser.parse_factor(tokenizer, symbol_table)
            result = UnOp(Token('LOGICAL_NOT', None), child)
            return result
        elif tokenizer.next.type == 'SCANLN':
            tokenizer.select_next()
            if tokenizer.next.type == 'LPAREN':
                tokenizer.select_next()
                if tokenizer.next.type == 'RPAREN':
                    tokenizer.select_next()
                    return Scanln(None)
                else:
                    raise Exception(f"Expected closing parenthesis, got {tokenizer.next.type}")
            else:
                raise Exception(f"Expected opening parenthesis, got {tokenizer.next.type}")
        elif tokenizer.next.type == 'STRING':
            result = StringVal(tokenizer.next.value)
            tokenizer.select_next()
            return result
        else:
            raise Exception(f"Unexpected token 1 : {tokenizer.next.type}")
    # @staticmethod
    # def parse_assignment(tokenizer, symbol_table):
    #     if tokenizer.next.type == 'IDENTIFIER':
    #         identifier = tokenizer.next.value
    #         tokenizer.select_next()
    #         if tokenizer.next.type == 'ASSIGN':
    #             tokenizer.select_next()
    #             expression = Parser.parse_relational_expression(tokenizer, symbol_table)
    #             statement = Assignment(identifier, expression)
    #             symbols.append(identifier)
    #         else:
    #             raise Exception(f"Unexpected token: {tokenizer.next.type}")
    #     else:
    #         raise Exception(f"Unexpected token: {tokenizer.next.type}")
    #     return statement

    @staticmethod
    def parse_term(tokenizer, symbol_table):
        result = Parser.parse_factor(tokenizer , symbol_table)
        while tokenizer.next.type in ['MULT', 'DIV']:
            op = tokenizer.next
            tokenizer.select_next()
            right = Parser.parse_factor(tokenizer , symbol_table)
            result = BinOp(op, result, right)
        return result

    @staticmethod
    def parse_expression(tokenizer, symbol_table):
        result = Parser.parse_term(tokenizer, symbol_table)
        while tokenizer.next.type in ['PLUS', 'MINUS', 'DOT']:
            op = tokenizer.next
            tokenizer.select_next()
            right = Parser.parse_term(tokenizer, symbol_table)
            result = BinOp(op, result, right)
        return result
    @staticmethod
    def parse_statement(tokenizer, symbol_table, block=False, func_table=None):
        # if tokenizer.next.type == 'ASSIGN':
        #     tokenizer.select_next()
        #     expression = Parser.parse_relational_expression(tokenizer, symbol_table)
        #     statement = Assignment(tokenizer.next.value, expression)
        if tokenizer.next.type == 'IDENTIFIER':
            identifier = tokenizer.next.value
            results = [tokenizer.next]
            tokenizer.select_next()
            # if tokenizer.next.type == 'EQUALS':
            #     tokenizer.select_next()
            #     expression = Parser.parse_relational_expression(tokenizer, symbol_table)
            #     # statement = Assignment(identifier, expression)
            # if tokenizer.next.type == 'ASSIGN' and block and identifier not in symbols:
            #     raise Exception("Assignment not allowed in block")
            if tokenizer.next.type == 'ASSIGN':
                tokenizer.select_next()
                symbols.append(identifier)
                if tokenizer.next.type == 'SCANLN':
                    tokenizer.select_next()
                    statement = Scanln(identifier)
                    if tokenizer.next.type == 'LPAREN':
                        tokenizer.select_next()
                    if tokenizer.next.type == 'RPAREN':
                        tokenizer.select_next()
                else:
                    expression = Parser.parse_relational_expression(tokenizer, symbol_table)
                    statement = Assignment(identifier, expression)
                    symbols.append(identifier)
                    
            elif tokenizer.next.type == 'LPAREN':
                    tokenizer.select_next()
                    if tokenizer.next.type == 'RPAREN':
                        tokenizer.select_next()
                        return identifier
                    results.append(tokenizer.next)
                    _type = tokenizer.next.type
                    # results.append(tokenizer.next)
                    # results.append(tokenizer.next)
                    result = Parser.parse_relational_expression(tokenizer, symbol_table)

                    while tokenizer.next.type == 'COMMA':
                        # results = [result]
                        tokenizer.select_next()
                        _type = tokenizer.next.type
                        results.append(tokenizer.next)
                        result = Parser.parse_relational_expression(tokenizer, symbol_table)
                    # tokenizer.select_next()
                    if tokenizer.next.type == 'RPAREN':
                        tokenizer.select_next()
                        return FuncCall(results)
                    else:
                        raise Exception(f"Expected closing parenthesis, got {tokenizer.next.type}") 
            else:
                raise Exception(f"Unexpected token: {tokenizer.next.type}")
        elif tokenizer.next.type == 'IF':
            tokenizer.select_next()
            condition = Parser.parse_relational_expression(tokenizer, symbol_table)

            if tokenizer.next.type == 'LBRACE':
                block = Parser.parse_block(tokenizer, symbol_table)
            else:                raise Exception(f"Expected opening brace after IF condition, got {tokenizer.next.type}")
            else_block = None
            if tokenizer.next.type == 'ELSE':
                tokenizer.select_next()
                if tokenizer.next.type == 'LBRACE':
                    else_block = Parser.parse_block(tokenizer, symbol_table)
                else:
                    raise Exception(f"Expected opening brace after ELSE, got {tokenizer.next.type}")
            statement = If(condition, block, else_block)
        elif tokenizer.next.type == 'FOR':
            tokenizer.select_next()
            assignment = Parser.parse_statement(tokenizer, symbol_table, block=False)
            if tokenizer.next.type == 'SEMICOLON':
                tokenizer.select_next()  # Consume ';'
            else:
                raise Exception(f"Expected semicolon after initialization in FOR loop, got {tokenizer.next.type}")
            condition = Parser.parse_relational_expression(tokenizer, symbol_table)
            if tokenizer.next.type == 'SEMICOLON':
                tokenizer.select_next()  # Consume ';'
            else:
                raise Exception(f"Expected semicolon after condition in FOR loop, got {tokenizer.next.type}")
        
            increment = Parser.parse_statement(tokenizer, symbol_table, block=False)
            block = Parser.parse_block(tokenizer, symbol_table)
            statement = For(assignment, condition, increment, block)
        elif tokenizer.next.type == 'PRINTLN':
            tokenizer.select_next()
            expression = Parser.parse_relational_expression(tokenizer, symbol_table)
            statement = Println(expression)
        elif tokenizer.next.type == 'RETURN':
            tokenizer.select_next()
            expression = Parser.parse_relational_expression(tokenizer, symbol_table)
            statement = ReturnOP(expression)
        elif tokenizer.next.type == 'VAR':
            tokenizer.select_next()
            if tokenizer.next.type in reserved_tokens:
                raise Exception(f"reserved word {tokenizer.next.type } cannot be used as identifier")
            identifier = tokenizer.next.value
            tokenizer.select_next()
            if tokenizer.next.type == 'TYPE':
                _type = tokenizer.next.value
                tokenizer.select_next()
                statement = VarDec(identifier, _type)
                if tokenizer.next.type == 'ASSIGN':
                    tokenizer.select_next()
                    expression = Parser.parse_relational_expression(tokenizer, symbol_table)
                    assignment = Assignment(identifier, expression)
                    return Block([statement, assignment])
            else:
                raise Exception(f"Unexpected token: {tokenizer.next.type}")
        else:
            raise Exception(f"Unexpected token: {tokenizer.next.type}")
        return statement

    @staticmethod
    def parse_relational_expression(tokenizer, symbol_table):
        left = Parser.parse_expression(tokenizer, symbol_table)
        if tokenizer.next.type in ['LESS_THAN', 'GREATER_THAN', 'EQUALS', 'LOGICAL_AND', 'LOGICAL_OR', 'LOGICAL_NOT', 'DOT']:
            op = tokenizer.next
            tokenizer.select_next()
            right = Parser.parse_relational_expression(tokenizer, symbol_table)
            return BinOp(op, left, right)
        else:
            return left
        
    @staticmethod
    def parse_block(tokenizer, symbol_table, func_table=None):
        statements = []
        if tokenizer.next.type == 'LBRACE':
            tokenizer.select_next()
            while tokenizer.next.type != 'EOF' and tokenizer.next.type != 'RBRACE':
                statement = Parser.parse_statement(tokenizer, symbol_table,block=True, func_table=func_table)
                statements.append(statement)
            tokenizer.select_next()
            return Block(statements)
        else:
            while tokenizer.next.type != 'EOF':
                statement = Parser.parse_statement(tokenizer, symbol_table, block=False)
                if statement is not None:
                    statements.append(statement)
                # tokenizer.select_next()
            return Block(statements)
    @staticmethod
    def parse_program(tokenizer, symbol_table, func_table=None):
        functions = []
        while tokenizer.next.type != 'EOF':
            declaration = Parser.parse_declaration(tokenizer, symbol_table, func_table)
            functions.append(declaration)
        tokenizer.select_next()
        return functions

    @staticmethod
    def parse_declaration(tokenizer, symbol_table, func_table=None):
        if tokenizer.next.type == 'FUNC':
            tokenizer.select_next()
            if tokenizer.next.type == 'IDENTIFIER':
                identifiers = []
                name = Identifier(tokenizer.next.value)
                identifiers.append(name)
                symbols.append(name.value)
                tokenizer.select_next()
                if tokenizer.next.type == 'LPAREN':
                    tokenizer.select_next()
                    if tokenizer.next.type == 'IDENTIFIER':
                        value = tokenizer.next.value
                        tokenizer.select_next()
                        if tokenizer.next.type == 'TYPE':
                            _type = tokenizer.next.value
                            identifiers.append(Identifier(value, _type))
                            tokenizer.select_next()
                        else:
                            raise Exception(f"Expected type, got {tokenizer.next.type}")
                        while tokenizer.next.type == 'COMMA':
                            tokenizer.select_next()
                            if tokenizer.next.type == 'IDENTIFIER':
                                value = tokenizer.next.value
                                tokenizer.select_next()
                            else:
                                raise Exception(f"Expected identifier, got {tokenizer.next.type}")
                            if tokenizer.next.type == 'TYPE':
                                identifiers.append(Identifier(value, _type))
                                _type = tokenizer.next.value
                                tokenizer.select_next()
                            else:
                                raise Exception(f"Expected type, got {tokenizer.next.type}")
                    if tokenizer.next.type == 'RPAREN':
                        tokenizer.select_next()
                        _type = tokenizer.next.value
                        tokenizer.select_next()
                        block = Parser.parse_block(tokenizer, symbol_table, func_table)
                        return FuncDec(identifiers, block, _type)
                    else:
                        raise Exception(f"Expected closing parenthesis, got {tokenizer.next.type}")
                else:
                    raise Exception(f"Expected opening parenthesis, got {tokenizer.next.type}")
            else:
                raise Exception(f"Expected identifier, got {tokenizer.next.type}")
        else:
            raise Exception(f"Expected FUNC, got {tokenizer.next.type}")



    @staticmethod
    def run(code):
        code_without_comments = PreProcessor.filter(code)
        code_without_comments = PreProcessor.remove_spaces(code_without_comments)
        tokenizer = Tokenizer(code_without_comments)
        tokenizer.select_next()
        symbol_table = SymbolTable()
        func_table = FuncTable()
        ast_root = Parser.parse_program(tokenizer, symbol_table, func_table)
        tokenizer.select_next()
        if tokenizer.next.type != 'EOF':
            raise Exception("Unexpected token")
        ast_root.append(FuncCall([Identifier('main')]))
        # print("AST:")
        # print(ast_root)
        # print("Evaluation:")
        for function in ast_root:
            function.Evaluate(func_table, symbol_table)
            
if __name__ == "__main__":
    filename = sys.argv[1]
    # filename = 'teste1.go'
    with open(filename, 'r') as file:
        code = file.read()
    Parser.run(code)