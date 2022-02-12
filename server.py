import cherrypy, main
import cherrypy_cors

conf = {
  'global' : {
    'server.socket_host' : '127.0.0.1',
    'server.socket_port' : 8080,
    'server.thread_pool' : 8,
    'tools.CORS.on': True, 
    'tools.response_headers.on': True,
    'tools.response_headers.headers': [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin')]
    }
}

def CORS():
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*" 
    cherrypy.response.headers["Access-Control-Allow-Headers"] = "*"
    cherrypy.response.headers["Access-Control-Allow-Methods"] = 'GET, POST, PUT'

class GroceryData(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return main.order_products_by_name(main.conn_naive)

class GroceryPricesData(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return main.get_prices(main.conn_naive)

if __name__ == '__main__':
    cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS)
    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 8080,
        'tools.CORS.on': True,
    })
    
    cherrypy.tree.mount(GroceryData(), '/')
    cherrypy.tree.mount(GroceryPricesData(), '/prices')
    cherrypy.engine.start()
    cherrypy.engine.block()
