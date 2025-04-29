from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDateEdit, QComboBox, QMessageBox, QLineEdit, QTabWidget
)
from PyQt5.QtCore import Qt, QDate
import datetime
from typing import Dict

class MainWindow(QMainWindow):
    def __init__(self, hotel):
        super().__init__()
        self.hotel = hotel
        self.setWindowTitle("Админ-панель отеля")
        self.setGeometry(100, 100, 1000, 600)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        self.create_tabs()
        self.load_data()
    
    def create_tabs(self):
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Вкладка бронирований
        self.bookings_tab = QWidget()
        self.tabs.addTab(self.bookings_tab, "Бронирования")
        self.setup_bookings_tab()
        
        # Вкладка гостей
        self.guests_tab = QWidget()
        self.tabs.addTab(self.guests_tab, "Гости")
        self.setup_guests_tab()
        
        # Вкладка капсул
        self.capsules_tab = QWidget()
        self.tabs.addTab(self.capsules_tab, "Капсулы")
        self.setup_capsules_tab()
    
    def setup_bookings_tab(self):
        layout = QVBoxLayout()
        self.bookings_tab.setLayout(layout)
        
        # Фильтры
        filter_layout = QHBoxLayout()
        
        self.date_filter = QComboBox()
        self.date_filter.addItems(["Все", "Сегодня", "Завтра", "На этой неделе", "В этом месяце"])
        self.date_filter.currentIndexChanged.connect(self.load_bookings)
        filter_layout.addWidget(QLabel("Период:"))
        filter_layout.addWidget(self.date_filter)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Все", "Активные", "Завершенные", "Оплаченные", "Неоплаченные"])
        self.status_filter.currentIndexChanged.connect(self.load_bookings)
        filter_layout.addWidget(QLabel("Статус:"))
        filter_layout.addWidget(self.status_filter)
        
        layout.addLayout(filter_layout)
        
        # Таблица бронирований
        self.bookings_table = QTableWidget()
        self.bookings_table.setColumnCount(7)
        self.bookings_table.setHorizontalHeaderLabels([
            "ID", "Гость", "Капсула", "Дата заезда", "Дата выезда", 
            "Сумма", "Статус оплаты"
        ])
        self.bookings_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.bookings_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.bookings_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.bookings_table.doubleClicked.connect(self.show_booking_details)
        layout.addWidget(self.bookings_table)
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self.load_bookings)
        button_layout.addWidget(self.refresh_btn)
        
        self.mark_paid_btn = QPushButton("Отметить как оплаченное")
        self.mark_paid_btn.clicked.connect(self.mark_as_paid)
        button_layout.addWidget(self.mark_paid_btn)
        
        self.cancel_btn = QPushButton("Отменить бронирование")
        self.cancel_btn.clicked.connect(self.cancel_booking)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def setup_guests_tab(self):
        layout = QVBoxLayout()
        self.guests_tab.setLayout(layout)
        
        # Поиск
        search_layout = QHBoxLayout()
        self.guest_search = QLineEdit()
        self.guest_search.setPlaceholderText("Поиск по имени или паспорту...")
        self.guest_search.textChanged.connect(self.load_guests)
        search_layout.addWidget(self.guest_search)
        layout.addLayout(search_layout)
        
        # Таблица гостей
        self.guests_table = QTableWidget()
        self.guests_table.setColumnCount(4)
        self.guests_table.setHorizontalHeaderLabels([
            "ID", "Имя", "Паспорт", "Телефон"
        ])
        self.guests_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.guests_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.guests_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.guests_table.doubleClicked.connect(self.show_guest_details)
        layout.addWidget(self.guests_table)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        self.add_guest_btn = QPushButton("Добавить гостя")
        self.add_guest_btn.clicked.connect(self.add_guest)
        button_layout.addWidget(self.add_guest_btn)
        
        self.refresh_guests_btn = QPushButton("Обновить")
        self.refresh_guests_btn.clicked.connect(self.load_guests)
        button_layout.addWidget(self.refresh_guests_btn)
        
        layout.addLayout(button_layout)
    
    def setup_capsules_tab(self):
        layout = QVBoxLayout()
        self.capsules_tab.setLayout(layout)
        
        # Фильтры
        filter_layout = QHBoxLayout()
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Все", "Стандарт", "Люкс", "Премиум"])
        self.type_filter.currentIndexChanged.connect(self.load_capsules)
        filter_layout.addWidget(QLabel("Тип:"))
        filter_layout.addWidget(self.type_filter)
        
        self.availability_filter = QComboBox()
        self.availability_filter.addItems(["Все", "Доступные", "Занятые"])
        self.availability_filter.currentIndexChanged.connect(self.load_capsules)
        filter_layout.addWidget(QLabel("Доступность:"))
        filter_layout.addWidget(self.availability_filter)
        
        layout.addLayout(filter_layout)
        
        # Таблица капсул
        self.capsules_table = QTableWidget()
        self.capsules_table.setColumnCount(5)
        self.capsules_table.setHorizontalHeaderLabels([
            "ID", "Тип", "Цена за ночь", "Доступность", "Текущее бронирование"
        ])
        self.capsules_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.capsules_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.capsules_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.capsules_table.doubleClicked.connect(self.show_capsule_details)
        layout.addWidget(self.capsules_table)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        self.add_capsule_btn = QPushButton("Добавить капсулу")
        self.add_capsule_btn.clicked.connect(self.add_capsule)
        button_layout.addWidget(self.add_capsule_btn)
        
        self.refresh_capsules_btn = QPushButton("Обновить")
        self.refresh_capsules_btn.clicked.connect(self.load_capsules)
        button_layout.addWidget(self.refresh_capsules_btn)
        
        layout.addLayout(button_layout)
    
    def load_data(self):
        self.load_bookings()
        self.load_guests()
        self.load_capsules()
    
    def load_bookings(self):
        self.bookings_table.setRowCount(0)
        
        date_filter = self.date_filter.currentText()
        status_filter = self.status_filter.currentText()
        today = datetime.date.today()
        
        for booking in sorted(self.hotel.bookings.values(), key=lambda b: b.start_date):
            # Фильтрация по дате
            if date_filter == "Сегодня" and booking.start_date != today:
                continue
            if date_filter == "Завтра" and booking.start_date != today + datetime.timedelta(days=1):
                continue
            if date_filter == "На этой неделе" and (booking.start_date < today or booking.start_date > today + datetime.timedelta(days=7)):
                continue
            if date_filter == "В этом месяце" and (booking.start_date < today or booking.start_date.month != today.month):
                continue
            
            # Фильтрация по статусу
            if status_filter == "Активные" and (booking.end_date < today or booking.start_date > today):
                continue
            if status_filter == "Завершенные" and booking.end_date >= today:
                continue
            if status_filter == "Оплаченные" and not booking.is_paid:
                continue
            if status_filter == "Неоплаченные" and booking.is_paid:
                continue
            
            row = self.bookings_table.rowCount()
            self.bookings_table.insertRow(row)
            
            self.bookings_table.setItem(row, 0, QTableWidgetItem(str(booking.booking_id)))
            self.bookings_table.setItem(row, 1, QTableWidgetItem(booking.guest.name))
            self.bookings_table.setItem(row, 2, QTableWidgetItem(f"{booking.capsule.type} (#{booking.capsule.capsule_id})"))
            self.bookings_table.setItem(row, 3, QTableWidgetItem(booking.start_date.strftime("%d.%m.%Y")))
            self.bookings_table.setItem(row, 4, QTableWidgetItem(booking.end_date.strftime("%d.%m.%Y")))
            self.bookings_table.setItem(row, 5, QTableWidgetItem(f"{booking.calculate_total():.2f} руб."))
            self.bookings_table.setItem(row, 6, QTableWidgetItem("Оплачено" if booking.is_paid else "Не оплачено"))
    
    def load_guests(self):
        self.guests_table.setRowCount(0)
        search_text = self.guest_search.text().lower()
        
        for guest in sorted(self.hotel.guests.values(), key=lambda g: g.guest_id):
            if (search_text in guest.name.lower() or 
                search_text in guest.passport.lower() or 
                search_text in guest.phone.lower() or 
                not search_text):
                
                row = self.guests_table.rowCount()
                self.guests_table.insertRow(row)
                
                self.guests_table.setItem(row, 0, QTableWidgetItem(str(guest.guest_id)))
                self.guests_table.setItem(row, 1, QTableWidgetItem(guest.name))
                self.guests_table.setItem(row, 2, QTableWidgetItem(guest.passport))
                self.guests_table.setItem(row, 3, QTableWidgetItem(guest.phone))
    
    def load_capsules(self):
        self.capsules_table.setRowCount(0)
        
        type_filter = self.type_filter.currentText()
        availability_filter = self.availability_filter.currentText()
        
        for capsule in sorted(self.hotel.capsules.values(), key=lambda c: c.capsule_id):
            # Фильтрация по типу
            if type_filter != "Все" and capsule.type != type_filter:
                continue
                
            # Фильтрация по доступности
            if availability_filter == "Доступные" and not capsule.is_available:
                continue
            if availability_filter == "Занятые" and capsule.is_available:
                continue
            
            row = self.capsules_table.rowCount()
            self.capsules_table.insertRow(row)
            
            self.capsules_table.setItem(row, 0, QTableWidgetItem(str(capsule.capsule_id)))
            self.capsules_table.setItem(row, 1, QTableWidgetItem(capsule.type))
            self.capsules_table.setItem(row, 2, QTableWidgetItem(f"{capsule.price_per_night:.2f} руб."))
            self.capsules_table.setItem(row, 3, QTableWidgetItem("Доступна" if capsule.is_available else "Занята"))
            
            booking_info = ""
            if capsule.current_booking:
                booking = capsule.current_booking
                booking_info = f"Гость: {booking.guest.name} ({booking.start_date} - {booking.end_date})"
            self.capsules_table.setItem(row, 4, QTableWidgetItem(booking_info))
    
    def show_booking_details(self):
        selected = self.bookings_table.selectedItems()
        if not selected:
            return
        
        booking_id = int(selected[0].text())
        booking = self.hotel.bookings.get(booking_id)
        if not booking:
            return
        
        details = (
            f"Бронирование #{booking.booking_id}\n\n"
            f"Гость: {booking.guest.name} (ID: {booking.guest.guest_id})\n"
            f"Паспорт: {booking.guest.passport}\n"
            f"Телефон: {booking.guest.phone}\n\n"
            f"Капсула: {booking.capsule.type} (ID: {booking.capsule.capsule_id})\n"
            f"Цена за ночь: {booking.capsule.price_per_night:.2f} руб.\n\n"
            f"Дата заезда: {booking.start_date.strftime('%d.%m.%Y')}\n"
            f"Дата выезда: {booking.end_date.strftime('%d.%m.%Y')}\n"
            f"Количество ночей: {(booking.end_date - booking.start_date).days}\n\n"
            f"Общая сумма: {booking.calculate_total():.2f} руб.\n"
            f"Статус оплаты: {'Оплачено' if booking.is_paid else 'Не оплачено'}"
        )
        
        QMessageBox.information(self, "Детали бронирования", details)
    
    def show_guest_details(self):
        selected = self.guests_table.selectedItems()
        if not selected:
            return
        
        guest_id = int(selected[0].text())
        guest = self.hotel.guests.get(guest_id)
        if not guest:
            return
        
        active_bookings = [b for b in guest.bookings if b.end_date >= datetime.date.today()]
        
        details = (
            f"Гость #{guest.guest_id}\n\n"
            f"Имя: {guest.name}\n"
            f"Паспорт: {guest.passport}\n"
            f"Телефон: {guest.phone}\n\n"
            f"Активных бронирований: {len(active_bookings)}\n"
        )
        
        if active_bookings:
            details += "\nАктивные бронирования:\n"
            for booking in active_bookings:
                details += (
                    f"- Бронь #{booking.booking_id}: "
                    f"{booking.capsule.type} (с {booking.start_date} по {booking.end_date})\n"
                )
        
        QMessageBox.information(self, "Детали гостя", details)
    
    def show_capsule_details(self):
        selected = self.capsules_table.selectedItems()
        if not selected:
            return
        
        capsule_id = int(selected[0].text())
        capsule = self.hotel.capsules.get(capsule_id)
        if not capsule:
            return
        
        details = (
            f"Капсула #{capsule.capsule_id}\n\n"
            f"Тип: {capsule.type}\n"
            f"Цена за ночь: {capsule.price_per_night:.2f} руб.\n"
            f"Статус: {'Доступна' if capsule.is_available else 'Занята'}\n"
        )
        
        if capsule.current_booking:
            booking = capsule.current_booking
            details += (
                f"\nТекущее бронирование:\n"
                f"ID: {booking.booking_id}\n"
                f"Гость: {booking.guest.name} (ID: {booking.guest.guest_id})\n"
                f"Период: {booking.start_date} - {booking.end_date}\n"
                f"Статус оплаты: {'Оплачено' if booking.is_paid else 'Не оплачено'}"
            )
        
        QMessageBox.information(self, "Детали капсулы", details)
    
    def mark_as_paid(self):
        selected = self.bookings_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите бронирование")
            return
        
        booking_id = int(selected[0].text())
        booking = self.hotel.bookings.get(booking_id)
        if not booking:
            return
        
        if booking.is_paid:
            QMessageBox.information(self, "Информация", "Бронирование уже оплачено")
            return
        
        booking.mark_as_paid()
        booking.save_to_db()
        self.load_bookings()
        QMessageBox.information(self, "Успех", "Бронирование отмечено как оплаченное")
    
    def cancel_booking(self):
        selected = self.bookings_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите бронирование")
            return
        
        booking_id = int(selected[0].text())
        booking = self.hotel.bookings.get(booking_id)
        if not booking:
            return
        
        if booking.is_paid:
            QMessageBox.warning(self, "Ошибка", "Нельзя отменить оплаченное бронирование")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение", 
            f"Вы уверены, что хотите отменить бронирование #{booking_id}?", 
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                booking.cancel()
                del self.hotel.bookings[booking_id]
                self.load_bookings()
                QMessageBox.information(self, "Успех", "Бронирование отменено")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось отменить бронирование: {str(e)}")
    
    def add_guest(self):
        # Реализация добавления нового гостя
        pass
    
    def add_capsule(self):
        # Реализация добавления новой капсулы
        pass