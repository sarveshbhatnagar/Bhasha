from strings_with_arrows import *
import string

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

class Error:
    """
    Parent Error class, takes in pos_start, pos_end, error_name and details of the error.
    contains method as_string , which returns error.
    """
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = "{}: {}\n".format(self.error_name,self.details)
        result += "File {}, line {}".format(self.pos_start.fn,self.pos_start.ln + 1)
        result += "\n\n" + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

class IllegalCharError(Error):
    """
    Used when illegal character is encountered, sends in error name to class error as Illegal Character.
    """
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

class ExpectedCharError(Error):
    """
    Used when there is a missing character, sends in error name to class error as Expected Character.
    """
    def __init__(self, pos_start,pos_end, details):
        super().__init__(pos_start,pos_end,'Expected Character', details)

class InvalidSyntaxError(Error):
    """
    Used when Invalid Syntax is encountered, sends in error name to class error as Invalid Syntax.
    """
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

class RTError(Error):
    """
    Used when Runtime error is encountered, sends in error name to class error as Runtime Error.
    """
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'Runtime Error', details)
        self.context = context

    def as_string(self):
        result  = self.generate_traceback()
        result += "{}:{}".format(self.error_name,self.details)
        result += "\n\n" + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        ctx =  self.context

        while ctx:
            result = "File {}, line {}, in {}\n".format(pos.fn,str(pos.ln + 1), ctx.display_name) + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent
        return 'Traceback (most recent call last): \n' + result

### POSITION

class Position:
    """
    Class for keeping track of position.
    Methods :
    1. advance: updates current index pointer, if line ends, updates line number.
    2. copy: returns a copy of its own POSITION object.
    """
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

### TOKENS

TT_IDENTIFIER   = 'IDENTIFIER'
TT_EQ           = 'EQ'
TT_KEYWORD      = 'KEYWORD'
TT_INT		    = 'INT'
TT_POW          = 'POW'
TT_FLOAT        = 'FLOAT'
TT_PLUS         = 'PLUS'
TT_MINUS        = 'MINUS'
TT_MUL          = 'MUL'
TT_DIV          = 'DIV'
TT_LPAREN       = 'LPAREN'
TT_RPAREN       = 'RPAREN'
TT_COMMA        = 'COMMA'
TT_ARROW        = 'ARROW'
TT_EE           = 'EE'
TT_NE           = 'NE'
TT_LT           = 'LT'
TT_GT           = 'GT'
TT_LTE          = 'LTE'
TT_GTE          = 'GTE'
TT_EOF		    = 'EOF'

KEYWORDS = [
    'DABBA',
    'AUR', #AND
    'YATOH', #OR
    'ULTA', #NOT
    'AGAR', #if
    'TOH', #then
    'NAHITOH', #ELIF
    'MAGAR', #else
    'YEH', #FOR
    'ISTAK', #TO
    'KADAM', #STEP
    'JABTAK' #WHILE
    'FUN' #function decl.
]

class Token: #used to create a token, value pair. storing position start and position end of the token.
    """
    A token class has token type, token value, start position of the token and end position of the token.

    functions:
    matches(type,value): checks if the token object which is calling the matches function have the same value and type as the parameters passed.

    """
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end.copy()

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    def __repr__(self):
        if self.value:
            return "{}:{}".format(self.type,self.value)
        return "{}".format(self.type)


#List of Special Handling functions in Lexer :
# make_number() : used for handling numbers, creating the integer or floating point as per the number encountered. Also used for verifying that the number is not invalid  : e.g. 21a12


