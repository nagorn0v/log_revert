import os
import unittest
from app import app, db
from config import basedir
from models import Task, List


class APITestCase(unittest.TestCase):
    list_id = None
    task_id = None
    list = {"name": "test name", "color": "black"}
    task = {"title": "test title", "description": "test description", "due_date": "2022-01-01T14:30:00",
            "list_id": list_id}
    headers = {'x-user-id': 0}

    @classmethod
    def tearDownClass(cls):
        list = List.query.get(APITestCase.list_id)
        task = Task.query.get(APITestCase.task_id)
        if list:
            db.session.delete(list)
        if task:
            db.session.delete(task)
        db.session.commit()
        os.remove(os.path.join(basedir, 'logs/0.log'))

    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()

    def tearDown(self):
        self.ctx.pop()

    def test_not_found_user_id(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 403)

    def test_invalid_user_id(self):
        response = self.client.get('/', headers={'x-user-id': 2})
        self.assertEqual(response.status_code, 401)

    # List tests
    def test_list_create(self):
        response = self.client.post('/lists', json=self.__class__.list, headers=self.__class__.headers)
        self.assertEqual(response.status_code, 201)
        self.__class__.list_id = response.get_json().get('id')

    def test_list_create_invalid(self):
        response = self.client.post('/lists', json={'test': "test", 'color': 'red'}, headers=self.__class__.headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['message'], 'name field not found')

    def test_lists_read(self):
        response = self.client.get('/lists', headers=self.__class__.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    def test_list_read(self):
        response = self.client.get(f'/lists/{self.__class__.list_id}', headers=self.__class__.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), self.__class__.list | response.get_json())

    def test_list_read_invalid(self):
        response = self.client.get('/lists/0', headers=self.__class__.headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()['message'], 'List with id 0 not found')

    def test_list_patch(self):
        response = self.client.patch(f'/lists/{self.__class__.list_id}', json={"color": "white"},
                                     headers=self.__class__.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('white', response.get_json()['color'])

    # Task tests
    def test_task_create(self):
        response = self.client.post('/tasks', json=self.__class__.task, headers=self.__class__.headers)
        self.assertEqual(response.status_code, 201)
        self.__class__.task_id = response.get_json().get('id')

    def test_task_create_invalid(self):
        response = self.client.post('/tasks', json={'test': "test"}, headers=self.__class__.headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['message'], 'title field not found')

    def test_tasks_read(self):
        response = self.client.get('/tasks', headers=self.__class__.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    def test_task_read(self):
        response = self.client.get(f'/tasks/{self.__class__.task_id}', headers=self.__class__.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), self.__class__.task | response.get_json())

    def test_task_read_invalid(self):
        response = self.client.get('/tasks/0', headers=self.__class__.headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()['message'], 'Task with id 0 not found')

    def test_task_patch(self):
        response = self.client.patch(f'/tasks/{self.__class__.task_id}', json={"due_date": "2022-02-02T14:30:00"},
                                     headers=self.__class__.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('2022-02-02T14:30:00', response.get_json()['due_date'])

    def test_task_patch_invalid(self):
        response = self.client.patch(f'/tasks/{self.__class__.task_id}', json={"due_date": "234243324234"},
                                     headers=self.__class__.headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['message'], 'Invalid datetime format')


if __name__ == '__main__':
    unittest.main()
