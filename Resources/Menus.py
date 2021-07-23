import discord
from discord.ext import menus


""" Class | Menu List Selector

This class allows the creation of menus with given options that are used to select items from the list.
"""
class MenuListSelector(menus.MenuPages):
    def __init__(self, ctx, source, handler, **kwargs):
        super().__init__(source, **kwargs)
        self.ctx = ctx
        self.handler = handler

        self.emojis = [
            "\N{DIGIT ONE}\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
            "\N{DIGIT TWO}\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
            "\N{DIGIT THREE}\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
            "\N{DIGIT FOUR}\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
            "\N{DIGIT FIVE}\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
            "\N{DIGIT SIX}\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
            "\N{DIGIT SEVEN}\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
            "\N{DIGIT EIGHT}\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}"
        ]

        self.custom_buttons = [menus.Button(e, self.handle_selection, position = menus.Position(i), skip_if=getattr(self, f"_skip_item_{i+1}")) for i, e in enumerate(self.emojis)]
        for button in self.custom_buttons:
            self.add_button(button)

    async def handle_selection(self, payload):
        try:
            await self.ctx.message.delete()
        except:
            pass
        self.stop()
        selection = self.emojis.index(payload.emoji.name)
        selection = (self.current_page * self._source.per_page) + selection
        if self._source.rr:
            await self.handler(self.ctx, selection, payload, self._source.rr[3])
        elif self._source.roles:
            await self.handler(self.ctx, self._source.roles[selection])
        else:
            await self.handler(self.ctx, selection, payload)

    async def show_page(self, page_number):
        page = await self._source.get_page(page_number)
        old_page = await self._source.get_page(self.current_page)
        self.current_page = page_number
        kwargs = await self._get_kwargs_from_page(page)
        await self.message.edit(**kwargs)

        if not type(page) == list:
            page = [page]
        if not type(old_page) == list:
            old_page = [old_page]

        if len(page) > len(old_page):
            for i, button in enumerate(self.custom_buttons):
                if i+1 > len(old_page) and i+1 <= len(page):
                    await self.add_button(button, react = True)
        elif len(page) < len(old_page):
            for i, button in enumerate(self.custom_buttons):
                if i+1 > len(page):
                    await self.remove_button(button, react = True)

    def get_page(self, page_number):
        if self._source.per_page == 1:
            return self._source.entries[page_number]
        else:
            base = page_number * self._source.per_page
            return self._source.entries[base:base + self._source.per_page]

    def _skip_pagination(self):
        max_pages = self._source.get_max_pages()
        if max_pages is None:
            return True
        return max_pages <= 1

    def _skip_double_triangle_buttons(self):
        max_pages = self._source.get_max_pages()
        if max_pages is None:
            return True
        return max_pages <= 2

    def _skip_page_item(self, item):
        page = self.get_page(self.current_page)

        if type(page) == list:
            return item > len(page)
        else:
            return item > 1

    def _skip_item_1(self):
        return self._skip_page_item(1)
    def _skip_item_2(self):
        return self._skip_page_item(2)
    def _skip_item_3(self):
        return self._skip_page_item(3)
    def _skip_item_4(self):
        return self._skip_page_item(4)
    def _skip_item_5(self):
        return self._skip_page_item(5)
    def _skip_item_6(self):
        return self._skip_page_item(6)
    def _skip_item_7(self):
        return self._skip_page_item(7)
    def _skip_item_8(self):
        return self._skip_page_item(8)

    @menus.button('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\ufe0f', position=menus.First(0), skip_if=_skip_double_triangle_buttons)
    async def go_to_first_page(self, payload):
        await self.show_page(0)

    @menus.button('\N{BLACK LEFT-POINTING TRIANGLE}\ufe0f', position=menus.First(1), skip_if=_skip_pagination)
    async def go_to_previous_page(self, payload):
        await self.show_checked_page(self.current_page - 1)


    @menus.button('\N{BLACK RIGHT-POINTING TRIANGLE}\ufe0f', position=menus.First(2), skip_if=_skip_pagination)
    async def go_to_next_page(self, payload):
        await self.show_checked_page(self.current_page + 1)

    @menus.button('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\ufe0f', position=menus.First(3), skip_if=_skip_double_triangle_buttons)
    async def go_to_last_page(self, payload):
        await self.show_page(self._source.get_max_pages() - 1)

    @menus.button('\N{BLACK SQUARE FOR STOP}\ufe0f', position=menus.First(4))
    async def stop_pages(self, payload):
        try:
            await self.ctx.message.delete()
        except:
            pass
        self.stop()


