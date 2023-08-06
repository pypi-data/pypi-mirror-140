from conftest import api

def test_basic_routes(api):
    @api.route("/home")
    def home(req,resp):
        resp.text = "YOLU"


