import unittest
from .. import Reply

class TestReply(unittest.TestCase):


    def assertHtmlEqual(self, expected, actual):
        def _strip(string):
            return string.replace(' ', '').replace('\n', '')
        return self.assertEqual(_strip(expected), _strip(actual))

    def test_can_convert_into_html(self):
        message = 'a simple <i>message</i>'
        reply = Reply(message)
        self.assertHtmlEqual(message, reply.to_html())

    def test_can_convert_link_into_html(self):
        message = 'a simple <i>message</i>'
        reply = Reply({'message': message, 'link': 'http://google.com'})
        self.assertHtmlEqual(('a simple <i>message</i>'
                        '<br>'
                        '<a href="http://google.com">http://google.com</a>'),
                        reply.to_html())

    def test_can_convert_list_into_html(self):
        message = 'a simple <i>message</i>'
        reply = Reply({'message': message, 'list': ['a', 'b', 1]})
        self.assertHtmlEqual(message
                            + '<br><ul><li>a</li><li>b</li><li>1</li></ul>',
                        reply.to_html())

    def test_can_convert_dict_into_html(self):
        message = 'a simple <i>message</i>'
        values = {
            '1': 'valueA',
            '2': 'valueB',
            '3': 'valueC'
        }
        reply = Reply({'message': message, 'dict': values})
        expected = message + '<br>'
        expected += """ <table>
                            <tbody>
                                <tr>
                                    <td>1</td>
                                    <td>valueA</td>
                                </tr>
                                <tr>
                                    <td>2</td>
                                    <td>valueB</td>
                                </tr>
                                <tr>
                                    <td>3</td>
                                    <td>valueC</td>
                                </tr>
                            </tbody>
                        </table>"""
        self.assertHtmlEqual(expected, reply.to_html())

    def test_can_convert_table_into_html(self):
        message = 'a simple <i>message</i>'
        values = {
            'id': [1, 2, 3],
            'val': [42, 356, 98],
            'prop': ['a', 'b', 'c']
        }
        reply = Reply({'message': message, 'table': values})
        expected = message + '<br>'
        expected += """ <table>
                            <thead>
                                <th>id</th>
                                <th>val</th>
                                <th>prop</th>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>1</td>
                                    <td>42</td>
                                    <td>a</td>
                                </tr>
                                <tr>
                                    <td>2</td>
                                    <td>356</td>
                                    <td>b</td>
                                </tr>
                                <tr>
                                    <td>3</td>
                                    <td>98</td>
                                    <td>c</td>
                                </tr>
                            </tbody>
                        </table>"""
        self.assertHtmlEqual(expected, reply.to_html())
