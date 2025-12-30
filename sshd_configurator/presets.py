#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Готовые пресеты настроек для SSH
"""

PRESETS = {
    'hardened': {
        'name': 'Усиленная безопасность',
        'description': 'Максимальная безопасность для публичных серверов\n'
                      '• Нестандартный порт\n'
                      '• Отключен root доступ\n'
                      '• Только ключи, без паролей\n'
                      '• Ограниченные попытки входа',
        'settings': {
            'Port': '2222',
            'PermitRootLogin': 'no',
            'PasswordAuthentication': 'no',
            'PubkeyAuthentication': 'yes',
            'X11Forwarding': 'no',
            'MaxAuthTries': '3',
            'ClientAliveInterval': '300',
            'LoginGraceTime': '30',
            'Protocol': '2',
            'IgnoreRhosts': 'yes',
            'HostbasedAuthentication': 'no',
            'PermitEmptyPasswords': 'no'
        }
    },
    
    'developer': {
        'name': 'Режим разработчика',
        'description': 'Удобные настройки для локальной разработки\n'
                      '• Стандартный порт\n'
                      '• Разрешен root\n'
                      '• Включен X11 forwarding\n'
                      '• Долгий таймаут',
        'settings': {
            'Port': '22',
            'PermitRootLogin': 'yes',
            'PasswordAuthentication': 'yes',
            'PubkeyAuthentication': 'yes',
            'X11Forwarding': 'yes',
            'MaxAuthTries': '6',
            'ClientAliveInterval': '0',
            'LoginGraceTime': '120',
            'AllowTcpForwarding': 'yes'
        }
    },
    
    'default': {
        'name': 'Настройки по умолчанию',
        'description': 'Стандартные настройки Ubuntu/Debian\n'
                      '• Безопасный доступ root\n'
                      '• Пароли и ключи\n'
                      '• Стандартные таймауты',
        'settings': {
            'Port': '22',
            'PermitRootLogin': 'prohibit-password',
            'PasswordAuthentication': 'yes',
            'PubkeyAuthentication': 'yes',
            'X11Forwarding': 'yes',
            'MaxAuthTries': '6',
            'ClientAliveInterval': '0',
            'LoginGraceTime': '120'
        }
    },
    
    'minimal': {
        'name': 'Минимальная конфигурация',
        'description': 'Только самые необходимые настройки\n'
                      '• Минимальный набор опций\n'
                      '• Безопасный доступ root\n'
                      '• Только ключи',
        'settings': {
            'Port': '22',
            'PermitRootLogin': 'prohibit-password',
            'PasswordAuthentication': 'no',
            'PubkeyAuthentication': 'yes'
        }
    }
}

def get_preset(name):
    """
    Получение пресета по имени
    
    Args:
        name: Имя пресета
        
    Returns:
        dict: Настройки пресета или пустой словарь
    """
    preset = PRESETS.get(name, {})
    return preset.get('settings', {})

def get_preset_info(name):
    """
    Получение информации о пресете
    
    Args:
        name: Имя пресета
        
    Returns:
        dict: Информация о пресете
    """
    return PRESETS.get(name, {'name': 'Неизвестный', 'description': '', 'settings': {}})

def list_presets():
    """
    Получение списка доступных пресетов
    
    Returns:
        list: Список имен пресетов
    """
    return list(PRESETS.keys())

def format_preset_settings(settings):
    """
    Форматирование настроек для отображения
    
    Args:
        settings: Словарь настроек
        
    Returns:
        str: Отформатированная строка
    """
    if not settings:
        return "Нет настроек"
    
    lines = []
    for key, value in sorted(settings.items()):
        lines.append(f"{key:25} {value}")
    
    return "\n".join(lines)

# Тестирование
if __name__ == "__main__":
    print("Доступные пресеты:")
    print("-" * 40)
    
    for preset_name in list_presets():
        info = get_preset_info(preset_name)
        print(f"\n{info['name']} ({preset_name}):")
        print(f"Описание: {info['description']}")
        print("Настройки:")
        print(format_preset_settings(info['settings']))
        print("-" * 40)