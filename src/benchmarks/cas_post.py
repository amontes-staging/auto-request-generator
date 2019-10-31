import requests
import time
import os

from request_generator import request_generator
from request_generator import request_builder

class CASPost:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config

    def init_test(self):
        ready = self.config.get('endpoint').replace('files', 'ready')
        self.logger.debug(ready)
        while True:
            try:
                self.logger.info('Trying CAS...')
                r = requests.get(ready, timeout=5)
                if r.status_code == 200:
                    self.logger.info('Got 200 from ready endpoint')
                    break
            except Exception:
                self.logger.error('CAS isnt ready yet')
                time.sleep(1)

        endpoint = self.config.get('endpoint')

        self.rps = int(self.config['rps'])
        self.duration = int(self.config['duration'])
        file_path = '/assets/test.jpg'
        self.req = request_builder.RequestBuilder(
                endpoint,
                params={},
                data=None,
                cookiejarfile=f'/assets/cookies-{self.config["cluster"]}.txt',
                auth=None,
                method='POST',
                user_agent='reqgen',
                auth_type='basic',
                headers={},
                files=[f'filename:{file_path}'],
                insecure=False,
                nokeepalive=False,
                http2=False
            )
        self.args = {
            'req': self.req,
            'payload_size': self.config['payload_size'],
            'file_path': file_path
        }

    def run_test(self, output_file):
        self.logger.debug('starting test')
        reqgen = request_generator.RequestGenerator(self.rps, self.duration, cas_post, self.args)
        num_requests = reqgen.run(output_file=output_file)
        self.logger.debug('finished test')
        self.logger.info(f'Sent {num_requests} requests')

def cas_post(args):

    with open(args['file_path'], 'wb') as new_file:
        new_file.write(os.urandom(args['payload_size']))

    req = args['req']
    sess = requests.session()
    resp = sess.request(
        req.method,
        req.ipurl,
        params=req.params,
        data=req.data,
        headers=req.headers,
        files=req.files,
        auth=req.auth,
        cookies=req.cookies,
        verify=req.verify
    )
    resp.raise_for_status()

    return request_generator.Result(req.url, resp.status_code, len(resp.content))
