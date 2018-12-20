from flask import Flask, request, Response

import os
import requests
import logging
import json
import dotdictify


app = Flask(__name__)
logger = None
format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger('microsoft-graph')

# Log to stdout
stdout_handler = logging.StreamHandler()
stdout_handler.setFormatter(logging.Formatter(format_string))
logger.addHandler(stdout_handler)
logger.setLevel(logging.DEBUG)


def get_token():
    logger.info("Creating header")
    payload = json.loads((os.environ.get("token_payload")).replace("'", "\""))
    resp = requests.post(url=os.environ.get("token_url"), data=payload)
    logger.info("fetching access token from " + os.environ.get('token_url'))
    return resp


class DataAccess:

#main get function, will probably run most via path:path
    def __get_all_paged_entities(self, path,access_token, args):
        logger.info("Fetching data from paged url: %s", path)

        since = args.get("since")
        if since is not None:
            ##TODO
            ##I do not think this works correctly with graph to sharepoint API. This needs to be fixed in the future.
            logger.info("Fetching data from list: %s, since %s", path, since)
            url = os.environ.get("base_url") + path + "?expand=fields&$OrderBy=lastModifiedDateTime&$filter=lastModifiedDateTime ge datetime'" + since + "'"
        else:
            logger.info("Fetching data from list: %s", path)
            url = os.environ.get("base_url") + path + "?expand=fields"

        req = requests.get(url,  headers={'Authorization': 'Bearer ' + access_token})
        if req.status_code == 200:
            next = json.loads(req.text).get('@odata.nextLink')

            while next is not None:
                for entity in dotdictify.dotdictify(json.loads(req.text)).value:
                    yield set_updated(entity, args)
                req = requests.get(next, headers={'Authorization': 'Bearer ' + access_token})
                next = json.loads(req.text).get('@odata.nextLink')

            else:
                for entity in dotdictify.dotdictify(json.loads(req.text)).value:
                    yield set_updated(entity, args)

        else:
            logger.error(json.dumps(req.json()))
            return req

    def get_entities(self, path, access_token, args):
        print("getting all paged")
        return self.__get_all_paged_entities(path, access_token, args)

data_access_layer = DataAccess()


def set_updated(entity, args):
    since_path = args.get("since_path")

    if since_path is not None:
        b = dotdictify.dotdictify(entity)
        entity["_updated"] = b.get(since_path)

    return entity


def stream_json(clean):
    first = True
    yield '['
    for i, row in enumerate(clean):
        if not first:
            yield ','
        else:
            first = False
        yield json.dumps(row)
    yield ']'


@app.route("/<path:path>", methods=["GET"])
def get(path):
    resp = get_token()
    if resp.status_code == 200:
        access_token = dotdictify.dotdictify(resp.json()).access_token

        entities = data_access_layer.get_entities(path, access_token, args=request.args)
        return Response(stream_json(entities),mimetype='application/json')
    else:
        logger.error(json.dumps(resp.json()))
        return Response(json.dumps(resp.json()), status=resp.status_code, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True, port=os.environ.get('port',5000))
