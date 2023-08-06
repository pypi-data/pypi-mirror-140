"""
Module containing grid definition and every addition needed for it.
"""

from __future__ import annotations
from typing import Union, List, Tuple

import pygame

from pyggui.gui.item import StaticItem


class Cell(StaticItem):
    """
    Class for representing a single rectangle in the grid that is placed in the i, j position and has i-th rows height,
    j-th columns height. Items can be added to it, aligned and padded.
    """
    def __init__(
        self,
        grid: Grid,
        position_in_grid: Tuple,
        position: List[int] = [0, 0],
        size: Tuple[int, int] = (1, 1),
    ):
        """
        Args:
            position (List[int] = [0, 0]): Position to place item on screen (or on page).
            size (Tuple[int, int] = (1, 1)): Size of item.
            visible (bool): If item is currently visible.
            selected (bool): If item is currently selected.
        """
        super().__init__(position, size, False, False)
        self.grid = grid
        self.position_in_grid = position_in_grid

        # Possible alignments
        self.alignments = {
            "left": self._left,
            "right": self._right,
            "top": self._top,
            "bottom": self._bottom,
            "centre": self._centre,
            None: self._centre
        }
        # Possible paddings
        self._padding = {
            "top": 0,
            "bottom": 0,
            "left": 0,
            "right": 0
        }

    @property
    def padding(self):
        return self._padding

    @padding.setter
    def padding(self, padding):
        # TODO: Padding for whole cell, also to add is alignment for whole cell
        pass

    def _left(self, item: any) -> None:
        """
        Method aligns item to the left side of cell.
        """
        item.position = (self.position[0], item.position[1])

    def _right(self, item: any) -> None:
        """
        Method aligns item to the right side of cell.
        """
        # Set right cell border to match item right side
        diff = (self.width - item.width) if self.width > item.width else 0
        # Set new x position
        item.position = (self.position[0] + diff, item.position[1])

    def _top(self, item: any) -> None:
        """
        Method aligns item to the top side of cell.
        """
        # Set top borders to match
        item.position = (item.position[0], self.position[1])

    def _bottom(self, item: any) -> None:
        """
        Method aligns item to the bottom side of cell.
        """
        # Set bottom cell border to match item bottom
        diff = (self.height - item.height) if self.height > item.height else 0
        item.position = (item.position[0], self.position[1] + diff)

    def _centre(self, item: any) -> None:
        """
        Method aligns item so its centre matches the cells centre.
        """
        # Item centre is at cell centre
        centered_x = self.position[0] + ((self.width - item.width) // 2)
        centered_y = self.position[1] + ((self.height - item.height) // 2)
        item.position = (centered_x, centered_y)

    def __pad(self, item: any, padding: str, value: int) -> None:
        """
        Method adds padding to item based on cell position and size.

        Args:
            item (any): Item to pad.
            padding (str): Padding type (top, bottom, left, right).
            value (int): Number of px to pad.
        """
        # TODO: Make padding not move items if there is already enough space
        if padding in self.padding.keys():
            if padding == "top":
                item.y += value
            elif padding == "bottom":
                item.y -= value
            elif padding == "left":
                item.x += value
            elif padding == "right":
                item.x -= value

    def add_item(self, item: any, align: str = None, padding: str = None) -> None:
        """
        Method adds item to cell, aligns and pads it base on passed values.

        Args:
            item (any): Item to add.
            align (str): String defining alignment type. Multiple alignments are separated by a space character.
                Example: alignment = "centre top"  # Centre should always be first.
            padding (str): String defining padding of item. Multiple alignments are separated by a comma. Value is
                passed next to the alignment position as an integer value.
                Example: padding = "top 5, left 3"  # 5px from top 3px from bottom
        """
        self.items.append(item)  # Add item to item list
        self.alignments["centre"](item)  # Align item into centre initially so it moves it into cell
        # Handle alignment
        if align:
            for align in align.split(" "):  #
                if align in self.alignments:
                    self.alignments[align](item)  # Align item in set way
        else:
            self.alignments[align](item)  # Default alignment for None is centre
        # Handle padding
        if padding:
            for pad in padding.split(","):  # Go over each padding
                _pad = pad.strip()  # Remove whitespace around
                _pad = _pad.split(" ")
                print(_pad, pad)
                key, value = _pad[0], int(_pad[1])  # Todo add exception handling
                self.__pad(item, padding=key, value=value)

    def update(self):
        for item in self.items:
            item.update()

    def draw(self, visible: bool = False):
        if visible:  # Only draw if grid is visible
            pygame.draw.rect(
                self.display,
                color=(0, 0, 0),
                rect=self.rect,
                width=0  # Fill this one
            )
            pygame.draw.rect(
                self.display,
                color=(255, 255, 255),
                rect=self.rect,
                width=2
            )
        for item in self.items:
            item.draw()


class Row:
    """
    Single row in Grid, is only used for grabbing items using indexing with []. Row contains cells that are in that
    row in the grid.
    """
    def __init__(self, grid: Grid, data: List = None):
        self.grid = grid

        if data:
            self._list = list(data)
        else:
            self._list = list()

    def __len__(self):
        """ List length """
        return len(self._list)

    def __getitem__(self, i):
        """ Get a list item """
        return self._list[i]

    def __delitem__(self, i):
        """ Delete an item """
        del self._list[i]

    def __setitem__(self, i, val):
        """ Set item """
        # optional: self._acl_check(val)
        self._list[i] = val

    def __repr__(self):
        return "<{0} {1}>".format(self.__class__.__name__, self._list)

    def __str__(self):
        return str(self._list)

    def insert(self, i, val):
        """ Insert value at index """
        # optional: self._acl_check(val)
        self._list.insert(i, val)

    def append(self, val):
        """ Append value at end of list """
        self.insert(len(self._list), val)


def make_grid_line(line: List[Union[float, int]], total_size: int, number_of_items: int) -> List[int]:
    """ Used internally by Grid for constructing cell sizes for each column, row.
    Function creates a list representing sizes of cells (in px) in that line (either row or column).
    Line can be passed as a list of decimals (representing percentage of total size) or integers (representing sizes).
    Line can also include less elements than there are rows/columns, elements then get added/removed accordingly.

    Args:
        line (List[Union[float, int]]): List of either integers or floats representing different size format (px or %).
        total_size (int): Total size (height of all rows or width of all columns), can be either 1 (if %) or an integer
            representing size in px.
        number_of_items (int): Expected number of items in line.
    """
    # Check number of elements matches, add/remove otherwise
    element_number_difference = number_of_items - len(line)
    if element_number_difference < 0:  # If more were passed, remove last items
        line = self.number_of_rows[:abs(element_number_difference)]
    elif element_number_difference > 0:  # If less were passed, add number of items (equal part)
        if isinstance(line[0], float):  # If float, parts added must be equal to 1/total_num_parts
            one_part = 1 / number_of_items
        else:  # Else add equal parts of total_size
            one_part = int(total_size / number_of_items)
        line += [one_part for _ in range(element_number_difference)]
    # Create list
    if isinstance(line[0], float):  # If decimal -> percentage
        line_sum = sum(line)
        # factor = line_sum / 1
        line = [part / line_sum for part in line]
        size_percentages = line  # [part * factor for part in line]
        return [int(total_size * part) for part in size_percentages]
    else:  # If not -> assume int -> sizes in px
        factor = total_size / sum(line)
        return [int(size * factor) for size in line]


class Grid(StaticItem):
    def __init__(
        self,
        position: List[int] = [0, 0],
        rows: int = 1,
        columns: int = 1,
        row_sizes: Union[List[int], List[float]] = None,
        column_sizes: Union[List[int], List[float]] = None,
        size: Tuple[int, int] = None,
        visible: bool = False,
        selected: bool = False
    ):
        """
        Args:
            position (List[int] = [0, 0]): Position to place item on screen (or on page).
            rows (int): An integer representing number of rows.
            columns (int): An integer representing number of columns.
            row_sizes (Union[List[int], List[float]]): List of heights for each row, heights can either (all together)
                be integer values (representing height of each row in px) or float numbers (representing height of each
                row by percentage relative to grid size)
            column_sizes (Union[List[int], List[float]]): List of widths for each column, widths can either
                (all together) be integer values (representing width of each row in px) or float numbers
                (representing width of each row by percentage relative to grid size)
            size (Tuple[int, int] = (1, 1)): Size of item.
            visible (bool): If item is currently visible.
            selected (bool): If item is currently selected.

        Note:
            Adding less elements in row_sizes or column_sizes (ex. there's 5 rows you pass a list of 4 values) will
            result in the last one being added as an equal part to the total (width of grid if ints passed, or 1 if
            percentages (floats) passed).
            Adding more elements will just cut the additional ones off.
        """
        if not size:  # Fetch whole screen size if not passed
            size = pygame.display.get_surface().get_size()
        super().__init__(position=position, size=size, visible=visible, selected=selected)

        self._list: List[Row] = []
        self.number_of_rows, self.number_of_columns = rows, columns
        self.row_sizes = row_sizes
        self.column_sizes = column_sizes
        # Make rows and columns
        self.__make_row_and_column_sizes()
        self.__make(rows, columns)

    def __make_row_and_column_sizes(self) -> None:
        """
        Method constructs heights of rows and widths of columns in px so they can be generated in the __make method.
        """
        # Make rows
        if self.row_sizes:
            rows_sizes = make_grid_line(self.row_sizes, self.height, self.number_of_rows)
        else:
            equal_part = int(self.height / self.number_of_rows)
            rows_sizes = [equal_part for _ in range(self.number_of_rows)]
        self.row_sizes = rows_sizes
        # Make columns
        if self.column_sizes:
            rows_sizes = make_grid_line(self.column_sizes, self.width, self.number_of_columns)
        else:
            equal_part = int(self.width / self.number_of_columns)
            rows_sizes = [equal_part for _ in range(self.number_of_columns)]
        self.column_sizes = rows_sizes

    def __make(self, number_of_rows: int, number_of_columns: int) -> None:
        """
        Method creates grids list which contains rows of cells.

        Args:
            number_of_rows (int): Number of rows.
            number_of_columns (int): Number of columns.
        """
        curr_x, curr_y = 0, 0
        for i in range(number_of_rows):
            row = Row(self)
            for j in range(number_of_columns):
                row.append(
                    Cell(
                        grid=self,
                        position_in_grid=(i, j),
                        position=[curr_x, curr_y],
                        size=(self.column_sizes[j], self.row_sizes[i]),
                    )
                )
                curr_x += self.column_sizes[j]
            self._list.append(row)
            curr_x = 0
            curr_y += self.row_sizes[i]

    @property
    def rows(self):
        return len(self._list)

    @property
    def columns(self):
        return len(self._list[0])

    def add_item(self,
                 item: any,
                 row: int = None,
                 column: int = None,
                 align: str = None,
                 padding: str = None
                 ) -> None:
        """
        Method adds item to the grid in the specified cell at position row, column. Optional alignments, and paddings
        can be defined relative to the cell where the item is being added.

        Args:
            item (any): Item to add.
            row (int): Row in grid to add the item in. Starting at 0.
            column (int): Column in grid to add the item in. Starting at 0.
            align (str): Representing one or more alignment types. These include: centre, top, bottom, left, right.
                Centre should be defined first. Separate alignments using a space " ".
            padding (str): Representing one or more paddings of each side of the cell. Multiple can be passed by
                separating them with commas ",", each padding should be passed as "side px". Where sides include: top,
                bottom, left, right. Px represents an integer number of pixels to pad.
                Ex.: padding = "top 5, left 10"
        """
        self._list[row][column].add_item(item=item, align=alignment, padding=padding)

    def update(self):
        """ Method updates every item added to a cell in the grid. """
        for row in self._list:
            for cell in row:
                cell.update()

    def draw(self):
        """ Method draws every item added to a cell in the grid. """
        for row in self._list:
            for cell in row:
                cell.draw(visible=self.visible)  # Pass if self visible

    def __iter__(self):
        """ For iterating over grid. TODO: Decide if iterating should yield every item not row. """
        for row in self._list:
            yield row

    def __len__(self):
        """ List length """
        return len(self._list)

    def __getitem__(self, i):
        """ Get a list item """
        return self._list[i]

    def __delitem__(self, i):
        """ Delete an item """
        del self._list[i]

    def __setitem__(self, i, val):
        """ Set item """
        self._list[i] = val

    def __repr__(self):
        return "<{0} {1}>".format(self.__class__.__name__, self._list)

    def __str__(self):
        return str(self._list)
