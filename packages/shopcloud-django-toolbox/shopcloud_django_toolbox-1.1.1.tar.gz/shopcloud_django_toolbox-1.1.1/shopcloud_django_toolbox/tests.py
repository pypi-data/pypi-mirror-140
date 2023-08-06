import random
import string

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


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


class BaseTestApiAuthorization(TestCase):
    app_name = "test"

    username = "test.user"
    password = "test@123456789"

    admin_username = "test.admin"
    admin_password = "admin@123456789"

    def setUp(self) -> None:
        super().setUp()
        user, created = User.objects.get_or_create(username=self.username, password=self.password)
        admin_user = User.objects.create_superuser(
            username=self.admin_username,
            password=self.admin_password,
        )
        user.save()

    def _test_no_login(self, endpoint: str):
        client = APIClient()
        r = client.get(endpoint)
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def _test_user_no_model_permission(self, endpoint: str):
        client = APIClient()
        client.login(username=self.username, password=self.password)
        r = client.get(endpoint)
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def _test_superuser_access(self, endpoint: str):
        client = APIClient()
        client.login(username=self.admin_username, password=self.admin_password)
        r = client.get(endpoint)
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def run_test_endpoint(self, model_name: str):
        endpoint = f"/{self.app_name}/api/{model_name}/"
        self._test_no_login(endpoint=endpoint)
        self._test_user_no_model_permission(endpoint=endpoint)
        self._test_superuser_access(endpoint=endpoint)


class BaseTestAPIEndpointDoc(TestCase):
    def setUp(self) -> None:
        try:
            self.user = User.objects.create_superuser(
                username='admin',
                email='admin@talk-point.de',
                password='@12345678',
            )
        except:
            pass

    def test_doc(self):
        client = APIClient()

        r = client.get('/docs/')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

        client.force_authenticate(self.user)
        r = client.get('/docs/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