""" Class | Menu List

A class dedicated to being able to show a paginated list of items, which can be selected via reaction.
"""
class MenuListSource(menus.ListPageSource):
    def __init__(self, embed_util, title = None, desc = None, entries = [], rr = None, per_page = 8, selector = False, roles = None):
        self.title = title
        self.desc = desc
        self.embed_util = embed_util
        self.selector = selector
        self.rr = rr
        self.roles = roles

        self.emojis = [
            "\N{DIGIT ONE}\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
            "\N{DIGIT TWO}\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
            "\N{DIGIT THREE}\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
            "\N{DIGIT FOUR}\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
            "\N{DIGIT FIVE}\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
            "\N{DIGIT SIX}\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
            "\N{DIGIT SEVEN}\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
            "\N{DIGIT EIGHT}\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}"
        ]

        if per_page > 8:
            per_page = 8

        num = 0
        for i, entry in enumerate(entries):
            entries[i] = {
                "index": num,
                "content": entry
            }

            num += 1
            if num >= per_page:
                num = 0

        super().__init__(entries, per_page = per_page)


    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page

        if not type(entries) == list:
            entries = [entries]

        items = []
        for i, entry in enumerate(entries, start=offset):
            items.append(f"{self.emojis[entry['index']]} {entry['content']}")

        fields = []
        if self.rr:
            fields.append({"name": "Title", "value": self.rr[0]['title']})
            fields.append({"name": "Description", "value": self.rr[0]['description']})
            fields.append({"name": "Channel", "value": self.rr[2].mention})
            fields.append({"name": "Roles", "value": "\n".join(f"{r['emoji']} - {r['role']}" for r in self.rr[1])})

        embed = self.embed_util.get_embed(
            title = self.title,
            desc = self.desc + "\n\n" + "\n".join(items),
            fields = fields
        )
        if self.get_max_pages() > 1:
            embed.title = embed.title + f" | [{menu.current_page + 1}/{self.get_max_pages()}]"

        return embed

    def is_paginating(self):
        if self.selector:
            return True
        else:
            return len(self.entries) > self.per_page


