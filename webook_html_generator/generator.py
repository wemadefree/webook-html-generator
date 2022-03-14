import json
import requests
import jinja2
from webook_html_generator.schema import ArrangementRead, Login, Token
from webook_html_generator.config import Config


class Generator:
    def __init__(self, config: Config):
        self.config = config

    def get_token(self) -> Token:
        """Returns the token for a request"""

        print(self.config.__dict__)
        login = Login(username=self.config.user_name, password=self.config.password)
        try:
            req = requests.post(self.config.login_url, data=login.__dict__)
            req.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Http Login Error:", err)
            return None
        return json.loads(req.content)

    def get_arrangement_request(self, id: int) -> ArrangementRead:
        """Returns the data from a request (eg /arrangement)"""
        token: Token = self.get_token()
        print(token)
        url = f'{self.config.base_url}{"arrangement/"}{id}'
        req = requests.get(url)
        if not req.content:
            return None
        return json.loads(req.content)

    def make_template(self):
        arrangement = self.get_arrangement_request(1)
        print(arrangement)
        print(self.config.base_url)
        with open('template/person.html', 'r') as f:
            contents = f.read()

        template = jinja2.Template(contents)
        filled_template = template.render(person=arrangement)

        with open('html/output.html', 'w') as f:
            f.write(filled_template)






