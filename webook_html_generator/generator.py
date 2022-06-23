import datetime
import logging
import jinja2
import shutil
import time
from slugify import slugify
from typing import List
from webook_html_generator.schema import (DisplayData, DisplayLayout, DisplayCombo,
                                          Login, Token, Event, ScreenResource, Room,
                                          )
from webook_html_generator.data_handler import DataHandler
from webook_html_generator.config import Config


class Generator:
    def __init__(self, config: Config):
        self.config = config
        self.data_handler: DataHandler = None
        self.prepared_data_source: dict = None
        self.local_to_international_keys: dict = {}

    def _prepare_data_sources(self):

        self.prepared_data_source = dict()
        self.local_to_international_keys: dict = {}

        """screendisplay->location->room_name|layout|meeeting_place"""

        for loc in self.data_handler.locations:
            self.prepared_data_source[slugify(loc.name)] = dict()
            for room in self.data_handler.rooms:
                try:
                    if room.location_id == loc.id:
                        self.prepared_data_source[slugify(loc.name)][slugify(room.name)] = list()
                        source = 'template/whatson'
                        dest = f'{self.config.upload_dir}/{slugify(loc.name)}/{slugify(room.name)}'
                        self._copy_resources(source, dest, resources=['css', 'fonts'])

                except Exception as ex:
                    logging.error(f"Error in preparing folder structure for rooms: Details: {ex}")
            for layout in self.data_handler.layouts:
                try:
                    if not layout.is_room_based:
                        self.prepared_data_source[slugify(loc.name)][slugify(slugify(layout.name))] = list()
                        if slugify(layout.name) == 'mmg':
                            self.local_to_international_keys[slugify(layout.name)] = slugify(layout.name)+'-en'
                            source = 'template/mmg'
                            dest = f'{self.config.upload_dir}/{slugify(loc.name)}/mmg'
                            self._copy_resources(source, dest, resources=['css', 'fonts'])
                            dest = f'{self.config.upload_dir}/{slugify(loc.name)}/mmg-en'
                            self._copy_resources(source, dest, resources=['css', 'fonts'])
                        else:
                            self.local_to_international_keys[slugify(layout.name)] = slugify(layout.name)+'-en'
                            source = 'template/whatson'
                            dest = f'{self.config.upload_dir}/{slugify(loc.name)}/{slugify(layout.name)}'
                            self._copy_resources(source, dest, resources=['css', 'fonts'])
                            dest = f'{self.config.upload_dir}/{slugify(loc.name)}/{slugify(layout.name)}-en'
                            self._copy_resources(source, dest, resources=['css', 'fonts'])
                except Exception as ex:
                    logging.error(f"Error in preparing folder structure for layouts: Details: {ex}")
            for screen_res in self.data_handler.screens:
                try:
                    if not screen_res.room_id:
                        self.prepared_data_source[slugify(loc.name)][slugify(slugify(screen_res.screen_model))] = list()
                        source = 'template/whatson'
                        dest = f'{self.config.upload_dir}/{slugify(loc.name)}/{slugify(screen_res.screen_model)}'
                        self._copy_resources(source, dest, resources=['css', 'fonts'])
                except Exception as ex:
                    logging.error(f"Error in preparing folder structure for screen resources: Details: {ex}")

    def _copy_resources(self, source: str, dest: str, resources: List):
        """
        Copying resources from templates like css, fonts to appropriate folders
        :param source: source folder of  - relative path
        :param dest: destination folder path
        :param resources: list of resource names -> Example: resource = [css, fonts]
        :return: None
        """
        if resources:
            for resource_name in resources:
                shutil.copytree(f'{source}/{resource_name}', f'{dest}/{resource_name}/', dirs_exist_ok=True)
        else:
            shutil.copytree(f'{source}', f'{dest}/', dirs_exist_ok=True)

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
                                                         event, 'room_based', room)
                        elif not layout_dict.get(event_layout.name).is_room_based:
                            if event.arrangement.location:
                                sl = slugify(event.arrangement.location.name)
                                se = slugify(event_layout.name)
                                self.add_event_to_screen_showcase(self.prepared_data_source.get(sl), se,
                                                                   event, 'layout_based')
            except Exception as ex:
                logging.error(f"Error in arranging events: Details: {ex}")

    def _copy_mmg_route(self, dest_part: str ='whatson/mmg'):
        try:
            source = f'{self.config.upload_dir}/{self.config.mmg_dir}'
            dest = f'{self.config.upload_dir}/{dest_part}'
            self._copy_resources(source, dest, resources=None)
            self._copy_resources(source+'-en', dest+'-en', resources=None)
        except Exception as ex:
            logging.error(f"Error in copy mmg files to whatson folder: Details: {ex}")

    def custom_activities(self):
        self._copy_mmg_route()

    def add_event_to_screen_showcase(self, screen_showcase: dict, key: str, event: Event,
                                     room_name_type: str, room: Room = None):
        room_name = ''
        room_name_en = ''
        if room_name_type == 'room_based' and room:
            room_name = room.name
            if room.name_en:
                room_name_en = room.name_en
            else:
                room_name_en = room_name
        elif room_name_type == 'layout_based':
            if event.arrangement.meeting_place:
                room_name = event.arrangement.meeting_place
                if event.arrangement.meeting_place_en:
                    room_name_en = event.arrangement.meeting_place_en
                else:
                    room_name_en = room_name
            elif event.rooms:
                room_names = [room.name for room in event.rooms]
                room_names_en = [room.name_en if room.name_en else room.name for room in event.rooms]
                room_name = ",".join(room_names)
                room_name_en = ",".join(room_names_en)

        display_data = DisplayData()
        display_data.set_fields(event, room_name=room_name, international=False)
        screen_showcase[key].append(display_data)

        if event.title_en or event.arrangement.display_text_en:
            display_data = DisplayData()
            display_data.set_fields(event, room_name=room_name_en, international=True)
            screen_showcase[key].append(display_data)

    def _limit_number_of_events_per_screen(self, key: str, event_list):
        if key not in ('mmg', 'mmg-en'):
            event_list[key] = event_list[key][0:int(self.config.max_screen_items)]

    def render_html(self):
        self._prepare_data_sources()
        self.arrange_for_display(self.data_handler.current_events)
        self.arrange_for_display(self.data_handler.next_events)
        for loc in self.prepared_data_source:
            self._separate_local_from_international(self.prepared_data_source[loc])

            for key in self.prepared_data_source[loc]:
                self._limit_number_of_events_per_screen(key, self.prepared_data_source[loc])
                try:
                    if key in ('mmg', 'mmg-en'):
                        with open(f'template/mmg/_index.html', 'r', encoding="utf-8") as f:
                            contents = f.read()
                    else:
                        with open(f'template/whatson/_index.html', 'r', encoding="utf-8") as f:
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
                    logging.error(f"Error in rendering {loc}/{key} html: Details: {ex}")
        self.custom_activities()

    def _separate_local_from_international(self, data_source):
        """
        This function separate mmg into international and local channel.
        It creates new key 'mmg-en' int data-source which contains list of international events
        :param data_source:
        :return: None
        """
        for key in self.local_to_international_keys:
            if key in data_source:
                key_en = []
                for i, evt in reversed(list(enumerate(data_source[key]))):
                    if evt.international:
                        key_en.append(data_source[key].pop(i))
                key_en.reverse()
                data_source[key+'-en'] = key_en

    def handler(self):
        logging.info(f"-------------------------------------------------------------------------------------")
        logging.info(f"New iteration of generating started")
        self.data_handler = DataHandler(self.config)
        self.data_handler.retrieve_data()

        while not self.data_handler.is_valid:
            logging.warning(f"Data handler is not valid, please check. Trying to retrieve data")
            self.data_handler.retrieve_data()
            time.sleep(30)
        self.render_html()








