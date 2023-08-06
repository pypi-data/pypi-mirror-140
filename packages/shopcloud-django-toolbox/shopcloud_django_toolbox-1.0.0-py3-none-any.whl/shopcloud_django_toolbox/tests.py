import random
import string

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class SetupClass(TestCase):
    username = 'admin'
    pwd = ':L:3M3pFK"N$Y!Qj'

    def create_superuser(self):
        u = User.objects.create_superuser(
            username=self.username,
            password=self.pwd
        )
        u.save()

    def setUp(self):
        self.create_superuser()


class TestAdminTestCase(SetupClass):
    MODULE = 'test'

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.client.login(username=TestAdminTestCase.username, password=TestAdminTestCase.pwd)

    def run_for_model(self, model: str, **kwargs):
        if kwargs.get('is_check_add', True):
            response = self.client.get(
                reverse('admin:{}_{}_add'.format(self.MODULE, model)),
                follow=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.template_name[0], 'admin/{}/{}/change_form.html'.format(self.MODULE, model))

        response = self.client.get(
            reverse('admin:{}_{}_changelist'.format(self.MODULE, model)),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        if kwargs.get('is_check_template', True):
            self.assertEqual(response.template_name[0], 'admin/{}/{}/change_list.html'.format(self.MODULE, model))

        if kwargs.get('is_check_search', False):
            response = self.client.get(
                "{}?q={}".format(
                    reverse('admin:{}_{}_changelist'.format(self.MODULE, model)),
                    "test"
                ),
                follow=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.template_name[0], 'admin/{}/{}/change_list.html'.format(self.MODULE, model))