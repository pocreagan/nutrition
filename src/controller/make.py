import os
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from typing import Dict
from typing import List
from typing import Tuple

from xlsxwriter import Workbook as xlsxWorkbook
from xlsxwriter.format import Format as xlsxFormat
from xlsxwriter.worksheet import Worksheet as xlsxWorksheet

from src import __RESOURCE__
from src.controller.constants import *
from src.controller.objects import *
from src.model.enums import NutrientLimitType

SAMPLE_FOODS = [
    Food('F1111', 'Formula 1 Cookies and Cream', 1.0, 'NA', ),
    Food('F2222', 'Protein Drink Mix Chocolate', 1.0, 'NA', ),
    Food('F3333', 'Prolessa Duo', 1.0, 'NA', ),
    Food('111111', 'Milk, lowfat', 2.0, '240 g', ),
    Food('222222', 'Bananas', 1.0, '120 g', ),
    Food('333333', 'Strawberries', 0.5, '80 g', ),
]

SAMPLE_NUTRIENTS = [
    Nutrient('Energy (kcal)', NutrientLimitType.NL, [200, 120, 50, 160, 80, 40, ]),
    Nutrient('Fat (mg)', 10, [2.5, 0, 5, 4, 0, 0, ]),
    Nutrient('Protein (mg)', 50, [15, 12, 2, 10, 0, 0, ]),
    Nutrient('beta-Carotene (mg)', 3000, [0, 0, 0, 20, 15, 40, ]),
    Nutrient('Vitamin A (mg)', 2501, [120, 0, 0, 50, 0, 0, ]),
]

SAMPLE_REGIONS = [
    Region(
        'US & Canada', 'US Tolerable Upper Intake Levels, Vitamins and Elements 2019',
        SAMPLE_FOODS, SAMPLE_NUTRIENTS,
    ),
    Region(
        'Australia & New Zealand', 'US Tolerable Upper Intake Levels, Vitamins and Elements 2019',
        SAMPLE_FOODS, SAMPLE_NUTRIENTS,
    ),
    Region(
        'China', 'US Tolerable Upper Intake Levels, Vitamins and Elements 2019',
        SAMPLE_FOODS, SAMPLE_NUTRIENTS,
    ),
]

today = datetime.now().date()

SAMPLE_OUTPUT = Output([('Performed:', today), ('App Version:', today - timedelta(days=15))], SAMPLE_REGIONS)


class Format:
    wb: xlsxWorkbook
    _cache: Dict[Tuple, xlsxFormat] = {}

    def __init__(self) -> None:
        self.d = {
            'font_name': FONT_NAME, 'valign': 'vcenter', 'align': 'center'
        }

    def _update(self, k, v):
        self.d[k] = v
        return self

    def date(self):
        return self._update('num_format', 'm/d/yyyy')

    def size(self, pt: int):
        return self._update('font_size', pt)

    def fail_fg(self):
        return self.font_color(NUTRIENT_FAIL_COLOR_FG)

    def fail_bg(self):
        return self.font_color(NUTRIENT_FAIL_COLOR_BG)

    def font_color(self, color: str):
        return self._update('font_color', color)

    def bg_color(self, color: str):
        return self._update('bg_color', color)

    def border_right(self):
        return self._update('right', 1)

    def border_left(self):
        return self._update('left', 1)

    def border_top(self):
        return self._update('top', 1)

    def border_bottom(self):
        return self._update('bottom', 1)

    def bold(self):
        return self._update('bold', True)

    def align(self, alignment: str):
        return self._update('align', alignment)

    def percentage(self):
        return self._update('num_format', '0%')

    def left(self):
        return self.align('left')

    def center(self):
        return self.align('center')

    def right(self):
        return self.align('right')

    def top(self):
        return self._update('valign', 'top')

    def bottom(self):
        return self._update('valign', 'vbottom')

    def rotated(self):
        return self._update('rotation', -90)

    def render(self) -> xlsxFormat:
        cla = type(self)
        frozen_d = tuple(sorted(self.d.items()))
        _fmt = cla._cache.get(frozen_d)
        if not _fmt:
            _fmt = cla.wb.add_format(self.d)
            cla._cache[frozen_d] = _fmt
        return _fmt

    def __call__(self) -> xlsxFormat:
        return self.render()


