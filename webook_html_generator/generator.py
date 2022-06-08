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
        self.prepared_data_source: dict = None

    def _prepare_data_sources(self):

        self.prepared_data_source = dict()

        """screendisplay->location->room_name|layout|meeeting_place"""

        for loc in self.data_handler.locations:
            self.prepared_data_source[slugify(loc.name)] = dict()
            for room in self.data_handler.rooms:
                try:
                    if room.location_id == loc.id:
                        self.prepared_data_source[slugify(loc.name)][slugify(room.name)] = list()
                        shutil.copytree('template/whatson',
                                        f'{self.config.upload_dir}/{slugify(loc.name)}/{slugify(room.name)}/', dirs_exist_ok=True)
                except Exception as ex:
                    print(f"{datetime.datetime.now()} - Error in preparing folder structure: Details: {ex}")
            for layout in self.data_handler.layouts:
                try:
                    if not layout.is_room_based:
                        self.prepared_data_source[slugify(loc.name)][slugify(slugify(layout.name))] = list()
                        if slugify(layout.name) == "mmg":
                            shutil.copytree('template/mmg',
                                            f'{self.config.upload_dir}/{slugify(loc.name)}/{slugify(layout.name)}/',
                                            dirs_exist_ok=True)
                            shutil.copytree('template/mmg',
                                            f'{self.config.upload_dir}/{slugify(loc.name)}/{slugify(layout.name+"-en")}/',
                                            dirs_exist_ok=True)
                        else:
                            shutil.copytree('template/whatson',
                                            f'{self.config.upload_dir}/{slugify(loc.name)}/{slugify(layout.name)}/',
                                            dirs_exist_ok=True)
                except Exception as ex:
                    print(f"{datetime.datetime.now()} - Error in preparing folder structure: Details: {ex}")
            for screen_res in self.data_handler.screens:
                try:
                    if not screen_res.room_id:
                        self.prepared_data_source[slugify(loc.name)][slugify(slugify(screen_res.screen_model))] = list()
                        shutil.copytree('template/whatson',
                                        f'{self.config.upload_dir}/{slugify(loc.name)}/{slugify(screen_res.screen_model)}/',
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
                                    self.add_event_to_screen_showcase(self.prepared_data_source.get(sl), sr,
                                                         event, room_name=room.name)
                        elif not layout_dict.get(event_layout.name).is_room_based:
                            if event.arrangement.location:
                                sl = slugify(event.arrangement.location.name)
                                se = slugify(event_layout.name)
                                if event.arrangement.meeting_place:
                                    self.add_event_to_screen_showcase(self.prepared_data_source.get(sl), se,
                                                                   event, room_name=event.arrangement.meeting_place)
                                elif event.rooms:
                                    room_names = [room.name for room in event.rooms]
                                    self.add_event_to_screen_showcase(self.prepared_data_source.get(sl), se,
                                                         event, room_name=",".join(room_names))
                                else:
                                    self.add_event_to_screen_showcase(self.prepared_data_source.get(sl), se,
                                                                   event, room_name="")
            except Exception as ex:
                print(f"{datetime.datetime.now()} - Error in arranging events: Details: {ex}")

    def _copy_mmg_route(self, dest_part: str ='whatson/mmg'):
        try:
            shutil.copytree(f'{self.config.upload_dir}/{self.config.mmg_dir}',
                            f'{self.config.upload_dir}/{dest_part}/', dirs_exist_ok=True)
            shutil.copytree(f'{self.config.upload_dir}/{self.config.mmg_dir+"-en"}',
                            f'{self.config.upload_dir}/{dest_part+"_en"}/', dirs_exist_ok=True)
        except Exception as ex:
            print(f"{datetime.datetime.now()} - Error in copy mmg files: Details: {ex}")

    def custom_activities(self):
        self._copy_mmg_route()

    def add_event_to_screen_showcase(self, screen_showcase: dict, key: str, event: Event, room_name: str = ""):
        if event.arrangement.name:
            display_data = DisplayData()
            display_data.set_fields(event, room_name=room_name, international=False)
            if key == 'mmg':
                screen_showcase[key].append(display_data)
            else:
                if len(screen_showcase[key]) < int(self.config.max_screen_items):
                    screen_showcase[key].append(display_data)

        if event.arrangement.name_en:
            display_data = DisplayData()
            display_data.set_fields(event, room_name=room_name, international=True)
            if key == 'mmg':
                screen_showcase[key].append(display_data)
            else:
                if len(screen_showcase[key]) < int(self.config.max_screen_items):
                    screen_showcase[key].append(display_data)

    def render_html(self):
        self._prepare_data_sources()
        self.arrange_for_display(self.data_handler.current_events)
        self.arrange_for_display(self.data_handler.next_events)
        for loc in self.prepared_data_source:
            self._separate_mmg(self.prepared_data_source[loc])

            for key in self.prepared_data_source[loc]:
                try:
                    if key in ('mmg', 'mmg-en'):
                        with open(f'template/mmg/index.html', 'r', encoding="utf-8") as f:
                            contents = f.read()
                    else:
                        with open(f'template/whatson/index.html', 'r', encoding="utf-8") as f:
                            contents = f.read()
                    template = jinja2.Template(contents)
                    display = DisplayCombo(title=key, data=self.prepared_data_source[loc][key])
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

    def _separate_mmg(self, data_source):
        """
        This function separate mmg into international and local channel.
        It creates new key 'mmg-en' int data-source which contains list of international events
        :param data_source:
        :return: None
        """
        if 'mmg' in data_source:
            mmg_en = []
            for i, evt in reversed(list(enumerate(data_source['mmg']))):
                if evt.international:
                    mmg_en.append(data_source['mmg'].pop(i))
            mmg_en.reverse()
            data_source['mmg-en'] = mmg_en

    def handler(self):
        print(f"{datetime.datetime.now()} - Try to generate html")
        self.data_handler = DataHandler(self.config)
        self.data_handler.retrieve_data()

        while not self.data_handler.is_valid:
            self.data_handler.retrieve_data()
            time.sleep(30)
        self.render_html()








