
from db import get_session, Users, Payments
import bcrypt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QComboBox, QLineEdit, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QDateEdit, QHBoxLayout, QMessageBox, 
    QDialog, QSpinBox, QDoubleSpinBox, QScrollArea
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QHeaderView
from datetime import datetime
from fpdf import FPDF
import os

class LoginWindow(QDialog):
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Вход в систему')
        self.setGeometry(100, 100, 200, 200)
        self.user = None
        self.encrypt_passwords()
        # Основной вертикальный лэйаут
        self.layout = QVBoxLayout()

        # Горизонтальный лэйаут для имени пользователя и выпадающего списка
        user_layout = QHBoxLayout()

        # Лейбл для имени пользователя
        self.user_label = QLabel('Имя пользователя:')
        user_layout.addWidget(self.user_label)

        # Выпадающий список для выбора логина
        self.user_combo = QComboBox()
        user_layout.addWidget(self.user_combo)
        self.user_combo.setFixedWidth(150)

        # Устанавливаем выравнивание элементов по правому краю
        user_layout.setAlignment(Qt.AlignRight)

        # Добавляем горизонтальный лэйаут для логина в основной лэйаут
        self.layout.addLayout(user_layout)

        # Горизонтальный лэйаут для пароля (метка и поле ввода)
        password_layout = QHBoxLayout()

        # Лейбл для пароля
        self.password_label = QLabel('Пароль:')
        password_layout.addWidget(self.password_label)

        # Поле для ввода пароля
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedWidth(150)  # Устанавливаем одинаковую ширину для поля ввода
        password_layout.addWidget(self.password_input)

        # Устанавливаем выравнивание элементов по правому краю
        password_layout.setAlignment(Qt.AlignLeft)

        # Добавляем горизонтальный лэйаут для пароля в основной
        self.layout.addLayout(password_layout)

        # Горизонтальный лэйаут для кнопок
        button_layout = QHBoxLayout()

        # Кнопка Войти
        self.login_button = QPushButton('Войти')
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setFixedWidth(100)  # Устанавливаем меньший размер кнопки
        button_layout.addWidget(self.login_button)

        # Кнопка Выход
        self.exit_button = QPushButton('Выход')
        self.exit_button.clicked.connect(self.reject)
        self.exit_button.setFixedWidth(100)  # Устанавливаем меньший размер кнопки
        button_layout.addWidget(self.exit_button)

        # Устанавливаем выравнивание кнопок по правому краю
        button_layout.setAlignment(Qt.AlignRight)

        # Добавляем кнопки в основной лэйаут
        self.layout.addLayout(button_layout)

        # Устанавливаем основной лэйаут в окно
        self.setLayout(self.layout)

        # Загружаем пользователей в выпадающий список
        self.load_users()
    def encrypt_passwords(self):
        session = get_session()
        users = session.query(Users).all()
        for user in users:
            # Проверяем, если пароль не зашифрован (длина менее 60 символов для bcrypt)
            if len(user.password) < 60:
                # Генерируем хеш пароля с bcrypt
                hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
                user.password = hashed_password.decode('utf-8')  # Сохраняем как строку
        
        # Сохраняем изменения в базе данных
        session.commit()
        session.close()

    def load_users(self):
        session = get_session()  # get_session() возвращает соединение с БД
        users = session.query(Users).all()  # Загружаем пользователей из базы данных
        self.user_combo.clear()
        for user in users:
            self.user_combo.addItem(user.login)  # Добавляем логины в выпадающий список
        session.close()

    def handle_login(self):
        login = self.user_combo.currentText()
        password = self.password_input.text()

        session = get_session()
        user = session.query(Users).filter(Users.login == login).first()
        session.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            self.user = user
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")

