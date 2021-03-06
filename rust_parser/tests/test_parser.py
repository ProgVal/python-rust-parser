# Copyright (C) 2020 Valentin Lorentz
#
# This file is part of python-rust-parser.
#
# python-rust-parser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python-rust-parser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with python-rust-parser.  If not, see <https://www.gnu.org/licenses/>.

from ..gll import builtin_rules


def test_parse_addition(parser, ast):
    assert parser.parse("1 + 2", start_rule_name="ExprMain") == ast.Expr(
        attrs=[],
        kind=ast.ExprKind.Binary(
            left=ast.Expr(
                attrs=[],
                kind=ast.ExprKind.Literal(inner=builtin_rules.LITERAL(literal="1")),
            ),
            op=ast.BinaryOp.ADD,
            right=ast.Expr(
                attrs=[],
                kind=ast.ExprKind.Literal(inner=builtin_rules.LITERAL(literal="2")),
            ),
        ),
    )


def test_parse_const_declaration(parser, ast):
    assert parser.parse(
        'const foo: bar = "baz";', start_rule_name="ModuleMain"
    ) == ast.ModuleContents(
        attrs=[],
        items=[
            ast.Item(
                attrs=[],
                vis=None,
                kind=ast.ItemKind.Const(
                    name=builtin_rules.IDENT(ident="foo"),
                    ty=ast.Type.Path_(
                        inner=ast.QPath.Unqualified(
                            inner=ast.Path(
                                global_=False,
                                path=[
                                    ast.RelativePathInner(
                                        inner=ast.PathSegment(
                                            ident=builtin_rules.IDENT(ident="bar"),
                                            field_1=None,
                                        )
                                    )
                                ],
                            )
                        )
                    ),
                    value=ast.Expr(
                        attrs=[],
                        kind=ast.ExprKind.Literal(
                            inner=builtin_rules.LITERAL(literal='"baz"')
                        ),
                    ),
                ),
            )
        ],
    )


def test_parse_fn_declaration(parser, ast):
    def expected_ast(extra_stmts, ret_ty):
        return [
            ast.Item(
                attrs=[],
                vis=None,
                kind=ast.ItemKind.Fn(
                    header=ast.FnHeader(
                        constness=False, unsafety=False, asyncness=False, abi=None
                    ),
                    decl=ast.FnDecl(
                        name=builtin_rules.IDENT(ident="foo"),
                        generics=None,
                        args=None,
                        ret_ty=ret_ty,
                        where_clause=None,
                    ),
                    body=ast.Block(
                        attrs=[],
                        stmts=[
                            ast.Stmt.Expr_(
                                inner=ast.Expr(
                                    attrs=[],
                                    kind=ast.ExprKind.Literal(
                                        inner=builtin_rules.LITERAL(literal="42")
                                    ),
                                )
                            ),
                            *extra_stmts,
                        ],
                    ),
                ),
            )
        ]

    assert parser.parse(
        "fn foo() { 42 }", start_rule_name="ModuleMain"
    ) == ast.ModuleContents(attrs=[], items=expected_ast(extra_stmts=[], ret_ty=None))

    assert parser.parse(
        "fn foo() -> u64 { 42 }", start_rule_name="ModuleMain"
    ) == ast.ModuleContents(
        attrs=[],
        items=expected_ast(
            extra_stmts=[],
            ret_ty=ast.Type.Path_(
                inner=ast.QPath.Unqualified(
                    inner=ast.Path(
                        global_=False,
                        path=[
                            ast.RelativePathInner(
                                inner=ast.PathSegment(
                                    ident=builtin_rules.IDENT(ident="u64"), field_1=None
                                )
                            )
                        ],
                    )
                )
            ),
        ),
    )

    assert parser.parse(
        "fn foo() { 42; }", start_rule_name="ModuleMain"
    ) == ast.ModuleContents(
        attrs=[], items=expected_ast(extra_stmts=[ast.Stmt.Semi()], ret_ty=None)
    )


def test_parse_struct(parser, ast):
    expected_ast = ast.ModuleContents(
        attrs=[],
        items=[
            ast.Item(
                attrs=[],
                vis=None,
                kind=ast.ItemKind.Struct(
                    name=builtin_rules.IDENT(ident="Foo"),
                    generics=None,
                    body=ast.StructBody.Record(
                        where_clause=None,
                        fields=[
                            ast.RecordField(
                                attrs=[],
                                vis=None,
                                name=builtin_rules.IDENT(ident="bar"),
                                ty=ast.Type.Path_(
                                    inner=ast.QPath.Unqualified(
                                        inner=ast.Path(
                                            global_=False,
                                            path=[
                                                ast.RelativePathInner(
                                                    inner=ast.PathSegment(
                                                        ident=builtin_rules.IDENT(
                                                            ident="Baz"
                                                        ),
                                                        field_1=None,
                                                    )
                                                )
                                            ],
                                        )
                                    )
                                ),
                            )
                        ],
                    ),
                ),
            )
        ],
    )

    assert parser.parse(
        "struct Foo { bar: Baz }", start_rule_name="ModuleMain"
    ) == expected_ast
    assert parser.parse(
        "struct Foo { bar: Baz, }", start_rule_name="ModuleMain"
    ) == expected_ast