class Lexer:
    """
    class for aiding in lexical analysis. used for generation of token list.

    Methods defined:
    1. advance: move ahead. character by character.
    2. make_tokens: generates list of tokens
    3. make number: special handling function for make_tokens to make number.
    4. make_identifier: special handling function for identifier and KEYWORDS.
    5. make_not_equals: special handling function for '!='.
    6. make_equals: special handling function for '==' or '='.
    7. make_less_than: special handling function for '<' or '<='.
    8. make_greater_than: special handling function for '>' or '>='.

    """
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1,0,-1,fn,text) #look at it.
        self.current_char = None
        self.advance()

    def advance(self):
        """
        advance : moves ahead character by character.
        """
        self.pos.advance(self.current_char)# doubt.
        if self.pos.idx < len(self.text):
            self.current_char = self.text[self.pos.idx]
        else:
            self.current_char = None #at eof, current char = None.

    def make_tokens(self):
        """
        make_tokens : generates a list of tokens. Used for token handling.
        """
        tokens= []

        while self.current_char != None: #continue till current character is not none.
            if self.current_char in ' \t': #skip if space or tabs
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number()) #special handling for numbers.
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier()) #special handling for letters.
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, pos_start= self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(self.make_minus_or_arrow())
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, pos_start= self.pos))
                self.advance()
            elif self.current_char == '^':
                tokens.append(Token(TT_POW, pos_start= self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, pos_start= self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start= self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start= self.pos))
                self.advance()
            elif self.current_char == '!':
                tok, error = self.make_not_equals() #special handling function for NE.
                if error:
                    return [], error
                tokens.append(tok)
            elif self.current_char == '=':
                tokens.append(self.make_equals()) #special handling function for TT_EQ or TT_EE
            elif self.current_char == '<':
                tokens.append(self.make_less_than()) #special handling for less than or less than equals
            elif self.current_char == '>':
                tokens.append(self.make_greater_than()) # special handling for greater than or greater than equals.
            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start,self.pos,"'" + char + "'")

        tokens.append(Token(TT_EOF,pos_start=self.pos))
        return tokens, None

    def make_number(self): #special handling function for number
        """
        special handling function when token number is encountered.
        """
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    print("Error : Extra Dot Count \n")
                    break
                dot_count += 1
            num_str += self.current_char
            self.advance()


        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos) #returns integer if dot count == 0
        else:
            return Token(TT_FLOAT, float(num_str),pos_start,self.pos) # returns float otherwise.

    def make_identifier(self):
        """
        gets an identifier, checks if the identifier found is a KEYWORD or IDENTIFIER, returns the token accordingly.
        """
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
            id_str += self.current_char
            self.advance()

        tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
        return Token(tok_type, id_str, pos_start, self.pos)

    def make_minus_or_arrow(self):
        """
        Returns TT_MINUS if '-' and TT_ARROW if '->'
        """
        tok_type = TT_MINUS
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '>':
            self.advance()
            tok_type = TT_ARROW

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_not_equals(self):
        """
        if next character is "=" then returns a token of type TT_NE, otherwise returns an ExpectedCharError.
        """
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(TT_NE, pos_start = pos_start, pos_end= self.pos), None

        self.advance()
        return None, ExpectedCharError(pos_start, self.pos, " '=' after '!'")

    def make_equals(self):
        """
        Make equals checks if next token is '=', if it is then it returns TT_EE, else it returns TT_EQ.
        """
        tok_type = TT_EQ
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == '=':
            self.advance()
            tok_type = TT_EE

        return Token(tok_type, pos_start = pos_start, pos_end = self.pos)

    def make_less_than(self):
        """
        Make equals checks if next token is '=', if it is then it returns TT_LTE, else it returns TT_LT.
        """
        tok_type = TT_LT
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == '=':
            self.advance()
            tok_type = TT_LTE

        return Token(tok_type, pos_start = pos_start, pos_end = self.pos)

    def make_greater_than(self):
        """
        Make equals checks if next token is '=', if it is then it returns TT_GTE, else it returns TT_GT.
        """
        tok_type = TT_GT
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == '=':
            self.advance()
            tok_type = TT_GTE

        return Token(tok_type, pos_start = pos_start, pos_end = self.pos)





class NumberNode:
    """
    Used for holding number token, its start position and end position.

    """

    def __init__(self, tok):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return "{}".format(self.tok)

class VarAccessNode:
    """
    Used for holding variable name, start position and end position.
    """
    def __init__(self,var_name_tok):
        self.var_name_tok = var_name_tok

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

class VarAssignNode:
    """
    Used for holding variable name and variable value... also its start position and end position.
    """
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

