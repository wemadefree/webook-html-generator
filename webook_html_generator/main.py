import json
import os
import requests
import jinja2
from dotenv import load_dotenv
from pathlib import Path
from webook_html_generator.schema import Person


dotenv_path = Path('../.env')
load_dotenv(dotenv_path=dotenv_path)

API_KEY = os.getenv('API_KEY')
BASE_URL = os.getenv('BASE_URL')


def api_request(request) -> Person:
    '''Returns the data from a request (eg /persons)'''
    #rl = f'{BASE_URL}{request}?token={API_KEY}'
    url = f'{BASE_URL}{request}'
    req = requests.get(url)

    if not req.content:
        return None

    # We only want the data associated with the "response" key
    return json.loads(req.content)[0]


if __name__ == '__main__':
    person = api_request("persons")
    print(person)
    with open('template/person.html', 'r') as f:
        contents = f.read()

    template = jinja2.Template(contents)
    filled_template = template.render(person=person)

    with open('html/output.html', 'w') as f:
        f.write(filled_template)

