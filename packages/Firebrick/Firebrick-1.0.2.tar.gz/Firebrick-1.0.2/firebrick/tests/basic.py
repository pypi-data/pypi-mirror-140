from firebrick.tests.test import ResolveUrlTest, GetViewTest


class BasicViewTest(ResolveUrlTest, GetViewTest):
    def setUp(self):
        self.client = Client()