class BinOpNode:
    """ Initializes left node, operator token and right node... also holds position start as start of left node and
        position end as end of right node.
    """
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return "({},{},{})".format(self.left_node,self.op_tok,self.right_node)

class UnaryOpNode():
    """Initializes operator token with the operator, also initializes the node. Pos start is start of optok, pos end is end of the node."""

    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end #check otherwise.

    def __repr__(self):
        return "({},{})".format(self.op_tok,self.node)


class IfNode:
    """
    Holds cases list and else case.
    """

    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case

        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[len(self.cases) - 1][0]).pos_end

class ForNode:
    """
    holds variable name, start val node, end val node, step, and body_node.
    """

    def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node):
        self.var_name_tok = var_name_tok
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.body_node.pos_end

class WhileNode:
    """
    Holds condition and body.
    """

    def __init__(self, condition_node, body_node):
        self.condition_node = condition_node
        self.body_node = body_node

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end

class FuncDefNode:
    """
    Holds function name, arguments and function body.
    """
    def __init__(self, var_name_tok, arg_name_toks, body_node):
        self.var_name_tok = var_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node

        #If fun name defined, args defined, or none defined.
        if self.var_name_tok:
            self.pos_start = self.var_name_tok.pos_start
        elif len(self.arg_name_toks) > 0:
            self.pos_start = self.arg_name_toks[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start

        self.pos_end = self.body_node.pos_end

class CallNode:
    """Needs understanding."""

    def __init__(self, node_to_call, arg_nodes):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

        self.pos_start = self.node_to_call.pos_start

        if len(self.arg_nodes) > 0:
            self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
        else:
            self.pos_end = self.node_to_call.pos_end





### Need to understand Parse Result.
class ParseResult:#check what it does...
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0

    def register_advancement(self):
        self.advance_count += 1

    def register(self, res):
        self.advance_count += res.advance_count
        if res.error:
            self.error = res.error
        return res.node

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.advance_count == 0:
            self.error = error
        return self


class Parser:
    """
    Methods :
    1. advance : Increments tok_idx, checks if not out of bounds, updates current token.
    2. parse : used to get the parse result based on the grammar defined in grammar.txt.
    3. bin_op : (func() (args func())*) | (func() (args funcb())*)
    4. power
    5. atom
    6. term
    7. expr
    8. factor
    9. arith_expr
    10. comp_expr
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        """
        returns next token as current token.
        """
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        """
        special handling function : calls expr.
        """
        res = self.expr()
        if not res.error and self.current_tok.type != TT_EOF: #check what it does. why not res.error???? for that check expr().
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end,"Expected the defined operators."))
        return res

    def if_expr(self):
        """
        AGAR - EXPR - TOH - EXPR
        (NAHITOH - EXPR - TOH - EXPR)* #wrapped in while.
        MAGAR - EXPR

        """
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(TT_KEYWORD, 'AGAR'):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end,"Expected AGAR"))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(TT_KEYWORD,'TOH'):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected TOH"))

        res.register_advancement()
        self.advance()

        expr = res.register(self.expr())
        if res.error:
            return res
        cases.append((condition, expr))

        while self.current_tok.matches(TT_KEYWORD, "NAHITOH"):
            res.register_advancement()
            self.advance()

            condition = res.register(self.expr())
            if res.error:
                return res

            if not self.current_tok.matches(TT_KEYWORD, "TOH"):
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected TOH"))

            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            cases.append((condition, expr))

        if self.current_tok.matches(TT_KEYWORD,'MAGAR'):
            res.register_advancement()
            self.advance()

            else_case = res.register(self.expr())
            if res.error:
                return res

        return res.success(IfNode(cases, else_case))

    def for_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'YEH'):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end,"Expected YEH"))

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected Identifier"))

        var_name = self.current_tok
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_EQ:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected '='"))

        res.register_advancement()
        self.advance()

        start_value = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(TT_KEYWORD,'ISTAK'):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected ISTAK"))

        res.register_advancement()
        self.advance()

        end_value = res.register(self.expr())

        if res.error:
            return res

        if self.current_tok.matches(TT_KEYWORD,'KADAM'):
            res.register_advancement()
            self.advance()

            step_value = res.register(self.expr())
            if res.error:
                return res
        else:
            step_value = None

        if not self.current_tok.matches(TT_KEYWORD, 'TOH'):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected 'TOH'"))

        res.register_advancement()
        self.advance()

        body = res.register(self.expr())
        if res.error:
            return res

        return res.success(ForNode(var_name, start_value, end_value, step_value, body))


    def while_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'JABTAK'):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected JABTAK"))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())

        if res.error:
            return res

        if not self.current_tok.matches(TT_KEYWORD, 'TOH'):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected TOH"))

        res.register_advancement()
        self.advance()

        body = res.register(self.expr())
        if res.error:
            return res

        return res.success(WhileNode(condition, body))

    def func_def(self):
        """
        special handling function for function defination.
        KEYWORD:        FUN IDENTIFIER?
        				LPAREN (IDENTIFIER (COMMA IDENTIFIER)*)? RPAREN
        				ARROW expr
        """

        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD,'FUN'):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end,"Expected FUN"))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_IDENTIFIER:
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected ("))

        else:
            #No function name defined
            var_name_tok = None
            if self.current_tok.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected ("))

        res.register_advancement()
        self.advance()
        arg_name_toks = []

        if self.current_tok.type == TT_IDENTIFIER:
            arg_name_toks.append(self.current_tok)
            res.register_advancement()
            self.advance()

            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()

                if self.current_tok.type != TT_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected IDENTIFIER"))

                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()

            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected , or )"))

        else:
            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected )"))

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_ARROW:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected ->"))

        res.register_advancement()
        self.advance()
        node_to_return = res.register(self.expr())
        if res.error:
            return res

        return res.success(FuncDefNode(var_name_tok, arg_name_toks, node_to_return))





    def atom(self):
        """
        atom : INT|FLOAT
             : LPAREN expr RPAREN
             : if_expr
             : for_expr
             : while_expr
             : func_def
        """
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))
        elif tok.type in TT_IDENTIFIER:
            #whenever comes accross this identifier, VarAccessNode will be returned.
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))
        elif tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: #what does it do???
                return res
            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,"Expected ')'"))
        elif tok.matches(TT_KEYWORD, 'AGAR'):
            #IF statement handling.
            if_expr = res.register(self.if_expr())
            if res.error: return res
            return res.success(if_expr)

        elif tok.matches(TT_KEYWORD, 'YEH'):
            #IF statement handling.
            for_expr = res.register(self.for_expr())
            if res.error: return res
            return res.success(for_expr)

        elif tok.matches(TT_KEYWORD, 'JABTAK'):
            #IF statement handling.
            while_expr = res.register(self.while_expr())
            if res.error: return res
            return res.success(while_expr)

        elif tok.matches(TT_KEYWORD, 'FUN'):
            func_def = res.register(self.func_def())
            if res.error:
                return res
            return res.success(func_def)

        return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end,"Expected int, float, identifier, '+', '-', '(', "))

    def power(self):
        """
        power : atom (pow factor)*
        """
        return self.bin_op(self.call, (TT_POW, ), self.factor)

    def call(self):
        """
        why was call function defined???
        call	: atom (LPAREN  (expr (COMMA expr)*)? RPAREN)?
        """
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error:
            return res

        if self.current_tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            arg_nodes = []

            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')', 'DABBA', 'AGAR', 'YEH', 'JABTAK', 'FUN', int, float, identifier, '+', '-', '(' or 'ULTA'"))

                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()

                    arg_nodes.append(res.register(self.expr()))
                    if res.error:
                        return res

                if self.current_tok.type != TT_RPAREN:
                    return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected , or )"))

                res.register_advancement()
                self.advance()
            return res.success(CallNode(atom,arg_nodes))
        return res.success(atom)

    def factor(self):
        """
        factor  : (PLUS|MINUS) factor
                : POW
        """
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok,factor))

        return self.power()



        return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, "Expected int, float,identifier, '+', '-', or '('"))

    def term(self):
        """
        term    : factor ((MUL|DIV) factor)*
        """
        return self.bin_op(self.factor,(TT_MUL,TT_DIV))

    def arith_expr(self):
        """
        arith-expr		: term ((PLUS|MINUS) term)*
        """
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def comp_expr(self):
        """
        comp-expr		: ULTA comp-expr
        				: arith-expr ((EE|LT|GT|LTE|GTE) arith-expr)*

        """
        res = ParseResult()

        if self.current_tok.matches(TT_KEYWORD,"ULTA"):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error:
                return res
            return res.success(UnaryOpNode(op_tok, node))
        node = res.register(self.bin_op(self.arith_expr, (TT_EE,TT_NE,TT_LT,TT_GT,TT_LTE,TT_GTE)))

        if res.error:
            return res.failure(InvalidSyntaxError(
                tok.pos_start, tok.pos_end, "Expected int, float, identifier, '+', '-', '(', or ULTA"
            ))

        return res.success(node)




    def expr(self):
        """
        expr    : KEYWORD:DABBA IDENTIFIER EQ expr
                : comp_expr ((AUR|YATOH) comp_expr)*
        """
        res = ParseResult()
        if self.current_tok.matches(TT_KEYWORD,'DABBA'):
            res.register_advancement()
            self.advance()
            if self.current_tok.type != TT_IDENTIFIER:
                #error, There should have been an identifier here.
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end,'Expected Identifier'))
            var_name = self.current_tok
            res.register_advancement()
            self.advance()
            if self.current_tok.type != TT_EQ:
                #error expected equals token.
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,'Expected ='))

            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            else:
                #passing variable name and value of the evaluated expr.
                return res.success(VarAssignNode(var_name, expr))

        node = res.register(self.bin_op(self.comp_expr, ((TT_KEYWORD , "AUR"), (TT_KEYWORD , "YATOH"))))

        if res.error:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected int, float,DABBA, identifier, '+', '-', or '(' or ULTA"))
        return res.success(node)

    def bin_op(self,func_a,ops,func_b=None):#generalised function for term and expr.
        """
        bin_op    : func (args func)*
        bin_op    : func (args funcb)*
        """
        if func_b == None:
            func_b = func_a

        res = ParseResult()
        left = res.register(func_a())
        if res.error:
            return res

        while self.current_tok.type in ops or (self.current_tok.type,self.current_tok.value) in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)
        return res.success(left)


class RTResult:
    """Its kind of an unwrap function... dont know yet."""

    def __init__(self):
        self.value = None
        self.error = None

    def register(self, res):#what does register do???
        if res.error:
            self.error = res.error
        return res.value

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self

class Value:
    def __init__(self):
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def added_to(self,other):
        return None, self.illegal_operation(other)

    def subbed_by(self,other):
        return None, self.illegal_operation(other)

    def multed_by(self,other):
        return None, self.illegal_operation(other)

    def dived_by(self,other):
        return None, self.illegal_operation(other)

    def powed_by(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_eq(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_ne(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lte(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gte(self, other):
        return None, self.illegal_operation(other)

    def anded_by(self, other):
        return None, self.illegal_operation(other)

    def ored_by(self, other):
        return None, self.illegal_operation(other)

    def notted(self):
        return None, self.illegal_operation(other)

    def execute(self,args):
        return RTResult().failure(self.illegal_operation())

    def copy(self):
        raise Exception('No copy method defined')

    def is_true(self):
        return False

    def illegal_operation(self,other=None):
        if not other:
            other = self
        return RTError(self.pos_start, other.pos_end, "Illegal operation",self.context)




class Number(Value):
    """
    Methods defined:
    1. set_pos : params - start, end. Used to set position start and end
    2. set_context : params - context. Used to set context
    3. added_to : params - Number object. Used to add number to self.
    4. subbed_by : params - Number object. Used to subtract number from self.
    5. multed_by : params - Number object. Used to multiply number with self.
    6. dived_by : params - Number object. Used to divide number from self (self/number).
    7. powed_by
    8. get_comparison_eq
    9. get_comparison_ne
    10. get_comparison_lt
    11. get_comparison_gt
    12. get_comparison_lte
    13. get_comparison_gte
    14. anded_by
    15. notted
    16. ored_by
    17. copy

    """

    def __init__(self, arg):
        super().__init__()
        self.value = arg


    def added_to(self,other):
        """
        returns Number object, which is addition performed with self and the passed number object.
        """
        if isinstance(other,Number):#checks if the class Number and other are same.
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def subbed_by(self,other):
        """
        returns Number object, which is subtraction performed with self and the passed number object.
        """
        if isinstance(other,Number):#checks if the class Number and other are same.
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self,other):
        """
        returns Number object, which is multiplication performed with self and the passed number object.
        """
        if isinstance(other,Number):#checks if the class Number and other are same.
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def dived_by(self,other):
        """
        returns Number object, which is division performed with self and the passed number object.
        also checks if the other number passed is 0 or not... (division by zero error)
        """
        if isinstance(other,Number):#checks if the class Number and other are same.
            if other.value == 0:
                return None, RTError(other.pos_start,other.pos_end,"Division by zero",self.context)

            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def powed_by(self, other):
        """
        returns self.value ** other.value

        """
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_ne(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def anded_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def ored_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def notted(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start,self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value != 0



    def __repr__(self):
        return str(self.value)

class Function(Value):
    """
    Needs documentation.

    """

    def __init__(self, name, body_node, arg_names):
        super.__init__()
        self.name = name or "<anonymous>"
        self.body_node = body_node
        self.arg_names = arg_names

    def execute(self, args):
        res = RTResult()
        interpreter = Interpreter()
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)

        if len(args) > len(self.arg_names):
            return res.failure(RTError(self.pos_end, "{} too few args passed into '{}'".format(len(self.arg_names) - len(args), self.name), self.context))

        for i in range(len(args)):
            arg_name = self.arg_names[i]
            arg_value = args[i]
            arg_value.set_context(new_context)
            new_context.symbol_table.set(arg_name, arg_value)

        value = res.register(interpreter.visit(self.body_node, new_context))
        if res.error:
            return res

        return res.success(value)

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return "<function {}>".format(self.name)





class Context:
    """A class for keeping track of context. takes in display_name, parent context, parent_entry_pos."""

    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None


class SymbolTable:
    """
    Symbol table class is used to keep track of variables as of now.
    Functions defined:
    get(name) : returns value.
    set(name, value) : adds a name value pair to symbols List
    remove(name) : removes a variable from the symbols list
    """

    def __init__(self):
        self.symbols = {}
        self.parent = None

    def get(self, name):
        value = self.symbols.get(name, None)
        #gets the value if defined else returns none (above statememnt)
        # if none, then check in parent table, if current table is global table then there is no parent table,
        # so we also need to check if parent table is defined or not.
        if value == None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self,name):
        del self.symbols[name]


class Interpreter:
    """
    Methods defined:
    1. visit(node, context) : caller function, calls method according to the node type. if no matching method is called, calls no_visit_method by default.
    2. no_visit_method(node, context) : Raises exception. no visit_... method defined.
    3. visit_NumberNode(node,context) : Returns RTResult object, with number value in it.
    4. visit_BinOpNode(node,context) : Performs binary operation and then returns the RTResult object.
    5. visit_UnaryOpNode(node,context) : Performs unary operation and then returns the RTResult object.
    6. visit_VarAccessNode
    7. visit_VarAssignNode
    8. visit_IfNode(node, context)

    Individual function documentation remaining.
    """

    def visit(self, node, context):
        method_name = "visit_{}".format(type(node).__name__)
        method = getattr(self,method_name, self.no_visit_method)
        return method(node,context)

    def no_visit_method(self,node,context):
        raise Exception("No visit_{} method defined".format(type(node).__name__))

    # TYPE OF NODE.

    def visit_NumberNode(self, node, context):
        return RTResult().success(
            Number(node.tok.value).set_context(context).set_pos(node.pos_start,node.pos_end)
        )

    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(RTError(node.pos_start,node.pos_end,"'{}' is not defined".format(var_name)), context)

        value = value.copy().set_pos(node.pos_start, node.pos_end)
        return res.success(value)

    def visit_VarAssignNode(self,node,context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))

        if res.error:
            return res
        context.symbol_table.set(var_name,value)
        return res.success(value)


    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error:
            return res
        right = res.register(self.visit(node.right_node,context))
        if res.error:
            return res
        if node.op_tok.type == TT_PLUS:
            result , error = left.added_to(right)
        elif node.op_tok.type == TT_MINUS:
            result , error = left.subbed_by(right)
        elif node.op_tok.type == TT_MUL:
            result , error = left.multed_by(right)
        elif node.op_tok.type == TT_DIV:
            result , error = left.dived_by(right)
        elif node.op_tok.type == TT_POW:
            result , error = left.powed_by(right)
        elif node.op_tok.type == TT_EE:
            result, error = left.get_comparison_eq(right)
        elif node.op_tok.type == TT_NE:
            result, error = left.get_comparison_ne(right)
        elif node.op_tok.type == TT_LT:
            result, error = left.get_comparison_lt(right)
        elif node.op_tok.type == TT_GT:
            result, error = left.get_comparison_gt(right)
        elif node.op_tok.type == TT_LTE:
            result, error = left.get_comparison_lte(right)
        elif node.op_tok.type == TT_GTE:
            result, error = left.get_comparison_gte(right)
        elif node.op_tok.matches(TT_KEYWORD, 'AUR'):
            result, error = left.anded_by(right)
        elif node.op_tok.matches(TT_KEYWORD, 'YATOH'):
            result, error = left.ored_by(right)

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node,context))
        if res.error:
            return res
        error = None

        if node.op_tok.type == TT_MINUS:
            number, error = number.multed_by(Number(-1))
        elif node.op_tok.matches(TT_KEYWORD, 'ULTA'):
            number, error = number.notted()

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_IfNode(self, node, context):
        res = RTResult()

        for condition, expr in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.error:
                return res
            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.error:
                    return res
                return res.success(expr_value)

        if node.else_case:
            else_value = res.register(self.visit(node.else_case, context))
            if res.error:
                return res
            return res.success(else_value)

        return res.success(None)


    def visit_ForNode(self, node, context):
        res = RTResult()

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.error:
            return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.error:
            return res

        if node.step_value_node:
            step_value = res.register(self.visit(node.end_value_node,context))
            if res.error:
                return res
        else:
            step_value = Number(1)

        i = start_value.value

        if step_value.value >= 0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda: i > end_value.value

        while condition():
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            i+= step_value.value

            res.register(self.visit(node.body_node, context))
            if res.error:
                return res

        return res.success(None)

    def visit_WhileNode(self, node, context):
        res = RTResult()

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.error:
                return res

            if not condition.is_true():
                break

            res.register(self.visit(node.body_node, context))
            if res.error:
                return res
        return res.success(None)

        def visit_FuncDefNode(self, node, context):
            """
            Needs documentation.
            """

            res = RTResult()

            func_name = node.var_name_tok.value if node.var_name_tok else None
            body_node = node.body_node
            arg_names = [arg_name.value for arg_name in node.arg_name_toks]
            func_value = Function(func_name, body_node, arg_names).set_context(context).set_pos(node.pos_start, node.pos_end)

            if node.var_name_tok:
                context.symbol_table.set(func_name, func_value)

            return res.success(func_value)

        def visit_CallNode(self, node, context):
            """
            Needs documentation.
            """
            res = RTResult()
            args = []

            value_to_call = res.register(self.visit(node.node_to_call, context))
            if res.error:
                return res

            value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

            for arg_node in node.arg_nodes:
                args.append(res.register(self.visit(arg_node,context)))
                if res.error:
                    return res

            return_value = res.register(value_to_call.execute(args))
            if res.error:
                return res
            return res.success(return_value)


global_symbol_table = SymbolTable()
global_symbol_table.set("null",Number(0))
global_symbol_table.set("FALSE", Number(0))
global_symbol_table.set("TRUE", NUMBER(1))

def run(fn, text):
    lexer = Lexer(fn, text)
    tokens , error = lexer.make_tokens()
    if error:
        return None, error

    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, ast.error

    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)
    return result.value, result.error
