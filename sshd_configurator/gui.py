#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
from datetime import datetime

class SSHConfiguratorGUI:
    def __init__(self, root, ssh_manager, presets):
        """
        Инициализация графического интерфейса
        
        Args:
            root: Главное окно Tkinter
            ssh_manager: Объект SSHConfigManager
            presets: Словарь с пресетами
        """
        self.root = root
        self.manager = ssh_manager
        self.presets = presets
        
        # Переменные для хранения данных
        self.current_config = None
        self.backup_list = []
        
        # Создаем интерфейс
        self.setup_ui()
        
        # Загружаем данные
        self.load_data()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Настраиваем главное окно
        self.root.configure(bg='#f0f0f0')
        
        # Создаем стили
        self.setup_styles()
        
        # Создаем вкладки
        self.create_notebook()
        
        # Создаем статусную строку
        self.create_status_bar()
        
        # Настраиваем меню
        self.create_menu()
    
    def setup_styles(self):
        """Настройка стилей виджетов"""
        style = ttk.Style()
        
        # Используем тему по умолчанию
        style.theme_use('clam')
        
        # Настраиваем цвета
        style.configure('Title.TLabel', 
                       font=('Helvetica', 14, 'bold'),
                       background='#f0f0f0')
        style.configure('Section.TLabel',
                       font=('Helvetica', 11, 'bold'),
                       background='#f0f0f0')
        style.configure('Status.TLabel',
                       font=('Helvetica', 9),
                       background='#e0e0e0')
    
    def create_notebook(self):
        """Создание вкладок интерфейса"""
        # Создаем Notebook (панель вкладок)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Создаем вкладки
        self.create_basic_tab()
        self.create_security_tab()
        self.create_presets_tab()
        self.create_backups_tab()
        self.create_status_tab()
    
    def create_basic_tab(self):
        """Вкладка основных настроек"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Основные')
        
        # Фрейм с прокруткой
        canvas = tk.Canvas(tab, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient='vertical', command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        
        scroll_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True, padx=(0, 5))
        scrollbar.pack(side='right', fill='y')
        
        # Заголовок
        ttk.Label(scroll_frame, text='Основные настройки SSH',
                 style='Title.TLabel').pack(pady=(10, 20))
        
        # Порт SSH
        port_frame = ttk.LabelFrame(scroll_frame, text='Порт SSH', padding=10)
        port_frame.pack(fill='x', padx=10, pady=5)
        
        self.port_var = tk.StringVar(value='22')
        ttk.Label(port_frame, text='Порт:').pack(side='left', padx=(0, 10))
        ttk.Entry(port_frame, textvariable=self.port_var, width=10).pack(side='left')
        
        # Доступ root
        root_frame = ttk.LabelFrame(scroll_frame, text='Доступ для root', padding=10)
        root_frame.pack(fill='x', padx=10, pady=5)
        
        self.root_login_var = tk.StringVar(value='prohibit-password')
        options = ['yes', 'no', 'prohibit-password', 'without-password']
        for option in options:
            ttk.Radiobutton(root_frame, text=option, 
                           variable=self.root_login_var, 
                           value=option).pack(anchor='w')
        
        # Методы аутентификации
        auth_frame = ttk.LabelFrame(scroll_frame, text='Методы аутентификации', padding=10)
        auth_frame.pack(fill='x', padx=10, pady=5)
        
        self.password_auth_var = tk.BooleanVar(value=True)
        self.pubkey_auth_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(auth_frame, text='Парольная аутентификация',
                       variable=self.password_auth_var).pack(anchor='w')
        ttk.Checkbutton(auth_frame, text='Аутентификация по ключу',
                       variable=self.pubkey_auth_var).pack(anchor='w')
        
        # X11 Forwarding
        x11_frame = ttk.LabelFrame(scroll_frame, text='X11 Forwarding', padding=10)
        x11_frame.pack(fill='x', padx=10, pady=5)
        
        self.x11_var = tk.StringVar(value='yes')
        ttk.Radiobutton(x11_frame, text='Включить', 
                       variable=self.x11_var, value='yes').pack(anchor='w')
        ttk.Radiobutton(x11_frame, text='Отключить', 
                       variable=self.x11_var, value='no').pack(anchor='w')
        
        # Кнопка сохранения
        ttk.Button(scroll_frame, text='Сохранить настройки',
                  command=self.save_basic_settings).pack(pady=20)
    
    def create_security_tab(self):
        """Вкладка настроек безопасности"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Безопасность')
        
        canvas = tk.Canvas(tab, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient='vertical', command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        
        scroll_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True, padx=(0, 5))
        scrollbar.pack(side='right', fill='y')
        
        # Заголовок
        ttk.Label(scroll_frame, text='Настройки безопасности',
                 style='Title.TLabel').pack(pady=(10, 20))
        
        # Максимальное количество попыток
        frame1 = ttk.Frame(scroll_frame)
        frame1.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(frame1, text='Максимальное количество попыток входа:',
                 width=35).pack(side='left')
        self.max_auth_var = tk.StringVar(value='6')
        ttk.Entry(frame1, textvariable=self.max_auth_var, width=10).pack(side='left')
        
        # Время ожидания аутентификации
        frame2 = ttk.Frame(scroll_frame)
        frame2.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(frame2, text='Время ожидания аутентификации (секунды):',
                 width=35).pack(side='left')
        self.login_grace_var = tk.StringVar(value='120')
        ttk.Entry(frame2, textvariable=self.login_grace_var, width=10).pack(side='left')
        
        # Интервал Keep Alive
        frame3 = ttk.Frame(scroll_frame)
        frame3.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(frame3, text='Интервал Keep Alive (секунды):',
                 width=35).pack(side='left')
        self.keepalive_var = tk.StringVar(value='0')
        ttk.Entry(frame3, textvariable=self.keepalive_var, width=10).pack(side='left')
        
        # Разрешенные пользователи
        frame4 = ttk.Frame(scroll_frame)
        frame4.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(frame4, text='Разрешенные пользователи:').pack(anchor='w')
        self.allowed_users_var = tk.StringVar()
        ttk.Entry(frame4, textvariable=self.allowed_users_var, 
                 width=50).pack(fill='x', pady=(5, 0))
        ttk.Label(frame4, text='(через пробел)', font=('Helvetica', 9)).pack(anchor='w')
        
        # Разрешенные группы
        frame5 = ttk.Frame(scroll_frame)
        frame5.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(frame5, text='Разрешенные группы:').pack(anchor='w')
        self.allowed_groups_var = tk.StringVar()
        ttk.Entry(frame5, textvariable=self.allowed_groups_var, 
                 width=50).pack(fill='x', pady=(5, 0))
        ttk.Label(frame5, text='(через пробел)', font=('Helvetica', 9)).pack(anchor='w')
        
        # Кнопка сохранения
        ttk.Button(scroll_frame, text='Сохранить настройки безопасности',
                  command=self.save_security_settings).pack(pady=20)
    
    def create_presets_tab(self):
        """Вкладка с пресетами настроек"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Пресеты')
        
        # Заголовок
        ttk.Label(tab, text='Готовые пресеты настроек',
                 style='Title.TLabel').pack(pady=(10, 20))
        
        # Выбор пресета
        frame1 = ttk.Frame(tab)
        frame1.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(frame1, text='Выберите пресет:').pack(side='left', padx=(0, 10))
        self.preset_var = tk.StringVar()
        
        preset_names = []
        for key, preset in self.presets.items():
            preset_names.append(f"{preset['name']} ({key})")
        
        self.preset_combo = ttk.Combobox(frame1, textvariable=self.preset_var,
                                        values=preset_names, state='readonly', width=40)
        self.preset_combo.pack(side='left')
        self.preset_combo.bind('<<ComboboxSelected>>', self.on_preset_selected)
        
        # Описание пресета
        frame2 = ttk.LabelFrame(tab, text='Описание пресета', padding=10)
        frame2.pack(fill='x', padx=20, pady=10)
        
        self.preset_desc = tk.Text(frame2, height=6, width=60,
                                  wrap='word', state='disabled',
                                  bg='#f9f9f9', relief='flat')
        self.preset_desc.pack()
        
        # Предпросмотр настроек
        frame3 = ttk.LabelFrame(tab, text='Настройки пресета', padding=10)
        frame3.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.preset_preview = scrolledtext.ScrolledText(frame3, height=15,
                                                       state='disabled')
        self.preset_preview.pack(fill='both', expand=True)
        
        # Кнопки
        frame4 = ttk.Frame(tab)
        frame4.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(frame4, text='Применить пресет',
                  command=self.apply_preset).pack(side='left', padx=(0, 10))
        ttk.Button(frame4, text='Загрузить в основные настройки',
                  command=self.load_preset_to_ui).pack(side='left')
    
    def create_backups_tab(self):
        """Вкладка управления бэкапами"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Бэкапы')
        
        # Верхняя панель с кнопками
        top_frame = ttk.Frame(tab)
        top_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(top_frame, text='Создать бэкап',
                  command=self.create_backup).pack(side='left', padx=(0, 10))
        ttk.Button(top_frame, text='Обновить список',
                  command=self.refresh_backups).pack(side='left')
        
        # Список бэкапов
        frame = ttk.LabelFrame(tab, text='Доступные бэкапы', padding=10)
        frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Создаем Treeview для отображения бэкапов
        columns = ('name', 'date', 'size', 'comment')
        self.backup_tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        # Настраиваем заголовки
        self.backup_tree.heading('name', text='Имя файла')
        self.backup_tree.heading('date', text='Дата создания')
        self.backup_tree.heading('size', text='Размер')
        self.backup_tree.heading('comment', text='Комментарий')
        
        # Настраиваем колонки
        self.backup_tree.column('name', width=250)
        self.backup_tree.column('date', width=150)
        self.backup_tree.column('size', width=80)
        self.backup_tree.column('comment', width=200)
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(frame, orient='vertical', 
                                 command=self.backup_tree.yview)
        self.backup_tree.configure(yscrollcommand=scrollbar.set)
        
        self.backup_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Кнопки управления бэкапами
        bottom_frame = ttk.Frame(tab)
        bottom_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(bottom_frame, text='Восстановить выделенный',
                  command=self.restore_selected_backup).pack(side='left', padx=(0, 10))
        ttk.Button(bottom_frame, text='Удалить выделенный',
                  command=self.delete_selected_backup).pack(side='left')
    
    def create_status_tab(self):
        """Вкладка статуса системы"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Статус')
        
        # Заголовок
        ttk.Label(tab, text='Статус системы',
                 style='Title.TLabel').pack(pady=(10, 20))
        
        # Статус службы SSH
        status_frame = ttk.LabelFrame(tab, text='Статус службы SSH', padding=10)
        status_frame.pack(fill='x', padx=20, pady=10)
        
        self.service_status_var = tk.StringVar(value='Проверка...')
        ttk.Label(status_frame, textvariable=self.service_status_var,
                 font=('Helvetica', 12)).pack()
        
        # Кнопки управления службой
        btn_frame = ttk.Frame(status_frame)
        btn_frame.pack(pady=(10, 0))
        
        ttk.Button(btn_frame, text='Проверить статус',
                  command=self.check_service_status).pack(side='left', padx=(0, 10))
        ttk.Button(btn_frame, text='Перезапустить службу',
                  command=self.restart_service).pack(side='left')
        
        # Текущая конфигурация
        config_frame = ttk.LabelFrame(tab, text='Текущая конфигурация', padding=10)
        config_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.config_text = scrolledtext.ScrolledText(config_frame, height=20)
        self.config_text.pack(fill='both', expand=True)
        self.config_text.config(state='disabled')
    
    def create_status_bar(self):
        """Создание статусной строки"""
        self.status_bar = ttk.Frame(self.root, relief='sunken')
        self.status_bar.pack(side='bottom', fill='x')
        
        self.status_label = ttk.Label(self.status_bar, text='Готов',
                                     style='Status.TLabel')
        self.status_label.pack(side='left', padx=5, pady=2)
    
    def create_menu(self):
        """Создание меню приложения"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Меню "Настройки"
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Настройки", menu=settings_menu)
        settings_menu.add_command(label="Применить все настройки",
                                 command=self.apply_all_settings)
        
        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
    
    def load_data(self):
        """Загрузка данных при запуске"""
        self.set_status("Загрузка данных...")
        
        # Загружаем в отдельном потоке
        def load_thread():
            try:
                # Загружаем текущую конфигурацию
                self.current_config = self.manager.read_current_config()
                
                # Обновляем интерфейс
                self.root.after(0, self.update_ui_from_config)
                
                # Обновляем список бэкапов
                self.root.after(0, self.refresh_backups)
                
                # Проверяем статус службы
                self.root.after(0, self.check_service_status)
                
                self.set_status("Готов")
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Ошибка", f"Не удалось загрузить данные: {str(e)}"))
                self.set_status("Ошибка загрузки")
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def update_ui_from_config(self):
        """Обновление интерфейса из текущей конфигурации"""
        if not self.current_config:
            return
        
        try:
            # Основные настройки
            self.port_var.set(self.current_config.get('Port', '22'))
            self.root_login_var.set(self.current_config.get('PermitRootLogin', 'prohibit-password'))
            
            # Методы аутентификации
            pass_auth = self.current_config.get('PasswordAuthentication', 'yes')
            self.password_auth_var.set(pass_auth == 'yes')
            
            pubkey_auth = self.current_config.get('PubkeyAuthentication', 'yes')
            self.pubkey_auth_var.set(pubkey_auth == 'yes')
            
            # X11
            self.x11_var.set(self.current_config.get('X11Forwarding', 'yes'))
            
            # Безопасность
            self.max_auth_var.set(self.current_config.get('MaxAuthTries', '6'))
            self.login_grace_var.set(self.current_config.get('LoginGraceTime', '120'))
            self.keepalive_var.set(self.current_config.get('ClientAliveInterval', '0'))
            self.allowed_users_var.set(self.current_config.get('AllowUsers', ''))
            self.allowed_groups_var.set(self.current_config.get('AllowGroups', ''))
            
            # Обновляем вкладку статуса
            self.update_config_display()
            
        except Exception as e:
            print(f"Ошибка обновления UI: {e}")
    
    def update_config_display(self):
        """Обновление отображения конфигурации"""
        if not self.current_config:
            return
        
        self.config_text.config(state='normal')
        self.config_text.delete(1.0, tk.END)
        
        # Форматируем конфигурацию для отображения
        lines = []
        for key, value in sorted(self.current_config.items()):
            lines.append(f"{key}: {value}")
        
        self.config_text.insert(1.0, "\n".join(lines))
        self.config_text.config(state='disabled')
    
    def set_status(self, message):
        """Установка сообщения в статусной строке"""
        self.status_label.config(text=message)
    
    def save_basic_settings(self):
        """Сохранение основных настроек"""
        self.set_status("Сохранение основных настроек...")
        
        settings = {
            'Port': self.port_var.get(),
            'PermitRootLogin': self.root_login_var.get(),
            'PasswordAuthentication': 'yes' if self.password_auth_var.get() else 'no',
            'PubkeyAuthentication': 'yes' if self.pubkey_auth_var.get() else 'no',
            'X11Forwarding': self.x11_var.get()
        }
        
        self.apply_settings(settings, "Основные настройки")
    
    def save_security_settings(self):
        """Сохранение настроек безопасности"""
        self.set_status("Сохранение настроек безопасности...")
        
        settings = {
            'MaxAuthTries': self.max_auth_var.get(),
            'LoginGraceTime': self.login_grace_var.get(),
            'ClientAliveInterval': self.keepalive_var.get()
        }
        
        # Добавляем пользователей и группы, если указаны
        users = self.allowed_users_var.get().strip()
        groups = self.allowed_groups_var.get().strip()
        
        if users:
            settings['AllowUsers'] = users
        if groups:
            settings['AllowGroups'] = groups
        
        self.apply_settings(settings, "Настройки безопасности")
    
    def apply_settings(self, settings, description):
        """Применение настроек"""
        def apply_thread():
            try:
                result = self.manager.apply_settings(
                    settings,
                    create_backup=True,
                    backup_comment=description
                )
                
                if result['status'] == 'success':
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Успех", "Настройки успешно применены!"))
                    
                    # Обновляем текущую конфигурацию
                    self.current_config = self.manager.read_current_config()
                    self.root.after(0, self.update_config_display)
                    
                    # Предлагаем перезапустить службу
                    self.root.after(0, lambda: self.ask_restart_service())
                    
                else:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Ошибка", "Не удалось применить настройки"))
                
                self.set_status("Готов")
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Ошибка", f"Ошибка при применении настроек:\n{str(e)}"))
                self.set_status("Ошибка")
        
        threading.Thread(target=apply_thread, daemon=True).start()
    
    def ask_restart_service(self):
        """Запрос на перезапуск службы"""
        if messagebox.askyesno("Перезапуск службы",
                              "Настройки применены.\nПерезапустить службу SSH?"):
            self.restart_service()
    
    def on_preset_selected(self, event):
        """Обработка выбора пресета"""
        selection = self.preset_combo.get()
        if not selection:
            return
        
        # Извлекаем ключ пресета из строки
        preset_key = selection.split('(')[-1].strip(')')
        preset = self.presets.get(preset_key)
        
        if not preset:
            return
        
        # Обновляем описание
        self.preset_desc.config(state='normal')
        self.preset_desc.delete(1.0, tk.END)
        self.preset_desc.insert(1.0, preset['description'])
        self.preset_desc.config(state='disabled')
        
        # Обновляем предпросмотр
        self.preset_preview.config(state='normal')
        self.preset_preview.delete(1.0, tk.END)
        
        for key, value in preset['settings'].items():
            self.preset_preview.insert(tk.END, f"{key}: {value}\n")
        
        self.preset_preview.config(state='disabled')
    
    def apply_preset(self):
        """Применение выбранного пресета"""
        selection = self.preset_combo.get()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пресет")
            return
        
        # Извлекаем ключ пресета
        preset_key = selection.split('(')[-1].strip(')')
        preset = self.presets.get(preset_key)
        
        if not preset:
            messagebox.showerror("Ошибка", "Пресет не найден")
            return
        
        if messagebox.askyesno("Применение пресета",
                              f"Применить пресет '{preset['name']}'?\n\n"
                              "Текущие настройки будут изменены."):
            self.apply_settings(preset['settings'], f"Пресет: {preset['name']}")
    
    def load_preset_to_ui(self):
        """Загрузка настроек пресета в интерфейс"""
        selection = self.preset_combo.get()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пресет")
            return
        
        # Извлекаем ключ пресета
        preset_key = selection.split('(')[-1].strip(')')
        preset = self.presets.get(preset_key)
        
        if not preset:
            return
        
        settings = preset['settings']
        
        # Обновляем основные настройки
        if 'Port' in settings:
            self.port_var.set(settings['Port'])
        if 'PermitRootLogin' in settings:
            self.root_login_var.set(settings['PermitRootLogin'])
        if 'PasswordAuthentication' in settings:
            self.password_auth_var.set(settings['PasswordAuthentication'] == 'yes')
        if 'PubkeyAuthentication' in settings:
            self.pubkey_auth_var.set(settings['PubkeyAuthentication'] == 'yes')
        if 'X11Forwarding' in settings:
            self.x11_var.set(settings['X11Forwarding'])
        
        # Обновляем настройки безопасности
        if 'MaxAuthTries' in settings:
            self.max_auth_var.set(settings['MaxAuthTries'])
        if 'LoginGraceTime' in settings:
            self.login_grace_var.set(settings['LoginGraceTime'])
        if 'ClientAliveInterval' in settings:
            self.keepalive_var.set(settings['ClientAliveInterval'])
        
        messagebox.showinfo("Успех", "Настройки пресета загружены в интерфейс")
    
    def create_backup(self):
        """Создание бэкапа"""
        comment = tk.simpledialog.askstring("Комментарий к бэкапу",
                                           "Введите комментарий:")
        if comment is None:  # Пользователь нажал Cancel
            return
        
        self.set_status("Создание бэкапа...")
        
        def backup_thread():
            try:
                backup_path = self.manager.create_backup(comment or "Ручное создание")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Успех", f"Бэкап создан:\n{backup_path}"))
                self.root.after(0, self.refresh_backups)
                self.set_status("Готов")
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Ошибка", f"Ошибка создания бэкапа:\n{str(e)}"))
                self.set_status("Ошибка")
        
        threading.Thread(target=backup_thread, daemon=True).start()
    
    def refresh_backups(self):
        """Обновление списка бэкапов"""
        def refresh_thread():
            try:
                backups = self.manager.list_backups()
                self.backup_list = backups
                
                self.root.after(0, self.update_backup_list)
                self.set_status("Готов")
            except Exception as e:
                self.root.after(0, lambda: print(f"Ошибка обновления бэкапов: {e}"))
        
        threading.Thread(target=refresh_thread, daemon=True).start()
    
    def update_backup_list(self):
        """Обновление списка бэкапов в Treeview"""
        # Очищаем текущий список
        for item in self.backup_tree.get_children():
            self.backup_tree.delete(item)
        
        # Добавляем бэкапы
        for backup in self.backup_list:
            size_kb = backup['size'] / 1024
            date_str = backup['modified'].strftime("%Y-%m-%d %H:%M")
            comment = backup['meta'].get('comment', '')
            
            self.backup_tree.insert('', 'end', values=(
                backup['name'],
                date_str,
                f"{size_kb:.1f} KB",
                comment
            ))
    
    def restore_selected_backup(self):
        """Восстановление выделенного бэкапа"""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите бэкап для восстановления")
            return
        
        item = self.backup_tree.item(selection[0])
        backup_name = item['values'][0]
        
        # Находим полный путь к бэкапу
        backup_path = None
        for backup in self.backup_list:
            if backup['name'] == backup_name:
                backup_path = backup['path']
                break
        
        if not backup_path:
            messagebox.showerror("Ошибка", "Бэкап не найден")
            return
        
        if messagebox.askyesno("Восстановление",
                              f"Восстановить конфигурацию из бэкапа?\n\n"
                              f"{backup_name}\n\n"
                              "Текущие настройки будут заменены."):
            self.set_status("Восстановление бэкапа...")
            
            def restore_thread():
                try:
                    result = self.manager.restore_backup(backup_path)
                    
                    if result['status'] == 'success':
                        self.root.after(0, lambda: messagebox.showinfo(
                            "Успех", "Конфигурация восстановлена!"))
                        
                        # Обновляем данные
                        self.current_config = self.manager.read_current_config()
                        self.root.after(0, self.update_ui_from_config)
                        self.root.after(0, self.refresh_backups)
                        
                        # Предлагаем перезапустить службу
                        self.root.after(0, lambda: self.ask_restart_service())
                    else:
                        self.root.after(0, lambda: messagebox.showerror(
                            "Ошибка", "Не удалось восстановить бэкап"))
                    
                    self.set_status("Готов")
                    
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Ошибка", f"Ошибка восстановления:\n{str(e)}"))
                    self.set_status("Ошибка")
            
            threading.Thread(target=restore_thread, daemon=True).start()
    
    def delete_selected_backup(self):
        """Удаление выделенного бэкапа"""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите бэкап для удаления")
            return
        
        item = self.backup_tree.item(selection[0])
        backup_name = item['values'][0]
        
        if messagebox.askyesno("Удаление",
                              f"Удалить бэкап?\n\n{backup_name}"):
            self.set_status("Удаление бэкапа...")
            
            def delete_thread():
                try:
                    # Находим и удаляем файлы бэкапа
                    import os
                    for backup in self.backup_list:
                        if backup['name'] == backup_name:
                            os.remove(backup['path'])
                            meta_file = backup['path'] + '.meta'
                            if os.path.exists(meta_file):
                                os.remove(meta_file)
                            break
                    
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Успех", "Бэкап удален"))
                    self.root.after(0, self.refresh_backups)
                    self.set_status("Готов")
                    
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Ошибка", f"Ошибка удаления:\n{str(e)}"))
                    self.set_status("Ошибка")
            
            threading.Thread(target=delete_thread, daemon=True).start()
    
    def check_service_status(self):
        """Проверка статуса службы"""
        def check_thread():
            try:
                status = self.manager.get_service_status()
                status_text = {
                    'active': 'Активна',
                    'inactive': 'Неактивна',
                    'failed': 'Ошибка',
                    'unknown': 'Неизвестно'
                }.get(status, f' {status}')
                
                self.root.after(0, lambda: self.service_status_var.set(
                    f"Статус: {status_text}"))
                self.set_status("Готов")
            except Exception as e:
                self.root.after(0, lambda: self.service_status_var.set(
                    f"Ошибка: {str(e)}"))
                self.set_status("Ошибка")
        
        threading.Thread(target=check_thread, daemon=True).start()
    
    def restart_service(self):
        """Перезапуск службы SSH"""
        if messagebox.askyesno("Перезапуск службы",
                              "Перезапустить службу SSH?"):
            self.set_status("Перезапуск службы...")
            
            def restart_thread():
                try:
                    result = self.manager.restart_service()
                    
                    if result['status'] == 'success':
                        self.root.after(0, lambda: messagebox.showinfo(
                            "Успех", "Служба перезапущена"))
                        self.root.after(0, self.check_service_status)
                    else:
                        self.root.after(0, lambda: messagebox.showerror(
                            "Ошибка", f"Не удалось перезапустить службу:\n{result['message']}"))
                    
                    self.set_status("Готов")
                    
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Ошибка", f"Ошибка перезапуска:\n{str(e)}"))
                    self.set_status("Ошибка")
            
            threading.Thread(target=restart_thread, daemon=True).start()
    
    def apply_all_settings(self):
        """Применение всех настроек из интерфейса"""
        # Собираем все настройки
        settings = {}
        
        # Основные настройки
        settings.update({
            'Port': self.port_var.get(),
            'PermitRootLogin': self.root_login_var.get(),
            'PasswordAuthentication': 'yes' if self.password_auth_var.get() else 'no',
            'PubkeyAuthentication': 'yes' if self.pubkey_auth_var.get() else 'no',
            'X11Forwarding': self.x11_var.get(),
            'MaxAuthTries': self.max_auth_var.get(),
            'LoginGraceTime': self.login_grace_var.get(),
            'ClientAliveInterval': self.keepalive_var.get()
        })
        
        # Пользователи и группы
        users = self.allowed_users_var.get().strip()
        groups = self.allowed_groups_var.get().strip()
        
        if users:
            settings['AllowUsers'] = users
        if groups:
            settings['AllowGroups'] = groups
        
        self.apply_settings(settings, "Все настройки")
    
    def show_about(self):
        """Показать информацию о программе"""
        about_text = """SSH Daemon Configurator for Linux
        
Версия: 1.0
Разработчик: Python SSH Configurator Team

Описание: Приложение для настройки SSH сервера
на системах Linux с графическим интерфейсом.

Лицензия: MIT
"""
        messagebox.showinfo("О программе", about_text)