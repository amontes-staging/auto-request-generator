import requests
import time
import datetime
import os
import uuid

from request_generator import request_generator
from request_generator import request_builder

class PrivateApiGetUsername:
    def __init__(self, logger, config, name):
        self.logger = logger
        self.config = config
        self.name = name

    def init_test(self):
        ready = self.config.get('endpoint').replace('/graphql', '/ready')
        self.logger.debug(ready)
        while True:
            try:
                self.logger.info('Trying Private GraphQL API...')
                r = requests.get(ready, timeout=5)
                if r.status_code == 200:
                    self.logger.info('Got 200 from ready endpoint')
                    break
            except Exception:
                self.logger.error('Private API isnt ready yet')
                time.sleep(1)

        endpoint = self.config.get('endpoint')
        self.data = {
          "query":"query {\n  getUserDataByVoiceId(voice_id:\"anthonystark\") { username }\n}\n"
        }
        self.rps = int(self.config['rps'])
        self.duration = int(self.config['duration'])
        self.threads = int(self.config['threads'])
        self.req = request_builder.RequestBuilder(
                endpoint,
                params={},
                data=self.data,
                cookiejarfile=None,
                auth=None,
                method='POST',
                user_agent='reqgen',
                auth_type='basic',
                headers={
                  'Content-Type': 'application/json'
                },
                files=[], # this will get filled by the workers
                insecure=False,
                nokeepalive=False,
                http2=False
            )
        self.args = {
            'req': self.req,
            'query': self.data
        }

    def run_test(self, output_file):
        self.logger.debug('starting test')
        reqgen = request_generator.RequestGenerator(self.rps, self.duration, self.threads, private_api_get_username, self.args, name=self.name)
        num_requests = reqgen.run(output_file=output_file)
        self.logger.debug('finished test')
        self.logger.info(f'Sent {num_requests} requests')

def private_api_get_username(args):

    start = time.perf_counter()
    timestamp = datetime.datetime.now()
    req = args['req']
    sess = requests.session()
    resp = sess.request(
        req.method,
        req.url,
        params=req.params,
        json=req.data,
        headers=req.headers,
        files=None,
        auth=req.auth,
        cookies=req.cookies,
        verify=req.verify
    )
    resp.raise_for_status()
    elapsed = time.perf_counter() - start

    return request_generator.Result(req.url, resp.status_code, len(resp.content), timestamp=timestamp, elapsed_time=elapsed)
