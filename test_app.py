import importlib
import os
import unittest


class AppFallbackConfigTest(unittest.TestCase):

    def test_sqlite_fallback_when_mysql_password_missing(self):
        if 'MYSQL_PASSWORD' in os.environ:
            del os.environ['MYSQL_PASSWORD']

        import app
        app_module = importlib.reload(app)

        db_uri = app_module.app.config['SQLALCHEMY_DATABASE_URI']

        self.assertTrue(
            db_uri.startswith('sqlite:///'),
            db_uri
        )


class AdminLoginRedirectTest(unittest.TestCase):

    def test_admin_login_redirects_to_admin_dashboard(self):
        if 'MYSQL_PASSWORD' in os.environ:
            del os.environ['MYSQL_PASSWORD']

        import app as app_module
        app_module = importlib.reload(app_module)

        with app_module.app.app_context():
            app_module.db.create_all()
            user = app_module.User.query.filter_by(email='admin@placement.local').first()
            if user is None:
                user = app_module.User(
                    name='Admin User',
                    email='admin@placement.local',
                    password='admin123',
                    role='admin'
                )
                app_module.db.session.add(user)
                app_module.db.session.commit()

        client = app_module.app.test_client()
        response = client.post(
            '/login',
            data={'email': 'admin@placement.local', 'password': 'admin123'},
            follow_redirects=False
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/dashboard', response.location)


if __name__ == '__main__':
    unittest.main()