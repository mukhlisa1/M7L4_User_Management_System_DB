import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users

@pytest.fixture(scope="module")
def setup_database():
    """Фикстура для настройки базы данных перед тестами и её очистки после."""
    create_db()
    yield
    try:
        os.remove('users.db')
    except PermissionError:
        pass

@pytest.fixture
def connection():
    """Фикстура для получения соединения с базой данных и его закрытия после теста."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()


def test_create_db(setup_database, connection):
    """Тест создания базы данных и таблицы пользователей."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "Таблица 'users' должна существовать в базе данных."

def test_add_new_user(setup_database, connection):
    """Тест добавления нового пользователя."""
    add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user, "Пользователь должен быть добавлен в базу данных."

def test_add_existing_user(setup_database, connection):
    """нельзя добавить пользователя с уже существующим логином."""
    add_user('user1', 'user1@example.com', 'pass1')
    result = add_user('user1', 'another@example.com', 'pass2')
    assert result is False, "Нельзя добавить одинаковых пользователей."


def test_user_success(setup_database):
    """успешная аутентификация пользователя."""
    add_user('loginuser', 'login@example.com', 'mypassword')
    result = authenticate_user('loginuser', 'mypassword')
    assert result is True, "Пользователь должен войти с правильным паролем."


def test_user_not_found(setup_database):
    """попытка входа несуществующего пользователя."""
    result = authenticate_user('nouser', 'nopass')
    assert result is False, "Несуществующий пользователь не должен войти."


def test_wrong_password(setup_database):
    """неправильный пароль."""
    add_user('realuser', 'real@example.com', 'rightpass')
    result = authenticate_user('realuser', 'wrongpass')
    assert result is False, "Пользователь не должен войти с неправильным паролем."