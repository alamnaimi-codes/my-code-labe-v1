import sqlite3
import unittest

from app import app, get_db, init_db


class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DATABASE'] = 'test_database.db'

        conn = sqlite3.connect(app.config['DATABASE'])
        conn.execute('DROP TABLE IF EXISTS questions')
        conn.execute('DROP TABLE IF EXISTS notes')
        conn.execute('DROP TABLE IF EXISTS code_files')
        conn.close()

        init_db()
        self.client = app.test_client()

    def tearDown(self):
        conn = sqlite3.connect(app.config['DATABASE'])
        conn.execute('DROP TABLE IF EXISTS questions')
        conn.execute('DROP TABLE IF EXISTS notes')
        conn.execute('DROP TABLE IF EXISTS code_files')
        conn.close()

    def test_update_question_route(self):
        self.client.post('/add-question', data={
            'title': 'Old title',
            'question': 'Old question',
            'language': 'Python'
        })

        conn = get_db()
        row = conn.execute('SELECT * FROM questions').fetchone()
        conn.close()

        response = self.client.post(f'/update-question/{row["id"]}', data={
            'title': 'New title',
            'question': 'New question',
            'language': 'Java'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'New title', response.data)
        self.assertIn(b'New question', response.data)

    def test_update_code_route(self):
        self.client.post('/save-code', data={
            'filename': 'sample.py',
            'language': 'Python',
            'code': 'print("hello")'
        })

        conn = get_db()
        row = conn.execute('SELECT * FROM code_files').fetchone()
        conn.close()

        response = self.client.post(f'/update-code/{row["id"]}', data={
            'filename': 'updated.py',
            'language': 'Python',
            'code': 'print("updated")'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'updated.py', response.data)

        conn = get_db()
        updated = conn.execute('SELECT * FROM code_files WHERE id = ?', (row['id'],)).fetchone()
        conn.close()

        self.assertEqual(updated['filename'], 'updated.py')
        self.assertEqual(updated['code'], 'print("updated")')


if __name__ == '__main__':
    unittest.main()
