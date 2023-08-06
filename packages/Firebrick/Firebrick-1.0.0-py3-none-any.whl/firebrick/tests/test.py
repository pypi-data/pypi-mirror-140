from django.urls import resolve, reverse


class ResolveUrlTest:
    def test_url_is_resolved(self):
        if '/' not in self.name:
            url = reverse(self.name)
        else:
            url = self.name
        
        if '__func__' in dir(self.view):
            self.assertEquals(resolve(url).func, self.view.__func__)
        else:
            self.assertEquals(resolve(url).func.view_class, self.view)


class GetViewTest:
    def test_GET(self):
        if '/' not in self.name:
            url = reverse(self.name)
        else:
            url = self.name
        response = self.client.get(url)
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)