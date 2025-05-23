import warnings
from IPython.display import display_markdown
import re
from typing import List

warnings.simplefilter("once", category=UserWarning)

class ArraySizeError(Exception):
    """Exception raised when specified rows don't fit the required size
    """

    def __init__(self, msg):
        self.msg = msg
        Exception.__init__(self, msg, '')

    def __str__(self):
        return self.msg

class ModifiedTexttable:
    def __init__(self):

        self._row_size = None
        self._align = None
        self._header = []
        self._rows = []
        self._width = []
        
        self.set_chars(new_chars=["-", "|", "|", "-"])

    def set_chars(self, new_chars: List[str]):

        if len(new_chars) != 4: 
            raise ArraySizeError(f"a length of new_chars should be 4, but {len(new_chars)}")
        
        (self._char_horiz, self._char_vert, 
         self._char_corner, self._char_header) = new_chars
        
    def check_row_size(self, array: list):
        if self._row_size is None:
            self._row_size = len(array)
        elif self._row_size != len(array):
            raise ArraySizeError(f"a length of new_chars should be {self._row_size}, but {len(array)}")

    def set_cols_align(self, configs: list):

        self.check_row_size(configs)

        self._align = configs

    def add_header(self, header: list):

        self.check_row_size(header)

        self._header = header

    def check_width(self, rows: list):

        new_width = []
        for idx, content in enumerate(rows):
            new_width.append(max(len(content), self._width[idx]))
        self._width = new_width

    def add_rows(self, rows: list, header=False):

        self._width = list(map(len, rows[0]))

        if header:
            self.add_header(rows[0])
            rows = rows[1:]

        self.check_row_size(rows[0])

        rev_rows = []
        for cols in rows:
            rev_cols = []
            for col in cols:
                content = str(col)
                rev_content = re.compile(r"\n").sub("<br>", content)
                rev_cols.append(rev_content)
            self.check_width(rev_cols)
            rev_rows.append(rev_cols)
        self._rows.extend(rev_rows)

    def _draw_line(self, rows: list, is_header: bool = False):
            
        space = " "

        if is_header:
            rows = [rows]

        output = ""
        for cols in rows:
            output += "{sp_token} ".format(sp_token=self._char_vert)
            for idx, col in enumerate(cols):
                output += "{content} ".format(content=col.center(self._width[idx], space))
                if idx < len(cols) - 1:
                    output += "{sp_token} ".format(sp_token=self._char_vert) 
            output += "{sp_token}\n".format(sp_token=self._char_vert)
        return output
    
    def _build_hline(self):
        output = "{}".format(self._char_vert)

        header_cols = []
        for idx, w in enumerate(self._width):
            middle = self._char_header * w

            if self._align is None:
                middle = f"-{middle}-"
            elif self._align[idx] == "l":
                middle = f":{middle}-"
            elif self._align[idx] == "r":
                middle = f"-{middle}:"
            elif self._align[idx] == "c":
                middle = f":{middle}:"

            header_cols.append(middle)

        output += "{}".format(self._char_corner).join(header_cols)
        output += "{}\n".format(self._char_vert)
        return output
    
    def draw(self):

        if len(self._header) == 0 and len(self._rows) == 0:
            warnings.warn("Since header or rows have nothing.", UserWarning)
            warnings.simplefilter("ignore", UserWarning)
            return
        
        output = ""
        if self._header:
            output += self._draw_line(self._header, is_header=True)
            output += self._build_hline()
            output += self._draw_line(self._rows)
        
        return output[:-1]