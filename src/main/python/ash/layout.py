from prompt_toolkit.layout.containers import HSplit, VSplit, Window, ScrollOffsets, FloatContainer
from prompt_toolkit.layout.processors import HighlightSelectionProcessor
from prompt_toolkit.layout.controls import FillControl, TokenListControl
from prompt_toolkit.layout.margins import Margin, ScrollbarMargin
from prompt_toolkit.layout.dimension import LayoutDimension
from prompt_toolkit.layout.toolbars import TokenListToolbar
from prompt_toolkit.layout.lexers import PygmentsLexer
from prompt_toolkit.layout.screen import Char
from prompt_toolkit.document import Document
from pygments.token import Token

from .layout_bottombar import bottombar
from .layout_completer import completion_bar
from .lexer import EC2Lexer
from .table_control import TableControl

VERTICAL_LINE = '\u2501'
HORIZONTAL_LINE = '\u2503'

class SimpleMargin(Margin):
    def __init__(self, width): self.width = width
    def get_width(self, cli, get_ui_content): return self.width
    def create_margin(self, cli, window_render_info, width, height): return []

class ResourceWindow:
    def __init__(self, ash_cli):
        self.ash_cli = ash_cli

    def titles(self, _):
        T = Token.Resouce
        return [
            (T.Border, HORIZONTAL_LINE),
            (T.Title, " {:25} ".format("ID")),
            (T.Border, HORIZONTAL_LINE),
            (T.Title, " {:50} ".format("Name")),
            (T.Border, HORIZONTAL_LINE),
            (T.Title, " {:15} ".format("Type")),
            (T.Border, HORIZONTAL_LINE),
            (T.Title, " {:15} ".format("Private IP")),
            (T.Border, HORIZONTAL_LINE),
            (T.Title, " {:15} ".format("State")),
        ]

    def _format_inv_item(self, item):
        name = (item.name[:50] + '..') if len(item.name) > 50 else item.name
        return "{5} {0:<25} {5} {1:<50} {5} {2:<15} {5} {3:<15} {5} {4:<15}".format(
            item.instance_id,
            name,
            item.instance_type,
            item.private_ip_address,
            item.state['Name'],
            HORIZONTAL_LINE
        )

    def refresh_resource_buffer(self, completion_text=None):
        return None
        if completion_text:
            inv = self.ash_cli.inventory.find_completions(completion_text)
        else:
            inv = self.ash_cli.inventory.local_inv


        self.ash_cli.cli.buffers["RESOURCES_BUFFER"].document = Document(
            text="\n".join([self._format_inv_item(i) for i in inv]),
            cursor_position=0
        )

    def get_layout(self):
        return FloatContainer(
            HSplit([
                # Title
                TokenListToolbar(get_tokens=lambda cli: [(Token.Toolbar.Status.Title, 'ash')],
                                 align_center=True,
                                 default_char=Char(' ', Token.Toolbar.Status)),


                Window(height=LayoutDimension.exact(1),
                       content=FillControl(VERTICAL_LINE, token=Token.Resouce.Border)
                ),

                # resources area
                Window(
                    cursorline=True,
                    always_hide_cursor=True,
                    cursorline_token=Token.CursorColumn,
                    get_vertical_scroll=lambda x: 0,
                    scroll_offsets=ScrollOffsets(top=2, bottom=2),
                    left_margins=[ScrollbarMargin(display_arrows=True), SimpleMargin(2)],
                    content=TableControl(
                        get_table_titles=lambda cli: [
                            (Token.Resouce.Title, "title1"),
                            (Token.Resouce.Title, "title2"),
                            (Token.Resouce.Title, "title3")
                            ],
                        get_table_tokens=lambda cli: [
                            [
                                (Token.Resouce.Running, "test_r"),
                                (Token.Resouce.Stam, "stam"),
                                (Token.Resouce.Border, "border")
                            ],
                            [
                                (Token.Resouce.Running, "test_r2"),
                                (Token.Resouce.Stam, "stam2"),
                                (Token.Resouce.Border, "border2")
                            ],
                            [
                                (Token.Resouce.Running, "test_r3"),
                                (Token.Resouce.Stam, "stam3"),
                                (Token.Resouce.Border, "border3")
                            ]
                        ],
                        default_char=Char(token=Token.Resouce),
                        has_focus=True
                    )
                ),
                VSplit([
                    bottombar(self.ash_cli.inventory)
                ])
            ]),
            [
                completion_bar()
            ])
