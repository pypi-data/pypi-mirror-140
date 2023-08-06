from flask import Flask, request, Response
from eth_tester import EthereumTester
from flask import make_response


def make_app():

    t = EthereumTester()
    app = Flask('Fake Eth server')

    @app.route('/', defaults={'path': ''}, methods=['get', 'post'])
    @app.route('/<path:path>', methods=['get', 'post'])
    #@app.route("/")
    def hello_world(path):
        print(f"Requested: {path}")
        req = request.json
        print(f"Request: {req}")

        if req['method'] == 'eth_call':
            params, block = req['params']
            if 'from' not in params:
                params['from'] = t.get_accounts()[0]
            res = t.call(params, block)
            print(f"Result: {res}")

        if req['method'] == 'eth_chainId':
            return make_response({
              "id": req['id'],
              "jsonrpc": "2.0",
              "result": "4"
            })

        return Response(status=500)

    return app


app = make_app()
app.run()
