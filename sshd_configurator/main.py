#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SSH Daemon Configurator for Linux
Главный файл приложения
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Главная функция приложения"""
    print("=== SSH Daemon Configurator для Linux ===\n")
    
    # Проверяем, запущен ли с sudo
    if os.geteuid() != 0:
        print("ОШИБКА: Приложение требует прав суперпользователя!")
        print("Пожалуйста, запустите с помощью sudo:")
        print("    sudo python3 main.py")
        print("\nИли установите приложение и запустите через sudo:")
        print("    sudo ./sshd-configurator")
        sys.exit(1)
    
    # Проверяем наличие SSH
    if not os.path.exists("/etc/ssh/sshd_config"):
        print("ВНИМАНИЕ: Файл /etc/ssh/sshd_config не найден!")
        print("Установите openssh-server:")
        print("    sudo apt-get install openssh-server")
        answer = input("Продолжить? (y/N): ")
        if answer.lower() != 'y':
            sys.exit(1)
    
    # Импортируем наши модули
    try:
        from ssh_manager import SSHConfigManager
        from presets import PRESETS
        from gui import SSHConfiguratorGUI
    except ImportError as e:
        print(f"ОШИБКА импорта модулей: {e}")
        print("Убедитесь, что все файлы находятся в одной директории:")
        print("  - main.py")
        print("  - ssh_manager.py")
        print("  - presets.py")
        print("  - gui.py")
        print("  - backup.py (опционально)")
        sys.exit(1)
    
    try:
        # Создаем менеджер конфигурации
        print("Инициализация менеджера SSH...")
        ssh_manager = SSHConfigManager()
        
        # Создаем и запускаем GUI
        print("Запуск графического интерфейса...")
        root = tk.Tk()
        app = SSHConfiguratorGUI(root, ssh_manager, PRESETS)
        
        # Центрируем окно
        window_width = 900
        window_height = 700
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        root.title("SSH Daemon Configurator - Linux")
        print("\nПриложение запущено. Закройте окно для выхода.")
        root.mainloop()
        
    except Exception as e:
        print(f"\nКРИТИЧЕСКАЯ ОШИБКА: {e}")
        print("\nПодробная информация об ошибке:")
        import traceback
        traceback.print_exc()
        
        if 'tkinter' in sys.modules:
            messagebox.showerror("Ошибка", f"Не удалось запустить приложение:\n{str(e)}")
        
        sys.exit(1)

if __name__ == "__main__":
    main()