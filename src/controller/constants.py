FONT_NAME = 'Corbel Light'
NUTRIENT_FAIL_COLOR_FG = '#FF0000'
NUTRIENT_FAIL_COLOR_BG = '#FF9999'
INGREDIENT_DISPLAY_NAME_MAX_WIDTH_PX = 345
STANDARD_COLUMN_WIDTH_CHAR_UNITS = 68
BORDER_CELLS_SPAN_CHAR_UNITS = 28

GUIDANCE_LEVEL_EXCEEDED_HEADER_STRING = 'Guidance Level(s) Exceeded'

SUMMARY_RESULT_HEADER = 'Result:'

# noinspection SpellCheckingInspection
SUMMARY_BLURB = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque eget ipsum non turpis scelerisque ' \
                'consectetur. Donec tristique elit non magna semper, sed tincidunt nunc condimentum. Vivamus eu ' \
                'volutpat sem. Cras scelerisque finibus nisi, id ultrices magna lacinia non. Proin id finibus ipsum, ' \
                'vitae efficitur leo. Aliquam sit amet metus enim. '

SUMMARY_RESULT_STRINGS = {
    True: GUIDANCE_LEVEL_EXCEEDED_HEADER_STRING,
    False: 'OK'
}

SUMMARY_COL_WIDTHS = [
    (1, 1, 140),
    (2, 3, 230),
    (4, 50, 96),
]

SUMMARY_ROW_HEIGHTS = []

REGION_COL_WIDTHS = [
    (1, 1, 152),
    (2, 2, 345),
    (3, 100, 68),
]

REGION_ROW_HEIGHTS = [
    (1, 62),
    (2, 62),
    (7, 184),
]


class RegionWidths:
    STANDARD = 68
    COL_B = 122
    COL_C = 345


class FontSizes:
    STANDARD = 11
    REGION_NAME = 24


class FoodHeaders:
    FOOD_ID = 'ID'
    DESCRIPTION = 'Description'
    NUM_SERVINGS = '# of Servings'
    QTY_PER_SERVING = 'Quantity / Serving'


class CalcHeaders:
    SUM = 'Sum'
    GUIDANCE_LEVEL = 'Guidance Level ({region_name})'
    PERCENT_OF_LIMIT = '% of Guidance Level'
