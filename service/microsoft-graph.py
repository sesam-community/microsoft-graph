import os
import requests
import json
from sesamutils.flask import serve
from sesamutils.sesamlogger import sesam_logger
from sesamutils.dotdictify import Dotdictify
from flask import Flask, request, Response

app = Flask(__name__)

logger = sesam_logger('microsoft-graph', app=app)


def get_token():
    auth_url = os.environ.get('token_url')
    logger.info(f"trying to obtain access token from {auth_url}")
    payload = json.loads((os.environ.get("token_payload")).replace("'", "\""))
    resp = requests.post(url=auth_url, data=payload)
    resp.raise_for_status()
    logger.info(f"fetched access token from {auth_url}")
    return resp


class DataAccess:

    @staticmethod
    def __get_all_paged_entities(path, access_token, args):
        """
        internal get function
        :param path:
        :param access_token: Oauth2 access token string
        :param args:
        :return:
        """
        logger.info(f"fetching data from paged url: {path}")

        since = args.get("since")
        if since is not None:
            ##TODO
            ##I do not think this works correctly with graph to sharepoint API. This needs to be fixed in the future.
            logger.info(f"fetching data from list: {path}, since {since}")
            url = os.environ.get(
                "base_url") + path + "?expand=fields&$OrderBy=lastModifiedDateTime&$filter=lastModifiedDateTime ge datetime'" + since + "'"
        else:
            logger.info(f"fetching data from list: {path}")
            url = os.environ.get("base_url") + path + "?expand=fields"

        response = requests.get(url, headers={'Authorization': 'Bearer ' + access_token})
        response.raise_for_status()

        response_data = response.json()
        next_page = response_data.get('@odata.nextLink')

        if not response_data.get('value'):
            raise ValueError(f'value object not found in response: {response_data}')

        while next_page is not None:
            for entity in Dotdictify(response_data).value:
                yield set_updated(entity, args)
            response = requests.get(next_page, headers={'Authorization': 'Bearer ' + access_token})
            response_data = response.json()
            next_page = response_data.get('@odata.nextLink')

        else:
            for entity in Dotdictify(response_data).value:
                yield set_updated(entity, args)

    def get_entities(self, path, access_token, args):
        """
        main get function, will probably run most via path:path
        :param path:
        :param access_token:
        :param args:
        :return:
        """
        return self.__get_all_paged_entities(path, access_token, args)


data_access_layer = DataAccess()


def set_updated(entity, args):
    since_path = args.get("since_path")

    if since_path is not None:
        b = Dotdictify(entity)
        entity["_updated"] = b.get(since_path)

    return entity


def stream_json(generator_func):
    first = True
    yield '['
    for i, row in enumerate(generator_func):
        if not first:
            yield ','
        else:
            first = False
        yield json.dumps(row)
    yield ']'
    logger.info(f"successfully processed {i+1} entities")


@app.route("/<path:path>", methods=["GET"])
def get(path):
    try:
        resp = get_token()
        resp.raise_for_status()

        access_token = Dotdictify(resp.json()).access_token
        entities_generator = data_access_layer.get_entities(path, access_token, args=request.args)

        return Response(stream_json(entities_generator), mimetype='application/json')
    except requests.exceptions.HTTPError as exc:
        logger.error(f'exception {exc} occurred, response returned: {resp.text}')
        return Response(resp.text, status=resp.status_code, mimetype='application/json')


if __name__ == '__main__':
    serve(app)
