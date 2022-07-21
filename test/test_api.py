from unittest import TestCase

from guideapi.api import API


class TestGuideRouteApi(TestCase):

    def setUp(self):
        self.api = API()

    def test_route_default_decorater(self):

        @self.api.route('/home')
        def home(req, resp):
            return 'home'

        self.assertIn('get', self.api.routes['/home'])
        self.assertNotIn('post', self.api.routes['/home'])
        self.assertEqual(len(self.api.routes), 1)

    def test_route_get_decorater(self):

        @self.api.route('/home', methods='get')
        def home(req, resp):
            return 'home'

        self.assertIn('get', self.api.routes['/home'])
        self.assertNotIn('post', self.api.routes['/home'])
        self.assertEqual(len(self.api.routes), 1)
        self.assertEqual(len(self.api.routes['/home']), 1)

    def test_route_post_decorater(self):

        @self.api.route('/home', methods='post')
        def home(req, resp):
            return 'home'

        self.assertIn('post', self.api.routes['/home'])
        self.assertNotIn('get', self.api.routes['/home'])
        self.assertEqual(len(self.api.routes), 1)
        self.assertEqual(len(self.api.routes['/home']), 1)

    def test_route_get_post_decorater(self):

        @self.api.route('/home', methods=['get', 'post'])
        def home(req, resp):
            return 'home'

        self.assertIn('get', self.api.routes['/home'])
        self.assertIn('post', self.api.routes['/home'])
        self.assertNotIn('put', self.api.routes['/home'])
        self.assertEqual(len(self.api.routes), 1)
        self.assertEqual(len(self.api.routes['/home']), 2)

    def test_route_get_post_upper_decorater(self):

        @self.api.route('/home', methods=['GET', 'POST'])
        def home(req, resp):
            return 'home'

        self.assertIn('get', self.api.routes['/home'])
        self.assertIn('post', self.api.routes['/home'])
        self.assertNotIn('put', self.api.routes['/home'])
        self.assertEqual(len(self.api.routes), 1)
        self.assertEqual(len(self.api.routes['/home']), 2)

    def test_route_class_decorater(self):

        @self.api.route('/home')
        class Home(object):
            def get(self, req, resp):
                return 'home'

            def post(self, req, resp):
                return 'home'

        self.assertIn('/home', self.api.routes)
        self.assertIsInstance(self.api.routes['/home'], object)


class TestGUideAddRoute(TestCase):

    def setUp(self):
        self.api = API()

    def test_default_add(self):

        def home(req, resp):
            return 'home'

        self.api.add_route('/home', home)

        self.assertIn('get', self.api.routes['/home'])
        self.assertNotIn('post', self.api.routes['/home'])
        self.assertEqual(len(self.api.routes), 1)

    def test_get(self):

        def home(req, resp):
            return 'home'

        self.api.add_route('/home', home, methods='get')

        self.assertIn('get', self.api.routes['/home'])
        self.assertNotIn('post', self.api.routes['/home'])
        self.assertEqual(len(self.api.routes), 1)
        self.assertEqual(len(self.api.routes['/home']), 1)

    def test_post_add(self):

        def home(req, resp):
            return 'home'

        self.api.add_route('/home', home, methods='post')

        self.assertIn('post', self.api.routes['/home'])
        self.assertNotIn('get', self.api.routes['/home'])
        self.assertEqual(len(self.api.routes), 1)
        self.assertEqual(len(self.api.routes['/home']), 1)

    def test_list_add(self):

        def home(req, resp):
            return 'home'

        self.api.add_route('/home', home, methods=['get', 'post'])

        self.assertIn('get', self.api.routes['/home'])
        self.assertIn('post', self.api.routes['/home'])
        self.assertNotIn('put', self.api.routes['/home'])
        self.assertEqual(len(self.api.routes), 1)
        self.assertEqual(len(self.api.routes['/home']), 2)

    def test_list_add_upper(self):

        def home(req, resp):
            return 'home'

        self.api.add_route('/home', home, methods=['GET', 'POST'])

        self.assertIn('get', self.api.routes['/home'])
        self.assertIn('post', self.api.routes['/home'])
        self.assertNotIn('put', self.api.routes['/home'])
        self.assertEqual(len(self.api.routes), 1)
        self.assertEqual(len(self.api.routes['/home']), 2)

    def test_class_add(self):

        class Home(object):
            def get(self, req, resp):
                return 'home'

            def post(self, req, resp):
                return 'home'

        self.api.add_route('/home', Home)

        self.assertIn('/home', self.api.routes)
        self.assertIsInstance(self.api.routes['/home'], object)


class TestGuideFindHandler(TestCase):

    def setUp(self):
        self.api = API()

    def test_find_handler(self):

        @self.api.route('/home', methods=['get', 'post'])
        def home(req, resp):
            return 'home'

        handler, path = self.api.find_handler('/home', 'get')

        self.assertEqual(handler, home)
        self.assertEqual(path, {})

        handler, path = self.api.find_handler('/home', 'post')

        self.assertEqual(handler, home)
        self.assertEqual(path, {})
