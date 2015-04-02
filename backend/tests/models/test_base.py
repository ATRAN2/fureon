from fureon.models import base


class TestModelManager(object):
    @classmethod
    def setup_class(cls):
        cls._model_manager = base.ModelManager(None)

    def setup_method(self, method):
        self._test_list = [
                {1 : 1, 'y' : 'y', 'z' : 'z'},
                {2 : 2, 'y' : 'y', 'z' : 'z'},
                {3 : 3, 'y' : 'y', 'z' : 'z'},
                {4 : 4, 'y' : 'y', 'z' : 'z'}
        ]

    def test_format_list_to_numbered_dict(self):
        start_count = 2
        expected_result = {
            u'2' : self._test_list[0],
            u'3' : self._test_list[1],
            u'4' : self._test_list[2],
            u'5' : self._test_list[3]
        }
        result = self._model_manager \
            .format_list_to_numbered_dict(self._test_list, start_count)
        assert expected_result == result

    def test_remove_columns_from_query_rows_with_list(self):
        expected_result = [
            {1 : 1},
            {2 : 2},
            {3 : 3},
            {4 : 4}
        ]
        assert expected_result != self._test_list
        self._model_manager\
            .remove_columns_from_query_rows(['y', 'z'], self._test_list)
        assert expected_result == self._test_list

    def test_remove_columns_from_query_rows_with_dict(self):
        expected_result = {
            u'0' : {1 : 1},
            u'1' : {2 : 2},
            u'2' : {3 : 3},
            u'3' : {4 : 4}
        }
        test_list_as_dict = self._model_manager\
            .format_list_to_numbered_dict(self._test_list)
        assert expected_result != test_list_as_dict
        self._model_manager\
            .remove_columns_from_query_rows(['y', 'z'], test_list_as_dict)
        assert expected_result == test_list_as_dict


