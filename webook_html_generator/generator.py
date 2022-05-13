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

    def _prepare_folder_show_structure(self):
        """screendisplay->location->room_name|layout|meeeting_place"""

        for loc in self.data_handler.locations:
            self.show_structure[slugify(loc.name)] = dict()
            for room in self.data_handler.rooms:
                try:
                    if room.location_id == loc.id:
                        self.show_structure[slugify(loc.name)][slugify(room.name)] = list()
                        shutil.copytree('template/whatson',
                                        f'{self.config.upload_dir}/{slugify(loc.name)}/{slugify(room.name)}/', dirs_exist_ok=True)
                except Exception as ex:
                    print(f"{datetime.datetime.now()} - Error in preparing folder structure: Details: {ex}")
            for layout in self.data_handler.layouts:
                try:
                    if not layout.is_room_based:
                        self.show_structure[slugify(loc.name)][slugify(slugify(layout.name))] = list()
                        shutil.copytree('template/whatson',
                                        f'{self.config.upload_dir}/{slugify(loc.name)}/{slugify(layout.name)}/', dirs_exist_ok=True)
                except Exception as ex:
                    print(f"{datetime.datetime.now()} - Error in preparing folder structure: Details: {ex}")
            for screen_res in self.data_handler.screens:
                try:
                    if not screen_res.room_id:
                        self.show_structure[slugify(loc.name)][slugify(slugify(screen_res.screen_model))] = list()
                        shutil.copytree('template/whatson',
                                        f'{self.config.upload_dir}/{slugify(loc.name)}/'f'{slugify(screen_res.screen_model)}/',
                                        dirs_exist_ok=True)
                except Exception as ex:
                    print(f"{datetime.datetime.now()} - Error in preparing folder structure: Details: {ex}")

    def arrange_for_display(self, all_events: List[Event]):
        layout_dict = {layout.name: layout for layout in self.data_handler.layouts}

        for event in all_events:
            arr_layout_names = [layout.name for layout in event.arrangement.display_layouts]
            try:
                for event_layout in event.display_layouts:
                    if event_layout.name in layout_dict and event_layout.name in arr_layout_names:
                        if layout_dict.get(event_layout.name).is_room_based:
                            if event.arrangement.location:
                                sl = slugify(event.arrangement.location.name)
                                for room in event.rooms:
                                    sr = slugify(room.name)
                                    self.adding_to_screen_showcase(self.show_structure.get(sl).get(sr),
                                                         event, room_name=room.name)
                        elif not layout_dict.get(event_layout.name).is_room_based:
                            if event.arrangement.location:
                                sl = slugify(event.arrangement.location.name)
                                se = slugify(event_layout.name)
                                if event.rooms:
                                    room_names = [room.name for room in event.rooms]
                                    self.adding_to_screen_showcase(self.show_structure.get(sl).get(se),
                                                         event, room_name=",".join(room_names))
                                elif event.arrangement.meeting_place:
                                    self.adding_to_screen_showcase(self.show_structure.get(sl).get(se),
                                                         event, room_name=event.arrangement.meeting_place)
                                else:
                                    self.adding_to_screen_showcase(self.show_structure.get(sl).get(se),
                                                                   event, room_name="")
            except Exception as ex:
                print(f"{datetime.datetime.now()} - Error in arranging events: Details: {ex}")

    def _copy_mmg_route(self, dest_part: str ='whatson/mmg'):
        try:
            shutil.copytree(f'{self.config.upload_dir}/{self.config.mmg_dir}',
                            f'{self.config.upload_dir}/{dest_part}/', dirs_exist_ok=True)
        except Exception as ex:
            print(f"{datetime.datetime.now()} - Error in copy mmg files: Details: {ex}")

    def custom_activities(self):
        self._copy_mmg_route()

    def adding_to_screen_showcase(self, screen_showcase: List, event: Event, room_name: str = ""):
        if event.arrangement.name:
            display_data = DisplayData()
            display_data.set_fields(event, room_name=room_name, international=False)
            screen_showcase.append(display_data)
        if event.arrangement.name_en:
            display_data = DisplayData()
            display_data.set_fields(event, room_name=room_name, international=True)
            screen_showcase.append(display_data)

    def initialize(self):
        self.data_handler = DataHandler(self.config)
        self.show_structure = dict()
        if self.data_handler.validate():
            self._prepare_folder_show_structure()
        else:
            print(f"{datetime.datetime.now()} - Error in preparing folder structure: Details: datahandler not sett")
            return False

    def render_html(self, all_events: List[Event]):
        self.arrange_for_display(all_events)
        for loc in self.show_structure:
            for key in self.show_structure[loc]:
                try:
                    with open(f'template/whatson/index.html', 'r', encoding="utf-8") as f:
                        contents = f.read()
                    template = jinja2.Template(contents)
                    display = DisplayCombo(title=key, data=self.show_structure[loc][key])
                    context = {
                        'now': datetime.datetime.now(),
                        'in_half_hour': datetime.datetime.now() + datetime.timedelta(minutes=30),
                    }
                    filled_template = template.render(display=display, **context)
                    with open(f'{self.config.upload_dir}/{loc}/{key}/index.html', 'w', encoding="utf-8") as f:
                        f.write(filled_template)
                except Exception as ex:
                    print(f"{datetime.datetime.now()} - Error in rendering {loc}/{key} html: Details: {ex}")
        self.custom_activities()

    def handler(self):
        print(f"{datetime.datetime.now()} - Try to generate html")
        self.initialize()
        while not self.data_handler.validate():
            self.initialize()
            time.sleep(30)
        self.render_html(self.data_handler.events)








