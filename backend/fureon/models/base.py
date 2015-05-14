from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class ModelManager(object):
    def __init__(self, session):
        self._session = session

    def format_list_to_numbered_dict(self, input_list, start_count=0):
        numbered_dict = {}
        entry_count = start_count
        for entry in input_list:
            numbered_dict[unicode(entry_count)] = entry
            entry_count += 1
        return numbered_dict

    def format_query_rows_to_dict(self, query):
        if isinstance(query, list):
            return map(self._format_row_to_dict, query)
        else:
            return self._format_row_to_dict(query)

    def remove_columns_from_query_rows(self, column_names, query_rows):
        if isinstance(query_rows, list):
            for row in query_rows:
                self._remove_columns_from_row(column_names, row)
        else:
            for row_number, row_data in query_rows.iteritems():
                self._remove_columns_from_row(column_names, row_data)

    def _format_row_to_dict(self, row):
        dict = {}
        for column in row.__table__.columns:
            dict[column.name] = getattr(row, column.name)
        return dict

    def _remove_columns_from_row(self, column_names, row):
        for column_name in column_names:
            row.pop(column_name)