""" Class | School Menu Select

This class hosts the menu to manage what category of school gets picked, by the letter it is registered under.
"""
class SchoolMenuSelect(menus.MenuPages):
    def __init__(self, ctx, source, handler, **kwargs):
        super().__init__(source, **kwargs)
        self.ctx = ctx
        self.handler = handler

        self.custom_buttons = [{"button": menus.Button(e['emoji'], self.handle_selection, position = menus.Position(i), skip_if=getattr(self, f"_skip_item_{e['letter']}")), "emoji": e['emoji'], "letter": e['letter']} for i, e in enumerate(self._source.entries)]
        for button in self.custom_buttons:
            self.add_button(button['button'])

    async def handle_selection(self, payload):
        try:
            await self.ctx.message.delete()
        except:
            pass
        self.stop()
        selection = self.custom_buttons[[e['emoji'] for e in self.custom_buttons].index(payload.emoji.name)]['letter']
        await self.handler(self.ctx, selection)

    def get_page(self, page_number):
        if self._source.per_page == 1:
            return self._source.entries[page_number]
        else:
            base = page_number * self._source.per_page
            return self._source.entries[base:base + self._source.per_page]

    def _skip_pagination(self):
        max_pages = self._source.get_max_pages()
        if max_pages is None:
            return True
        return max_pages <= 1

    def _skip_double_triangle_buttons(self):
        max_pages = self._source.get_max_pages()
        if max_pages is None:
            return True
        return max_pages <= 2

    def _skip_page_item(self, item):
        for i, e in enumerate(self._source.entries):
            if e['letter'] == item:
                return False

        return True

    def _skip_item_A(self):
        return self._skip_page_item('A')
    def _skip_item_B(self):
        return self._skip_page_item('B')
    def _skip_item_C(self):
        return self._skip_page_item('C')
    def _skip_item_D(self):
        return self._skip_page_item('D')
    def _skip_item_E(self):
        return self._skip_page_item('E')
    def _skip_item_F(self):
        return self._skip_page_item('F')
    def _skip_item_G(self):
        return self._skip_page_item('G')
    def _skip_item_H(self):
        return self._skip_page_item('H')
    def _skip_item_I(self):
        return self._skip_page_item('I')
    def _skip_item_J(self):
        return self._skip_page_item('J')
    def _skip_item_K(self):
        return self._skip_page_item('K')
    def _skip_item_L(self):
        return self._skip_page_item('L')
    def _skip_item_M(self):
        return self._skip_page_item('M')
    def _skip_item_N(self):
        return self._skip_page_item('N')
    def _skip_item_O(self):
        return self._skip_page_item('O')
    def _skip_item_P(self):
        return self._skip_page_item('P')
    def _skip_item_Q(self):
        return self._skip_page_item('Q')
    def _skip_item_R(self):
        return self._skip_page_item('R')
    def _skip_item_S(self):
        return self._skip_page_item('S')
    def _skip_item_T(self):
        return self._skip_page_item('T')
    def _skip_item_U(self):
        return self._skip_page_item('U')
    def _skip_item_V(self):
        return self._skip_page_item('V')
    def _skip_item_W(self):
        return self._skip_page_item('W')
    def _skip_item_X(self):
        return self._skip_page_item('X')
    def _skip_item_Y(self):
        return self._skip_page_item('Y')
    def _skip_item_Z(self):
        return self._skip_page_item('Z')

    @menus.button('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\ufe0f', position=menus.First(0), skip_if=_skip_double_triangle_buttons)
    async def go_to_first_page(self, payload):
        await self.show_page(0)

    @menus.button('\N{BLACK LEFT-POINTING TRIANGLE}\ufe0f', position=menus.First(1), skip_if=_skip_pagination)
    async def go_to_previous_page(self, payload):
        await self.show_checked_page(self.current_page - 1)


    @menus.button('\N{BLACK RIGHT-POINTING TRIANGLE}\ufe0f', position=menus.First(2), skip_if=_skip_pagination)
    async def go_to_next_page(self, payload):
        await self.show_checked_page(self.current_page + 1)

    @menus.button('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\ufe0f', position=menus.First(3), skip_if=_skip_double_triangle_buttons)
    async def go_to_last_page(self, payload):
        await self.show_page(self._source.get_max_pages() - 1)

    @menus.button('\N{BLACK SQUARE FOR STOP}\ufe0f', position=menus.First(4))
    async def stop_pages(self, payload):
        try:
            await self.ctx.message.delete()
        except:
            pass
        self.stop()


""" Class | School Menu List

The class dedicated to managing the paginated list of schools registered in the system.
"""
class SchoolMenuList(menus.ListPageSource):
    def __init__(self, embed_util, title = None, desc = None, entries = []):
        self.embed_util = embed_util
        self.title = title
        self.desc = desc
        self.entries = entries
        self.per_page = 2

        super().__init__(self.entries, per_page = self.per_page)

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page

        if not type(entries) == list:
            entries = [entries]

        fields = []
        for i, entry in enumerate(entries, start=offset):
            fields.append({"name": entry['emoji'], "value": "\n".join(r.mention for r in entry['roles']), "inline": False})

        embed = self.embed_util.get_embed(
            title = self.title,
            desc = self.desc,
            fields = fields
        )
        if self.get_max_pages() > 1:
            embed.title = embed.title + f" [{menu.current_page + 1}/{self.get_max_pages()}]"

        return embed

    def is_paginating(self):
        return True
