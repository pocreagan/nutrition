from typing import Dict
from typing import Union

from kivy import Logger
from kivy.clock import mainthread
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import BooleanProperty
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.snackbar import BaseSnackbar
from kivymd.uix.textfield import MDTextField

from src import __RESOURCE__
from src.base import loggers
from src.model.config import Model
from src.view.utils import hide
from src.view.utils import show

__all__ = [
    'View',
]


class FoodQTYField(MDTextField):
    app: 'View' = ObjectProperty(None)
    root: 'FoodCard' = ObjectProperty(None)

    def on_text_validate(self) -> None:
        try:
            qty = float(self.text)
            if qty <= 0.:
                raise ValueError

        except ValueError:
            self.app.warning_snackbar(f'`{self.text}` is not a valid QTY')
            self.text = str(self.root.validated_qty)

        else:
            self.root.validated_qty = qty
            self.text = str(qty)

        super().on_text_validate()

    def on_focus(self, _arg, is_focused: bool) -> None:
        if self.text != '1.0' and not is_focused:
            self.text = str(self.root.validated_qty)
        super().on_focus(_arg, is_focused)


class FoodCard(MDCard):
    food_id = StringProperty('Food ID')
    description = StringProperty('Food Description')
    QTY = StringProperty('Food QTY')
    UOM = StringProperty('Food UOM')
    source = StringProperty('Food Source')

    qty_field: FoodQTYField = ObjectProperty(None)

    def __init__(self, **kwargs) -> None:
        self.validated_qty = 0.
        super().__init__(**kwargs)


class LoadingScreen(FloatLayout):
    label = ObjectProperty(None)


class RootWidget(BoxLayout):
    food_fields: BoxLayout = ObjectProperty(None)
    food_id_input_field: MDTextField = ObjectProperty(None)
    loading_screen: BoxLayout = ObjectProperty(None)
    running_screen: BoxLayout = ObjectProperty(None)
    no_foods_yet_label: BoxLayout = ObjectProperty(None)
    food_list_field: BoxLayout = ObjectProperty(None)
    log: Logger

    def toggle_field_view(self) -> None:
        if self.food_fields.children:
            show(self.food_fields)
            self.log.debug('Hiding no_foods_yet_label')
            hide(self.no_foods_yet_label)
        else:
            hide(self.food_fields)
            self.log.debug('Showing no_foods_yet_label')
            show(self.no_foods_yet_label)


class CustomSnackbar(BaseSnackbar):
    text = StringProperty(None)
    icon = StringProperty(None)
    font_size = NumericProperty("20sp")


class View(MDApp):
    model: Model
    root: RootWidget
    is_loading = BooleanProperty(True)
    is_processing = BooleanProperty(True)
    logo_source = StringProperty('sam_logo.png')

    def __init__(self, **kwargs) -> None:
        self.log = loggers.Logger('View', Logger)
        kwargs['title'] = 'Sam'
        self.stack: Dict[int, FoodCard] = dict()
        super().__init__(**kwargs)

    @mainthread
    def start_model_building(self) -> None:
        self.log.debug('Starting model building thread')
        from src.model.model import build_model
        from threading import Thread
        Thread(
            target=build_model, name='ModelBuilderThread', args=(self.log, self.add_model,), daemon=True,
        ).start()

    @mainthread
    def add_model(self, model: Union[Exception, Model]) -> None:
        self.is_loading = False
        if isinstance(model, Exception):
            self.is_processing = False
            self.log.error(f'Model building failed. <{str(model)}>', exc_info=False)
            self.root.loading_screen.label.text = 'failed to load food data\nplease seek technical support'

        else:
            self.log.info('Received built model')
            self.model = model
            hide(self.root.loading_screen, self.root.no_foods_yet_label)
            show(self.root.running_screen)
            self.add_food('1102695')
            self.add_food('173166')
            self.add_food('171909')
            self.add_food('167787')
            self.add_food('170913')
            self.add_food('1102757')

    def build(self):
        self.start_model_building()
        self.theme_cls.primary_palette = "Green"
        self.root: RootWidget = Builder.load_file(__RESOURCE__.cfg('view.kv'))
        self.root.log = self.log
        hide(self.root.running_screen)
        return self.root

    def warning_snackbar(self, text: str) -> None:
        snackbar = CustomSnackbar(
            text=text,
            icon="information",
            snackbar_x="10dp",
            snackbar_y="10dp",
        )
        snackbar.size_hint_x = (Window.width - (snackbar.snackbar_x * 2)) / Window.width
        snackbar.open()

    @mainthread
    def clear_field(self, do_clear_text: bool = True) -> None:
        if do_clear_text:
            self.root.food_id_input_field.text = ''
        self.root.food_id_input_field.focus = True

    def add_food(self, text: str) -> None:
        if not text:
            return
        try:
            food_id = int(text)
            food = self.model.foods.get(food_id, None)
            if food is None:
                raise TypeError

        except TypeError:
            self.clear_field(do_clear_text=False)
            return self.warning_snackbar(f'Food ID `{text}` was not found')

        if food_id in self.stack:
            scroll_to_widget = self.stack[food_id]
            self.warning_snackbar(f'Food ID {food_id} is already in the stack')

        else:
            food_card = FoodCard()
            food_card.food_id = str(food_id)
            food_card.description = food['description']
            food_card.QTY = str(food['QTY'])
            food_card.UOM = food['UOM']
            food_card.source = food["source"]
            self.stack[food_id] = food_card
            self.root.food_fields.add_widget(food_card)
            scroll_to_widget = food_card

        @mainthread
        def scroll_to_widget_callback(widget):
            if self.root.food_fields.height > self.root.food_list_field.height:
                self.root.food_list_field.scroll_to(widget)

        scroll_to_widget_callback(scroll_to_widget)
        self.clear_field()

    def analyze(self) -> None:
        self.log.info('Analyze button pressed')

    def remove_from_stack(self, food_card: FoodCard) -> None:
        food_id = food_card.food_id
        del self.stack[int(food_id)]

        self.root.food_fields.remove_widget(food_card)
        self.log.info(f'Removed food `{food_card.food_id}` from stack')
        if self.stack:
            hide(self.root.no_foods_yet_label)
        else:
            show(self.root.no_foods_yet_label)
        # self.root.toggle_field_view()

    @mainthread
    def close_app(self) -> None:
        self.get_running_app().stop()


if __name__ == '__main__':
    View().run()
