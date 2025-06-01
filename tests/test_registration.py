import pytest
import sqlite3
from registration.registration import *
from io import StringIO
import sys
from unittest.mock import patch
import os
# Фикстуры
@pytest.fixture(scope="function")
def test_db():
    """Создаем временную БД для каждого теста"""
    DB_NAME = 'test_users.db'
    conn = sqlite3.connect(DB_NAME)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    yield DB_NAME
    conn.close()
    try:
        os.remove(DB_NAME)
    except:
        pass

# 1. Тесты для authenticate_user (4 строки)
def test_authenticate_user_success(test_db):
    """Тест успешной аутентификации"""
    with patch('registration.registration.DB_NAME', test_db):
        add_user('testuser', 'test@test.com', 'testpass')
        assert authenticate_user('testuser', 'testpass') is True

def test_authenticate_user_wrong_password(test_db):
    """Тест с неверным паролем"""
    with patch('registration.registration.DB_NAME', test_db):
        add_user('testuser', 'test@test.com', 'testpass')
        assert authenticate_user('testuser', 'wrongpass') is False

def test_authenticate_user_nonexistent(test_db):
    """Тест с несуществующим пользователем"""
    with patch('registration.registration.DB_NAME', test_db):
        assert authenticate_user('nonexistent', 'anypass') is False

def test_authenticate_user_db_error():
    """Тест ошибки БД"""
    with patch('sqlite3.connect', side_effect=sqlite3.Error):
        assert authenticate_user('test', 'pass') is False

# 2. Тесты для display_users (5 строк)
def test_display_users_with_data(test_db, capsys):
    """Тест отображения с данными"""
    with patch('registration.registration.DB_NAME', test_db):
        add_user('user1', 'user1@test.com', 'pass1')
        add_user('user2', 'user2@test.com', 'pass2')
        display_users()
        captured = capsys.readouterr()
        assert 'user1@test.com' in captured.out
        assert 'user2@test.com' in captured.out

def test_display_users_empty(test_db, capsys):
    """Тест отображения пустой БД"""
    with patch('registration.registration.DB_NAME', test_db):
        display_users()
        captured = capsys.readouterr()
        assert 'Логин:' not in captured.out

def test_display_users_db_error(capsys):
    """Тест ошибки БД при отображении"""
    with patch('sqlite3.connect', side_effect=sqlite3.Error):
        display_users()
        captured = capsys.readouterr()
        assert captured.out == ''

# 3. Тесты для user_choice (4 строки)
def test_user_choice_valid_1(monkeypatch):
    """Тест выбора 1"""
    monkeypatch.setattr('sys.stdin', StringIO('1\n'))
    assert user_choice() == '1'

def test_user_choice_valid_2(monkeypatch):
    """Тест выбора 2"""
    monkeypatch.setattr('sys.stdin', StringIO('2\n'))
    assert user_choice() == '2'

def test_user_choice_invalid_then_valid(monkeypatch, capsys):
    """Тест неверного ввода с последующим верным"""
    monkeypatch.setattr('sys.stdin', StringIO('3\n1\n'))
    assert user_choice() == '1'
    captured = capsys.readouterr()
    assert 'Неверный ввод' in captured.out

def test_user_choice_empty_input(monkeypatch):
    """Тест пустого ввода"""
    monkeypatch.setattr('sys.stdin', StringIO('\n1\n'))
    assert user_choice() == '1'

# 4. Тесты для main (15 строк)
def test_main_auth_success(test_db, monkeypatch, capsys):
    """Тест успешной авторизации через main"""
    with patch('registration.registration.DB_NAME', test_db):
        add_user('authuser', 'auth@test.com', 'authpass')
        inputs = ['1', 'authuser', 'authpass']
        monkeypatch.setattr('sys.stdin', StringIO('\n'.join(inputs)))
        main()
        captured = capsys.readouterr()
        assert 'Авторизация успешна' in captured.out

def test_main_auth_failure(test_db, monkeypatch, capsys):
    """Тест неудачной авторизации через main"""
    with patch('registration.registration.DB_NAME', test_db):
        inputs = ['1', 'wronguser', 'wrongpass']
        monkeypatch.setattr('sys.stdin', StringIO('\n'.join(inputs)))
        main()
        captured = capsys.readouterr()
        assert 'Неверный логин или пароль' in captured.out

def test_main_registration(test_db, monkeypatch, capsys):
    """Тест регистрации через main"""
    with patch('registration.registration.DB_NAME', test_db):
        inputs = ['2', 'newuser', 'new@test.com', 'newpass']
        monkeypatch.setattr('sys.stdin', StringIO('\n'.join(inputs)))
        main()
        captured = capsys.readouterr()
        assert 'newuser' in captured.out

def test_main_invalid_choice(test_db, monkeypatch, capsys):
    """Тест неверного выбора в main"""
    with patch('registration.registration.DB_NAME', test_db):
        inputs = ['3', '1', 'user', 'pass']
        monkeypatch.setattr('sys.stdin', StringIO('\n'.join(inputs)))
        main()
        captured = capsys.readouterr()
        assert 'Неверный ввод' in captured.out

def test_main_db_error(monkeypatch, capsys):
    """Тест ошибки БД в main"""
    with patch('sqlite3.connect', side_effect=sqlite3.Error):
        inputs = ['1', 'user', 'pass']
        monkeypatch.setattr('sys.stdin', StringIO('\n'.join(inputs)))
        main()
        captured = capsys.readouterr()
        assert 'Неверный логин или пароль' in captured.out