class AddPaymentWindow(QDialog):
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Добавить платеж")
        self.setGeometry(200, 200, 300, 200)

        self.layout = QVBoxLayout()

        # Категория
        self.category_layout = QHBoxLayout()
        self.category_label = QLabel("Категория:")
        self.category_label.setAlignment(Qt.AlignCenter)
        self.category_layout.addWidget(self.category_label)

        self.category_combo = QComboBox(self)
        self.load_categories()
        self.category_combo.setFixedWidth(150)
        self.category_layout.addWidget(self.category_combo, alignment=Qt.AlignLeft)

        self.layout.addLayout(self.category_layout)

        # Название платежа
        self.name_layout = QHBoxLayout()
        self.name_label = QLabel("Название платежа:")
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_layout.addWidget(self.name_label)

        self.name_input = QLineEdit(self)
        self.name_input.setFixedWidth(150)
        self.name_layout.addWidget(self.name_input, alignment=Qt.AlignLeft)

        self.layout.addLayout(self.name_layout)

        # Количество (заменено на QSpinBox)
        self.quantity_layout = QHBoxLayout()
        self.quantity_label = QLabel("Количество:")
        self.quantity_label.setAlignment(Qt.AlignCenter)
        self.quantity_layout.addWidget(self.quantity_label)

        self.quantity_input = QSpinBox(self)  # Используем QSpinBox
        self.quantity_input.setMinimum(1)  # Минимальное значение
        self.quantity_input.setMaximum(10000)  # Максимальное значение
        self.quantity_input.setValue(1)  # Начальное значение
        self.quantity_layout.addWidget(self.quantity_input, alignment=Qt.AlignLeft)

        self.layout.addLayout(self.quantity_layout)

        # Цена
        self.price_layout = QHBoxLayout()

        # Метка "Цена"
        self.price_label = QLabel("Цена (₽):")
        self.price_label.setAlignment(Qt.AlignCenter)
        self.price_layout.addWidget(self.price_label)

        # Поле ввода
        self.price_input = QLineEdit(self)
        self.price_input.setFixedWidth(100)
        self.price_layout.addWidget(self.price_input, alignment=Qt.AlignLeft)

        # Добавляем layout для "Цена" в основной layout
        self.layout.addLayout(self.price_layout)

        # Кнопки
        self.button_layout = QHBoxLayout()

        self.add_button = QPushButton("Добавить", self)
        self.add_button.clicked.connect(self.add_payment)
        self.button_layout.addWidget(self.add_button)

        self.cancel_button = QPushButton("Отменить", self)
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)

    def load_categories(self):
        session = get_session()
        categories = session.query(Payments.category).distinct().all()
        self.category_combo.addItem("-")
        for category in categories:
            self.category_combo.addItem(category[0])
        session.close()

    def add_payment(self):
        category = self.category_combo.currentText()
        name = self.name_input.text()
        quantity = self.quantity_input.value()  # Получаем количество из QSpinBox
        price_text = self.price_input.text()

        try:
            price = float(price_text.strip())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Неверный формат цены!")
            return

        if not name.strip():
            QMessageBox.warning(self, "Ошибка", "Название платежа не может быть пустым!")
            return

        if quantity <= 0:
            QMessageBox.warning(self, "Ошибка", "Количество должно быть положительным числом!")
            return

        session = get_session()
        new_payment = Payments(
            user_id=self.user.user_id,
            date=datetime.utcnow(),
            category=category,
            name=name,
            quantity=quantity,
            price=price,
            total=quantity * price
        )
        session.add(new_payment)
        session.commit()
        session.close()

        QMessageBox.information(self, "Успех", "Платеж успешно добавлен!")
        self.accept()


class MainWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle('Основное окно')
        self.setGeometry(100, 100, 900, 600)

        self.layout = QVBoxLayout()
        self.filter_panel = QHBoxLayout()

        # Кнопки фильтрации
        self.add_button = QPushButton("+")
        self.add_button.clicked.connect(self.open_add_payment_window)
        self.filter_panel.addWidget(self.add_button)

        self.delete_button = QPushButton("-")
        self.delete_button.clicked.connect(self.delete_payment)
        self.filter_panel.addWidget(self.delete_button)

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate(2015, 1, 1))
        self.date_from.setDisplayFormat("dd.MM.yyyy")  # Формат даты
        self.date_from.setFixedWidth(120)  # Увеличиваем ширину поля
        self.date_from.dateTimeChanged.connect(self.filter_by_date)  # Обработчик изменения даты
        self.filter_panel.addWidget(QLabel("С"))
        self.filter_panel.addWidget(self.date_from)

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate(2018, 12, 31))
        self.date_to.setDisplayFormat("dd.MM.yyyy")  # Формат даты
        self.date_to.setFixedWidth(120)  # Увеличиваем ширину поля
        self.date_to.dateTimeChanged.connect(self.filter_by_date)  # Обработчик изменения даты
        self.filter_panel.addWidget(QLabel("По"))
        self.filter_panel.addWidget(self.date_to)

        self.category_combo = QComboBox()
        self.category_combo.currentTextChanged.connect(self.filter_by_category)
        self.filter_panel.addWidget(QLabel("Категория:"))
        self.filter_panel.addWidget(self.category_combo)

        self.filter_button = QPushButton("Выбрать")
        self.filter_button.clicked.connect(self.open_login_window)
        self.filter_panel.addWidget(self.filter_button)

        self.clear_button = QPushButton("Очистить")
        self.clear_button.clicked.connect(self.load_data)
        self.filter_panel.addWidget(self.clear_button)

        self.report_button = QPushButton("Генерировать отчет")
        self.report_button.clicked.connect(self.generate_report)
        self.filter_panel.addWidget(self.report_button)

        self.layout.addLayout(self.filter_panel)

        # Создание таблицы
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Наименование платежа", "Количество", "Цена", "Сумма", "Категория"])

        # Настроим растяжение столбцов и строк
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)

        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)

        self.layout.addWidget(self.table)

        self.setLayout(self.layout)

        self.load_categories()
    def get_current_user_id(self):
        """Метод для получения идентификатора текущего пользователя"""
        # Реализуйте это в зависимости от вашего контекста. Например, это может быть вызов текущего сеанса пользователя
        # В качестве примера, возвращаем некоторое значение. Замените на вашу логику получения пользователя.
        return self.user.user_id if self.user.user_id else None
    def load_data1(self):
        print("Загрузка данных с фильтрацией по дате и пользователю")
        """Загрузка данных с фильтрацией по дате и пользователю"""
        session = get_session()

        # Получаем значения из QDateEdit
        date_from = self.date_from.date().toPython()
        date_to = self.date_to.date().toPython()

        # Проверяем, что дата_from не позже даты_to
        if date_from > date_to:
            QMessageBox.warning(self, "Ошибка", "Дата начала не может быть позже даты окончания")
            return

        # Получаем идентификатор текущего пользователя
        current_user_id = self.get_current_user_id()

        if not current_user_id:
            QMessageBox.warning(self, "Ошибка", "Пользователь не авторизован.")
            return

        # Фильтруем данные по дате и пользователю
        query = session.query(Payments).filter(
            Payments.date >= date_from,
            Payments.date <= date_to,
            Payments.user_id == current_user_id  # Фильтрация по текущему пользователю
        )

        # Выводим сам запрос и текущего пользователя
        print(f"Запрос для фильтрации: {query}")
        print(f"Текущий пользователь: {self.user}")  # Здесь предполагается, что self.user содержит текущего пользователя

        # Получаем отфильтрованные данные
        payments = query.all()

        # Обновляем таблицу с данными
        self.table.setRowCount(0)  # Сначала очищаем таблицу
        self.table.setRowCount(len(payments))  # Устанавливаем количество строк

        for row, payment in enumerate(payments):
            self.table.setItem(row, 0, QTableWidgetItem(payment.name))
            self.table.setItem(row, 1, QTableWidgetItem(str(payment.quantity)))
            self.table.setItem(row, 2, QTableWidgetItem(f"{payment.price:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{payment.total:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(payment.category))

        session.close()
    def filter_by_date(self):
        """Обновление данных на основе выбранной даты и категории"""
        print("Дата изменена")
        
        
        # Сохраняем выбранные значения в свойствах объекта
        self.date_from_value = self.date_from.date().toPython()
        self.date_to_value = self.date_to.date().toPython()
        self.selected_category = self.category_combo.currentText()
        
        # Вызываем метод загрузки данных
        self.load_data1()

    def load_categories(self):
        session = get_session()
        categories = session.query(Payments.category).distinct().all()
        self.category_combo.clear()
        self.category_combo.addItem("-")
        for category in categories:
            self.category_combo.addItem(category[0])
        session.close()

    def open_add_payment_window(self):
        add_payment_window = AddPaymentWindow(self, user=self.user)
        if add_payment_window.exec():
            self.load_data()

    def delete_payment(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите запись для удаления!")
            return

        payment_name = self.table.item(selected_row, 0).text()
        session = get_session()
        payment = session.query(Payments).filter_by(name=payment_name, user_id=self.user.user_id).first()
        if payment:
            session.delete(payment)
            session.commit()
            QMessageBox.information(self, "Успех", "Запись успешно удалена!")
        else:
            QMessageBox.warning(self, "Ошибка", "Запись не найдена!")
        session.close()
        self.load_data()

    def filter_by_category(self):
        selected_category = self.category_combo.currentText()
        session = get_session()
        
        # Условие для фильтрации по категории
        if selected_category == "-":  # Если выбрано "все"
            payments = session.query(Payments).filter(Payments.user_id == self.user.user_id).all()
        else:  # Если выбрана конкретная категория
            payments = session.query(Payments).filter(
                Payments.user_id == self.user.user_id,
                Payments.category == selected_category
            ).all()
        
        # Обновление таблицы
        self.table.setRowCount(len(payments))
        for row, payment in enumerate(payments):
            self.table.setItem(row, 0, QTableWidgetItem(payment.name))
            self.table.setItem(row, 1, QTableWidgetItem(str(payment.quantity)))
            self.table.setItem(row, 2, QTableWidgetItem(f"{payment.price:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{payment.total:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(payment.category))
        
        session.close()

    def generate_report(self):
        try:
            # Загружаем данные из базы данных
            session = get_session()  # Получаем сессию для работы с базой данных
            payments = session.query(Payments).filter(Payments.user_id == self.user.user_id).all()

            # Создаем объект PDF
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)  # Автоматический перенос на новую страницу
            pdf.add_page()

            # Проверяем наличие шрифта и добавляем его
            font_path = './FreeSans.ttf'  # Путь к шрифту
            if os.path.exists(font_path):
                pdf.add_font('FreeSans', '', font_path, uni=True)
                pdf.set_font('FreeSans', '', 12)
            else:
                QMessageBox.warning(self, "Ошибка шрифта", "Шрифт FreeSans не найден.")
                return

            # Группируем платежи по категориям
            categories = {}  # Словарь для категорий
            for payment in payments:
                if payment.category not in categories:
                    categories[payment.category] = []
                categories[payment.category].append(payment)

            total_amount = 0  # Общая сумма всех платежей

            # Функция для добавления шапки на первой странице
            def add_header(pdf):
                pdf.set_font('FreeSans', '', 12)
                pdf.cell(0, 10, "Список платежей", ln=True, align='C')
                pdf.ln(10)  # Отступ после заголовка

            # Номер страницы
            page_number = 1

            # Добавляем шапку только один раз, в начале отчета
            add_header(pdf)

            # Добавление данных по категориям
            for category, category_payments in categories.items():
                # Заголовок категории
                pdf.set_font('FreeSans', '', 16)  # Жирный шрифт для заголовка категории
                pdf.cell(0, 10, category, ln=True, align='L')
                pdf.set_font('FreeSans', '', 12)  # Возвращаем обычный шрифт

                # Строки для каждого платежа
                for payment in category_payments:
                    pdf.cell(100, 10, payment.name, border=0)
                    pdf.cell(40, 10, f"{payment.price:.2f} р.", border=0, align='R')
                    pdf.ln()
                    total_amount += payment.price

                pdf.ln(5)  # Отступ между категориями

                # Проверяем, нужно ли добавить новую страницу
                if pdf.get_y() > 260:  # Если текущая позиция слишком низка (на странице уже много данных)
                    pdf.add_page()
                    page_number += 1
                    add_header(pdf)  # Добавляем шапку на новой странице

                    # Добавляем футер на новую страницу сразу
                    add_footer(pdf, page_number)

            # Итоговая сумма
            pdf.set_font('FreeSans', '', 16)
            pdf.cell(40, 20, "Итого: " + f"{total_amount:.2f} р.", ln=True, align='R')

            # Функция для добавления футера с ФИО и номером страницы
            def add_footer(pdf, page_number):
                pdf.set_font('FreeSans', '', 10)
                pdf.set_y(270)  # Устанавливаем позицию для футера (15 мм от нижней границы страницы)
                pdf.cell(0, 10, f"ФИО: {self.user.fio}", 0, 0, 'L')  # ФИО в левой части
                pdf.cell(0, 10, f"Страница {page_number}", 0, 0, 'R')  # Номер страницы в правой части

            # Добавляем футер на последнюю страницу
            add_footer(pdf, page_number)

            # Сохраняем PDF на диск
            pdf_output_path = f"./report_{self.user.user_id}.pdf"  # Путь для сохранения отчета
            pdf.output(pdf_output_path)

            # Показать сообщение о завершении
            QMessageBox.information(self, "Экспорт завершен", f"Отчет был успешно экспортирован в {pdf_output_path}.")

            session.close()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка экспорта", f"Произошла ошибка при экспорте в PDF: {str(e)}")

    def load_data(self):
        """Загрузка данных платежей"""
        session = get_session()
        payments = session.query(Payments).filter(Payments.user_id == self.user.user_id).all()
        self.table.setRowCount(len(payments))
        for row, payment in enumerate(payments):
            self.table.setItem(row, 0, QTableWidgetItem(payment.name))
            self.table.setItem(row, 1, QTableWidgetItem(str(payment.quantity)))
            self.table.setItem(row, 2, QTableWidgetItem(f"{payment.price:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{payment.total:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(payment.category))
        session.close()

    def load_categories(self):
        """Загрузка категорий в выпадающий список"""
        session = get_session()
        categories = session.query(Payments.category).distinct().all()
        self.category_combo.clear()
        self.category_combo.addItem("-")
        for category in categories:
            self.category_combo.addItem(category[0])
        session.close()

    def open_login_window(self):
        """Закрыть текущее окно и открыть окно авторизации"""
        self.close()  # Закрываем текущее окно

        login_window = LoginWindow()
        if login_window.exec() == QDialog.Accepted:  # Если авторизация прошла успешно
            new_user = login_window.user
            if new_user:
                self.new_main_window = MainWindow(new_user)  # Создаем новое окно
                self.new_main_window.show()

            
    def handle_login(self):
        """Обрабатываем вход пользователя"""
        login = self.user_combo.currentText()
        password = self.password_input.text()

        session = get_session()
        user = session.query(Users).filter(Users.login == login).first()
        session.close()

        if user and user.password == password:
            QMessageBox.information(self, "Успех", "Добро пожаловать!")
            self.accept_login(user)  # Передаем авторизованного пользователя
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")


    def delete_payment(self):
        """Удаление выбранного платежа"""
        self.load_data()
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите запись для удаления!")
            return

        record_name = self.table.item(selected_row, 0).text()
        payment_id = self.get_payment_id(selected_row)

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить запись «{record_name}»?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            session = get_session()
            payment = session.query(Payments).get(payment_id)
            if payment:
                session.delete(payment)
                session.commit()
                session.close()

                QMessageBox.information(self, "Успех", "Запись успешно удалена!")
                self.load_data()
            else:
                session.close()
                QMessageBox.warning(self, "Ошибка", "Запись не найдена!")

    def get_payment_id(self, row):
        """Получить ID платежа из строки таблицы"""
        session = get_session()
        payment_name = self.table.item(row, 0).text()
        payment = session.query(Payments).filter_by(name=payment_name, user_id=self.user.user_id).first()
        session.close()
        return payment.id if payment else None

    def open_add_payment_window(self):
        """Открытие окна добавления платежа"""
        add_payment_window = AddPaymentWindow(parent=self, user=self.user)
        if add_payment_window.exec():
            self.load_data()  # Перезагружаем данные после добавления


    def filter_by_category(self):
        """Фильтрует платежи при выборе категории"""
        selected_category = self.category_combo.currentText()

        session = get_session()

        if selected_category == "-":
            payments = session.query(Payments).filter(Payments.user_id == self.user.user_id).all()
        else:
            payments = (
                session.query(Payments)
                .filter(Payments.user_id == self.user.user_id, Payments.category == selected_category)
                .all()
            )

        self.table.setRowCount(len(payments))
        for row, payment in enumerate(payments):
            self.table.setItem(row, 0, QTableWidgetItem(payment.name))
            self.table.setItem(row, 1, QTableWidgetItem(str(payment.quantity)))
            self.table.setItem(row, 2, QTableWidgetItem(f"{payment.price:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{payment.total:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(payment.category))

        session.close()