def new_sheet(wb: xlsxWorkbook, name: str) -> xlsxWorksheet:
    ws = wb.add_worksheet(name)
    # ws.set_zoom(160)

    return ws


def size_cells(ws: xlsxWorksheet,
               col_widths: List[Tuple[int, int, int]],
               row_heights: List[Tuple[int, int]], ) -> None:

    for row, height in [(0, BORDER_CELLS_SPAN_CHAR_UNITS)] + row_heights:
        ws.set_row_pixels(row, height=height)
    for col_i, col_f, width in [(0, 0, BORDER_CELLS_SPAN_CHAR_UNITS)] + col_widths:
        ws.set_column_pixels(col_i, col_f, width=width)


def make_region(wb: xlsxWorkbook, region: Region) -> None:
    ws = new_sheet(wb, region.name)

    row = 1
    ws.merge_range(row, 1, row, 4, region.name, Format().size(FontSizes.REGION_NAME)())
    row += 1
    fmt = Format()()
    fmt.set_text_wrap()
    ws.merge_range(row, 1, row, 4, region.limits_source, fmt)
    row += 2
    ws.merge_range(row, 1, row, 4, GUIDANCE_LEVEL_EXCEEDED_HEADER_STRING, Format().border_bottom()())
    row += 1
    bad_nutrients = [nut for nut in region.nutrients if nut.exceeds_guidance_level]
    if bad_nutrients:
        for nut in bad_nutrients:
            ws.merge_range(row, 1, row, 4, nut.name, Format().fail_fg()())
            row += 1
    else:
        ws.merge_range(row, 1, row, 4, 'NONE', Format()())

    row += 1

    size_cells(ws, REGION_COL_WIDTHS, REGION_ROW_HEIGHTS)


def make_summary(wb: xlsxWorkbook, output: Output) -> None:
    ws = new_sheet(wb, 'Summary')
    ws.insert_image(1, 1, __RESOURCE__.img('summary_logo.png'))

    row = 10
    for label, timestamp in output.versions:
        ws.write_string(row, 1, label, Format().bold().right()())
        ws.write_datetime(row, 2, timestamp, Format().left().date()())
        row += 1

    row += 1
    ws.write_string(row, 1, SUMMARY_RESULT_HEADER, Format().bold().right()())
    for region in output.regions:
        ws.write_string(row, 2, region.name, Format().right()())
        is_bad = region.exceeds_guidance_level
        fmt = Format().left()
        if is_bad:
            fmt.fail_fg().bold()
        ws.write_string(row, 3, SUMMARY_RESULT_STRINGS[is_bad], fmt())
        row += 1

    row += 1
    fmt = Format().top()()
    fmt.set_text_wrap()
    ws.merge_range(row, 1, row + 5, 3, SUMMARY_BLURB, fmt)

    ws.set_first_sheet()
    size_cells(ws, SUMMARY_COL_WIDTHS, SUMMARY_ROW_HEIGHTS)


def write_workbook(output: Output, name: str) -> None:
    output_file_path = Path(os.path.expanduser("~/Desktop")) / f'{name}.xlsx'
    if output_file_path.exists():
        os.remove(output_file_path)

    try:
        with xlsxWorkbook(str(output_file_path)) as wb:
            Format.wb = wb

            make_summary(wb, output)
            for region in output.regions:
                make_region(wb, region)

    except Exception:
        os.remove(output_file_path)
        raise

    else:
        os.system(f'"{output_file_path}"')


if __name__ == '__main__':
    write_workbook(SAMPLE_OUTPUT, 'test_file_name')
