#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os
import shutil
import tempfile
from pathlib import Path
import sys
import pwd
import grp
import json
from datetime import datetime

class SSHConfigError(Exception):
    """Кастомное исключение для ошибок конфигурации SSH"""
    pass

class SSHConfigManager:
    def __init__(self, config_path="/etc/ssh/sshd_config", test_mode=False):
        """
        Инициализация менеджера конфигурации SSH
        
        Args:
            config_path: Путь к файлу конфигурации sshd
            test_mode: Режим тестирования (не вносит реальных изменений)
        """
        self.config_path = Path(config_path)
        self.backup_dir = Path("/var/backup/sshd_configurator")
        self.test_mode = test_mode
        
        if not test_mode:
            self._ensure_privileges()
            self._ensure_backup_dir()
    
    def _ensure_privileges(self):
        """Проверка прав суперпользователя"""
        if os.geteuid() != 0:
            raise SSHConfigError("Требуются права суперпользователя!")
    
    def _ensure_backup_dir(self):
        """Создание директории для бэкапов"""
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            # Устанавливаем правильные права
            os.chmod(self.backup_dir, 0o700)
        except PermissionError:
            raise SSHConfigError(f"Нет прав для создания {self.backup_dir}")
    
    def read_current_config(self):
        """
        Чтение текущей конфигурации sshd
        
        Returns:
            dict: Словарь с текущими настройками
        """
        if not self.config_path.exists():
            raise SSHConfigError(f"Файл {self.config_path} не найден!")
        
        directives = {}
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # Пропускаем пустые строки и комментарии
                    if not line or line.startswith('#'):
                        continue
                    
                    # Обработка директив
                    parts = line.split(None, 1)
                    if len(parts) == 2:
                        key, value = parts
                        directives[key] = value
        
        except Exception as e:
            raise SSHConfigError(f"Ошибка чтения конфигурации: {e}")
        
        return directives
    
    def validate_setting(self, key, value):
        """Валидация значения настройки"""
        validators = {
            'Port': lambda v: v.isdigit() and 1 <= int(v) <= 65535,
            'PermitRootLogin': lambda v: v in ['yes', 'no', 'prohibit-password', 
                                               'without-password', 'forced-commands-only'],
            'PasswordAuthentication': lambda v: v in ['yes', 'no'],
            'PubkeyAuthentication': lambda v: v in ['yes', 'no'],
            'X11Forwarding': lambda v: v in ['yes', 'no'],
            'ClientAliveInterval': lambda v: v.isdigit() and int(v) >= 0,
            'MaxAuthTries': lambda v: v.isdigit() and int(v) > 0,
            'LoginGraceTime': lambda v: v.isdigit() and int(v) >= 0,
        }
        
        if key in validators:
            if not validators[key](value):
                raise ValueError(f"Некорректное значение для {key}: {value}")
        
        # Специальная валидация для AllowUsers/AllowGroups
        if key in ['AllowUsers', 'AllowGroups']:
            for item in value.split():
                if key == 'AllowUsers':
                    try:
                        pwd.getpwnam(item)
                    except KeyError:
                        raise ValueError(f"Пользователь {item} не существует")
                else:  # AllowGroups
                    try:
                        grp.getgrnam(item)
                    except KeyError:
                        raise ValueError(f"Группа {item} не существует")
        
        return True
    
    def create_backup(self, comment=""):
        """
        Создание резервной копии конфигурации
        
        Args:
            comment: Комментарий к бэкапу
            
        Returns:
            str: Путь к созданному бэкапу
        """
        if self.test_mode:
            print(f"[TEST] Создание бэкапа с комментарием: {comment}")
            return "/tmp/test_backup"
        
        try:
            # Создаем имя файла с timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_comment = comment.replace(' ', '_').replace('/', '_')[:50]
            backup_name = f"sshd_config_{timestamp}_{safe_comment}" if comment else f"sshd_config_{timestamp}"
            backup_path = self.backup_dir / backup_name
            
            # Копируем файл
            shutil.copy2(self.config_path, backup_path)
            
            # Создаем файл с метаинформацией
            meta = {
                'timestamp': timestamp,
                'original_path': str(self.config_path),
                'comment': comment,
                'user': os.getenv('SUDO_USER', 'root')
            }
            
            with open(f"{backup_path}.meta", 'w') as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)
            
            print(f"Создан бэкап: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            raise SSHConfigError(f"Ошибка создания бэкапа: {e}")
    
    def apply_settings(self, settings, create_backup=True, backup_comment=""):
        """
        Применение новых настроек
        
        Args:
            settings: dict с настройками {ключ: значение}
            create_backup: Создавать ли бэкап перед изменением
            backup_comment: Комментарий для бэкапа
            
        Returns:
            dict: Результат операции
        """
        if self.test_mode:
            print(f"[TEST] Применение настроек: {settings}")
            return {'status': 'test', 'applied': settings}
        
        try:
            # Валидация всех настроек
            for key, value in settings.items():
                self.validate_setting(key, value)
            
            # Создание бэкапа
            backup_path = None
            if create_backup:
                backup_path = self.create_backup(backup_comment)
            
            # Читаем текущий конфиг
            with open(self.config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            updated_lines = []
            updated_keys = set()
            
            # Обновляем существующие директивы
            for line in lines:
                stripped = line.strip()
                
                if not stripped or stripped.startswith('#'):
                    updated_lines.append(line)
                    continue
                
                key = stripped.split()[0]
                if key in settings:
                    # Обновляем директиву
                    indent = line[:len(line) - len(line.lstrip())]
                    updated_lines.append(f"{indent}{key} {settings[key]}\n")
                    updated_keys.add(key)
                else:
                    updated_lines.append(line)
            
            # Добавляем новые директивы в конец
            for key, value in settings.items():
                if key not in updated_keys:
                    updated_lines.append(f"\n# Добавлено через SSH Configurator\n{key} {value}\n")
            
            # Записываем во временный файл
            temp_fd, temp_path = tempfile.mkstemp()
            try:
                with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                    f.writelines(updated_lines)
                
                # Проверяем синтаксис
                if not self._test_config_syntax(temp_path):
                    raise SSHConfigError("Ошибка синтаксиса в новой конфигурации")
                
                # Копируем на место
                shutil.copy2(temp_path, self.config_path)
                
                # Устанавливаем правильные права
                os.chmod(self.config_path, 0o600)
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            
            return {
                'status': 'success',
                'backup': backup_path,
                'applied_settings': settings
            }
            
        except Exception as e:
            raise SSHConfigError(f"Ошибка применения настроек: {e}")
    
    def _test_config_syntax(self, config_path):
        """Проверка синтаксиса конфигурации"""
        try:
            result = subprocess.run(
                ['sshd', '-t', '-f', config_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                print(f"Ошибка синтаксиса: {result.stderr}")
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print("Таймаут проверки синтаксиса")
            return False
        except FileNotFoundError:
            print("Команда sshd не найдена")
            return False
        except Exception as e:
            print(f"Ошибка при проверке синтаксиса: {e}")
            return False
    
    def restart_service(self):
        """Перезапуск службы sshd"""
        if self.test_mode:
            print("[TEST] Перезапуск службы sshd")
            return {'status': 'test', 'restarted': True}
        
        try:
            result = subprocess.run(
                ['systemctl', 'restart', 'ssh'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # Пробуем альтернативное имя службы
                result = subprocess.run(
                    ['systemctl', 'restart', 'sshd'],
                    capture_output=True,
                    text=True
                )
            
            if result.returncode == 0:
                return {'status': 'success', 'message': 'Служба перезапущена'}
            else:
                return {'status': 'error', 'message': result.stderr}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_service_status(self):
        """Получение статуса службы sshd"""
        if self.test_mode:
            return "active (test mode)"
        
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', 'ssh'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                result = subprocess.run(
                    ['systemctl', 'is-active', 'sshd'],
                    capture_output=True,
                    text=True
                )
            
            return result.stdout.strip() if result.returncode == 0 else "unknown"
            
        except Exception:
            return "unknown"
    
    def list_backups(self):
        """Получение списка бэкапов"""
        if self.test_mode:
            return []
        
        backups = []
        try:
            for file in self.backup_dir.glob("sshd_config_*"):
                if file.suffix != '.meta':
                    meta_file = file.with_suffix(file.suffix + '.meta')
                    meta = {}
                    
                    if meta_file.exists():
                        try:
                            with open(meta_file, 'r') as f:
                                meta = json.load(f)
                        except:
                            pass
                    
                    file_stat = file.stat()
                    backups.append({
                        'path': str(file),
                        'name': file.name,
                        'size': file_stat.st_size,
                        'modified': datetime.fromtimestamp(file_stat.st_mtime),
                        'meta': meta
                    })
        except Exception as e:
            print(f"Ошибка при чтении бэкапов: {e}")
        
        return sorted(backups, key=lambda x: x['modified'], reverse=True)
    
    def restore_backup(self, backup_path):
        """Восстановление конфигурации из бэкапа"""
        if self.test_mode:
            print(f"[TEST] Восстановление из {backup_path}")
            return {'status': 'test', 'restored': True}
        
        try:
            backup_path = Path(backup_path)
            if not backup_path.exists():
                raise SSHConfigError(f"Бэкап {backup_path} не найден")
            
            # Создаем бэкап текущей конфигурации
            current_backup = self.create_backup("before_restore")
            
            # Копируем бэкап
            shutil.copy2(backup_path, self.config_path)
            
            return {
                'status': 'success',
                'restored_from': str(backup_path),
                'current_backup': current_backup
            }
            
        except Exception as e:
            raise SSHConfigError(f"Ошибка восстановления: {e}")

# Тестирование класса
if __name__ == "__main__":
    print("Тестирование SSHConfigManager...")
    
    # Создаем менеджер в тестовом режиме
    manager = SSHConfigManager(test_mode=True)
    
    # Тест чтения конфигурации
    try:
        config = manager.read_current_config()
        print(f"Текущий порт: {config.get('Port', 'не указан')}")
        print(f"Root доступ: {config.get('PermitRootLogin', 'не указан')}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    # Тест валидации
    print("\nТест валидации:")
    test_settings = {
        'Port': '2222',
        'PermitRootLogin': 'no',
        'PasswordAuthentication': 'yes'
    }
    
    for key, value in test_settings.items():
        try:
            manager.validate_setting(key, value)
            print(f"✓ {key}={value} - OK")
        except ValueError as e:
            print(f"✗ {key}={value} - {e}")