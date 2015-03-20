import tornado.web


class APIRootHandler(tornado.web.RequestHandler):
    def get(self):
        endpoints = { '/api/songs' : 'songs endpoint info goes here', }
        self.write(endpoints)

def convert_row_to_map(row):
    map = {}
    for column in row.__table__.columns:
        map[column.name] = getattr(row, column.name)
    return map
