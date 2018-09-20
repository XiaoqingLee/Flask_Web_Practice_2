import requests
from flask import current_app


def translate(text, source_language, target_language):

    url = current_app.config['TRANSLATION_SERVICE_API'].format(
        source_language,
        target_language,
        text
    )
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/69.0.3497.92 Safari/537.36'
    }
    r = requests.get(url=url, headers=headers)
    if r.status_code != 200:
        print(r.status_code)
        return 'Error: Fail to connect to translation service provider.'
    return r.json()[0][0][0]

