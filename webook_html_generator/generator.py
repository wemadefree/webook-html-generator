import datetime
import jinja2
import shutil
import time
from slugify import slugify
from typing import List
from webook_html_generator.schema import (DisplayData, DisplayLayout, DisplayCombo,
                                          Login, Token, Event, ScreenResource,
                                          )
from webook_html_generator.data_handler import DataHandler
from webook_html_generator.config import Config


class Generator:
    def __init__(self, config: Config):
        self.config = config
        self.data_handler: DataHandler = None
        self.show_structure = None
        self.initialize()

    def _prepare_folder_structure(self):
        """screendisplay->location->room_name|layout|meeeting_place"""

        for loc in self.data_handler.locations:
            self.show_structure[slugify(loc.name)] = dict()
            for room in self.data_handler.rooms:
                try:
                    if room.location_id == loc.id:
                        self.show_structure[slugify(loc.name)][slugify(room.name)] = list()
                        shutil.copytree('template/whatson', f'html/{slugify(loc.name)}/{slugify(room.name)}/')
                except OSError as e:
                    print(f"Directory {loc.name}/{room.name} already exists!")
                except Exception as ex:
                    pass
            for layout in self.data_handler.layouts:
                try:
                    if not layout.is_room_based:
                        self.show_structure[slugify(loc.name)][slugify(slugify(layout.name))] = list()
                        shutil.copytree('template/whatson', f'html/{slugify(loc.name)}/{slugify(layout.name)}/')
                except OSError as e:
                    print(f"Directory {loc.name}/{layout.name} already exists!")
                except Exception as ex:
                    pass
            for screen_res in self.data_handler.screens:
                try:
                    if not screen_res.room_id:
                        self.show_structure[slugify(loc.name)][slugify(slugify(screen_res.screen_model))] = list()
                        shutil.copytree('template/whatson', f'html/{slugify(loc.name)}/'
                                                            f'{slugify(screen_res.screen_model)}/')
                except OSError as e:
                    print(f"Directory {loc.name}/{slugify(screen_res.screen_model)} already exists!")
                except Exception as ex:
                    pass

        print(self.show_structure)

    def render_html(self, all_events: List[Event]):
        self.initialize()
        self.arrange_for_display(all_events)
        for loc in self.show_structure:
            for key in self.show_structure[loc]:
                with open(f'template/whatson/index.html', 'r', encoding="utf-8") as f:
                    contents = f.read()
                template = jinja2.Template(contents)
                display = DisplayCombo(title=key, data=self.show_structure[loc][key])
                context = {
                    'now': datetime.datetime.now(),
                    'in_half_hour': datetime.datetime.now() + datetime.timedelta(minutes=30),
                }
                filled_template = template.render(display=display, **context)
                with open(f'html/{loc}/{key}/index.html', 'w', encoding="utf-8") as f:
                    f.write(filled_template)

    def arrange_for_display(self, all_events: List[Event]):
        layout_dict = {layout.name: layout for layout in self.data_handler.layouts}

        for event in all_events:
            arr_layout_names = [layout.name for layout in event.arrangement.display_layouts]
            for event_layout in event.display_layouts:
                if event_layout.name in layout_dict and event_layout.name in arr_layout_names:
                    if layout_dict.get(event_layout.name).is_room_based:
                        if event.arrangement.location:
                            sl = slugify(event.arrangement.location.name)
                            for room in event.rooms:
                                sr = slugify(room.name)
                                self.add_for_display(self.show_structure.get(sl).get(sr),
                                                     event, room_name=room.name)
                    elif not layout_dict.get(event_layout.name).is_room_based:
                        if event.arrangement.location:
                            sl = slugify(event.arrangement.location.name)
                            se = slugify(event_layout.name)
                            if event.rooms:
                                room_names = [room.name for room in event.rooms]
                                self.add_for_display(self.show_structure.get(sl).get(se),
                                                     event, room_name=",".join(room_names))
                            elif event.arrangement.meeting_place:
                                self.add_for_display(self.show_structure.get(sl).get(se),
                                                     event, room_name=event.arrangement.meeting_place)

    def add_for_display(self, screen_showcase: List, event: Event, room_name: str = ""):
        if event.arrangement.name:
            screen_showcase.append(DisplayData().set_fields(event, room_name=room_name, international=False))
        if event.arrangement.name_en:
            screen_showcase.append(DisplayData().set_fields(event, room_name=room_name, international=True))

    def initialize(self):
        self.data_handler = DataHandler(self.config)
        self.show_structure = dict()
        self._prepare_folder_structure()

    def handler(self):
        while not self.data_handler.token:
            self.data_handler.refresh_token()
            time.sleep(30)
        self.render_html(self.data_handler.events)








