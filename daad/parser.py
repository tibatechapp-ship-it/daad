"""Recursive-descent parser for Daad (Arabic Python)."""
from __future__ import annotations

from . import ast_nodes as ast
from .lexer import Token, TokenType


class ParseError(Exception):
    def __init__(self, msg: str, line: int = 0, col: int = 0) -> None:
        loc = f" (السطر {line}، العمود {col})" if line else ""
        super().__init__(f"{msg}{loc}")
        self.line = line
        self.col = col


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    # ── Token helpers ────────────────────────────────────────
    def peek(self, offset: int = 0) -> Token:
        p = self.pos + offset
        return self.tokens[-1] if p >= len(self.tokens) else self.tokens[p]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        if tok.type != TokenType.EOF:
            self.pos += 1
        return tok

    def at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def expect(self, ttype: TokenType, value: str | None = None) -> Token:
        tok = self.peek()
        if tok.type != ttype:
            raise ParseError(f"توقعت {ttype.name}، وجدت {tok.value!r}", tok.line, tok.col)
        if value is not None and tok.value != value:
            raise ParseError(f"توقعت {value!r}، وجدت {tok.value!r}", tok.line, tok.col)
        return self.advance()

    def expect_keyword(self, mapped: str) -> Token:
        tok = self.peek()
        if tok.type != TokenType.KEYWORD or tok.mapped != mapped:
            raise ParseError(f"توقعت كلمة '{mapped}'، وجدت {tok.value!r}", tok.line, tok.col)
        return self.advance()

    def match_keyword(self, mapped: str) -> bool:
        tok = self.peek()
        return tok.type == TokenType.KEYWORD and tok.mapped == mapped

    def match_op(self, value: str) -> bool:
        tok = self.peek()
        return tok.type == TokenType.OP and tok.value == value

    def skip_newlines(self) -> None:
        while self.peek().type == TokenType.NEWLINE:
            self.advance()

    def expect_newline(self) -> None:
        tok = self.peek()
        if tok.type == TokenType.EOF:
            return
        if tok.type != TokenType.NEWLINE:
            raise ParseError(f"توقعت نهاية سطر، وجدت {tok.value!r}", tok.line, tok.col)
        self.advance()

    def indent(self) -> int:
        """Column of the current (non-newline) token."""
        return self.peek().col

    # ── Module ───────────────────────────────────────────────
    def parse(self) -> ast.Module:
        stmts: list[ast.Statement] = []
        while not self.at_end():
            if self.peek().type == TokenType.NEWLINE:
                self.advance()
                continue
            stmts.append(self.parse_statement())
        return ast.Module(stmts)

    # ── Statement dispatch ───────────────────────────────────
    def parse_statement(self) -> ast.Statement:
        tok = self.peek()
        if tok.type == TokenType.KEYWORD:
            m = tok.mapped
            if m == "def":      return self.parse_function_def()
            if m == "class":    return self.parse_class_def()
            if m == "if":       return self.parse_if(self.indent())
            if m == "for":      return self.parse_for()
            if m == "while":    return self.parse_while()
            if m == "return":   return self.parse_return()
            if m == "import":   return self.parse_import()
            if m == "from":     return self.parse_import_from()
            if m == "pass":
                self.advance(); self.expect_newline(); return ast.Pass()
            if m == "break":
                self.advance(); self.expect_newline(); return ast.Break()
            if m == "continue":
                self.advance(); self.expect_newline(); return ast.Continue()
        return self.parse_expr_or_assign()

    # ── Statements ───────────────────────────────────────────
    def parse_function_def(self) -> ast.FunctionDef:
        kw = self.advance()
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.OP, "(")
        params: list[str] = []
        if not self.match_op(")"):
            while True:
                params.append(self.expect(TokenType.IDENT).value)
                if self.match_op(","):
                    self.advance(); continue
                break
        self.expect(TokenType.OP, ")")
        self.expect(TokenType.OP, ":")
        body = self.parse_block(kw.col)
        return ast.FunctionDef(name, params, body)

    def parse_class_def(self) -> ast.ClassDef:
        kw = self.advance()
        name = self.expect(TokenType.IDENT).value
        bases: list[str] = []
        if self.match_op("("):
            self.advance()
            if not self.match_op(")"):
                while True:
                    bases.append(self.expect(TokenType.IDENT).value)
                    if self.match_op(","):
                        self.advance(); continue
                    break
            self.expect(TokenType.OP, ")")
        self.expect(TokenType.OP, ":")
        body = self.parse_block(kw.col)
        return ast.ClassDef(name, bases, body)

    def parse_if(self, parent_indent: int) -> ast.If:
        self.expect_keyword("if")
        test = self.parse_expression()
        self.expect(TokenType.OP, ":")
        body = self.parse_block(parent_indent)
        orelse = self._parse_else_chain(parent_indent)
        return ast.If(test, body, orelse)

    def _parse_else_chain(self, parent_indent: int) -> list[ast.Statement]:
        self.skip_newlines()
        if self.at_end() or self.indent() != parent_indent:
            return []
        tok = self.peek()
        if tok.type == TokenType.KEYWORD and tok.mapped == "elif":
            self.advance()
            test = self.parse_expression()
            self.expect(TokenType.OP, ":")
            body = self.parse_block(parent_indent)
            nested_orelse = self._parse_else_chain(parent_indent)
            return [ast.If(test, body, nested_orelse)]
        if tok.type == TokenType.KEYWORD and tok.mapped == "else":
            self.advance()
            self.expect(TokenType.OP, ":")
            return self.parse_block(parent_indent)
        return []

    def parse_for(self) -> ast.For:
        kw = self.advance()
        target = self.expect(TokenType.IDENT).value
        self.expect_keyword("in")
        iter_expr = self.parse_expression()
        self.expect(TokenType.OP, ":")
        body = self.parse_block(kw.col)
        return ast.For(target, iter_expr, body)

    def parse_while(self) -> ast.While:
        kw = self.advance()
        test = self.parse_expression()
        self.expect(TokenType.OP, ":")
        body = self.parse_block(kw.col)
        return ast.While(test, body)

    def parse_return(self) -> ast.Return:
        self.advance()
        if self.peek().type in (TokenType.NEWLINE, TokenType.EOF):
            self.expect_newline()
            return ast.Return(None)
        value = self.parse_expression()
        self.expect_newline()
        return ast.Return(value)

    def parse_import(self) -> ast.Import:
        self.advance()
        module = self.expect(TokenType.IDENT).value
        alias = None
        if self.match_keyword("as"):
            self.advance()
            alias = self.expect(TokenType.IDENT).value
        self.expect_newline()
        return ast.Import(module, alias)

    def parse_import_from(self) -> ast.ImportFrom:
        self.advance()
        module = self.expect(TokenType.IDENT).value
        self.expect_keyword("import")
        names: list[str] = []
        while True:
            names.append(self.expect(TokenType.IDENT).value)
            if self.match_op(","):
                self.advance(); continue
            break
        self.expect_newline()
        return ast.ImportFrom(module, names)

    def parse_expr_or_assign(self) -> ast.Statement:
        expr = self.parse_expression()
        tok = self.peek()
        if tok.type == TokenType.OP and tok.value in ("=", "+=", "-=", "*=", "/="):
            target = self._assign_target(expr, tok)
            self.advance()
            value = self.parse_expression()
            self.expect_newline()
            if tok.value == "=":
                return ast.Assign(target, value)
            return ast.AugAssign(target, tok.value[0], value)

        self.expect_newline()
        return ast.ExprStmt(expr)

    def _assign_target(self, expr: ast.Expression, tok: Token) -> ast.Expression:
        """الأهداف الصالحة: اسم، فهرس x[i]، أو خاصية obj.attr."""
        if isinstance(expr, (ast.Name, ast.Subscript, ast.Attribute)):
            return expr
        raise ParseError("هدف إسناد غير صالح", tok.line, tok.col)

    def parse_block(self, parent_indent: int) -> list[ast.Statement]:
        self.skip_newlines()
        if self.at_end():
            raise ParseError("توقعت كتلة، وجدت نهاية الملف")
        block_indent = self.indent()
        if block_indent <= parent_indent:
            tok = self.peek()
            raise ParseError(
                f"توقعت كتلة بادئة أعمق من {parent_indent}، وجدت {block_indent}",
                tok.line, tok.col,
            )
        stmts: list[ast.Statement] = []
        while not self.at_end():
            if self.peek().type == TokenType.NEWLINE:
                self.advance(); continue
            cur_indent = self.indent()
            if cur_indent < block_indent:
                break
            if cur_indent > block_indent:
                tok = self.peek()
                raise ParseError(
                    f"محاذاة غير متسقة: توقعت {block_indent}، وجدت {cur_indent}",
                    tok.line, tok.col,
                )
            stmts.append(self.parse_statement())
        if not stmts:
            raise ParseError("كتلة فارغة (أضف pass)")
        return stmts

    # ── Expressions (precedence climbing) ────────────────────
    def parse_expression(self) -> ast.Expression:
        return self.parse_or()

    def parse_or(self) -> ast.Expression:
        left = self.parse_and()
        while self.match_keyword("or"):
            self.advance()
            left = ast.BinOp(left, "or", self.parse_and())
        return left

    def parse_and(self) -> ast.Expression:
        left = self.parse_not()
        while self.match_keyword("and"):
            self.advance()
            left = ast.BinOp(left, "and", self.parse_not())
        return left

    def parse_not(self) -> ast.Expression:
        if self.match_keyword("not"):
            self.advance()
            return ast.UnaryOp("not", self.parse_not())
        return self.parse_comparison()

    def parse_comparison(self) -> ast.Expression:
        left = self.parse_additive()
        while True:
            tok = self.peek()
            if tok.type == TokenType.OP and tok.value in ("==", "!=", "<", ">", "<=", ">="):
                self.advance()
                left = ast.BinOp(left, tok.value, self.parse_additive())
            elif tok.type == TokenType.KEYWORD and tok.mapped in ("is", "in"):
                self.advance()
                left = ast.BinOp(left, tok.mapped, self.parse_additive())
            else:
                break
        return left

    def parse_additive(self) -> ast.Expression:
        left = self.parse_multiplicative()
        while True:
            tok = self.peek()
            if tok.type == TokenType.OP and tok.value in ("+", "-"):
                self.advance()
                left = ast.BinOp(left, tok.value, self.parse_multiplicative())
            else:
                break
        return left

    def parse_multiplicative(self) -> ast.Expression:
        left = self.parse_unary()
        while True:
            tok = self.peek()
            if tok.type == TokenType.OP and tok.value in ("*", "/", "//", "%"):
                self.advance()
                left = ast.BinOp(left, tok.value, self.parse_unary())
            else:
                break
        return left

    def parse_unary(self) -> ast.Expression:
        tok = self.peek()
        if tok.type == TokenType.OP and tok.value in ("-", "+", "~"):
            self.advance()
            return ast.UnaryOp(tok.value, self.parse_unary())
        return self.parse_power()

    def parse_power(self) -> ast.Expression:
        base = self.parse_postfix()
        if self.match_op("**"):
            self.advance()
            return ast.BinOp(base, "**", self.parse_unary())
        return base

    def parse_postfix(self) -> ast.Expression:
        expr = self.parse_primary()
        while True:
            if self.match_op("("):
                self.advance()
                args: list[ast.Expression] = []
                if not self.match_op(")"):
                    while True:
                        args.append(self.parse_expression())
                        if self.match_op(","):
                            self.advance(); continue
                        break
                self.expect(TokenType.OP, ")")
                expr = ast.Call(expr, args)
            elif self.match_op("."):
                self.advance()
                attr = self.expect(TokenType.IDENT).value
                expr = ast.Attribute(expr, attr)
            elif self.match_op("["):
                self.advance()
                idx = self.parse_expression()
                self.expect(TokenType.OP, "]")
                expr = ast.Subscript(expr, idx)
            else:
                break
        return expr

    def parse_primary(self) -> ast.Expression:
        tok = self.peek()

        if tok.type == TokenType.NUMBER:
            self.advance()
            return ast.Number(tok.value)

        if tok.type == TokenType.STRING:
            self.advance()
            return ast.Str(tok.value)

        if tok.type == TokenType.FSTRING:
            self.advance()
            return ast.FString(tok.value)

        if tok.type == TokenType.KEYWORD:
            if tok.mapped == "True":
                self.advance(); return ast.Bool(True)
            if tok.mapped == "False":
                self.advance(); return ast.Bool(False)
            if tok.mapped == "None":
                self.advance(); return ast.NoneLit()

        if tok.type == TokenType.IDENT:
            self.advance()
            return ast.Name(tok.value)

        if tok.type == TokenType.OP:
            if tok.value == "(":
                self.advance()
                if self.match_op(")"):
                    self.advance(); return ast.TupleLit([])
                first = self.parse_expression()
                if self.match_op(","):
                    elems = [first]
                    while self.match_op(","):
                        self.advance()
                        if self.match_op(")"):
                            break
                        elems.append(self.parse_expression())
                    self.expect(TokenType.OP, ")")
                    return ast.TupleLit(elems)
                self.expect(TokenType.OP, ")")
                return first
            if tok.value == "[":
                self.advance()
                elems: list[ast.Expression] = []
                if not self.match_op("]"):
                    while True:
                        elems.append(self.parse_expression())
                        if self.match_op(","):
                            self.advance()
                            if self.match_op("]"):
                                break
                            continue
                        break
                self.expect(TokenType.OP, "]")
                return ast.ListLit(elems)
            if tok.value == "{":
                self.advance()
                keys: list[ast.Expression] = []
                vals: list[ast.Expression] = []
                if not self.match_op("}"):
                    while True:
                        keys.append(self.parse_expression())
                        self.expect(TokenType.OP, ":")
                        vals.append(self.parse_expression())
                        if self.match_op(","):
                            self.advance()
                            if self.match_op("}"):
                                break
                            continue
                        break
                self.expect(TokenType.OP, "}")
                return ast.DictLit(keys, vals)

        raise ParseError(f"تعبير غير متوقع: {tok.value!r}", tok.line, tok.col)


def parse(tokens: list[Token]) -> ast.Module:
    return Parser(tokens).parse()
