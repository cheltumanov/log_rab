import os
import datetime
from typing import Dict, List, Optional, Deque, Set
from collections import deque, defaultdict
from abc import ABC, abstractmethod
import telebot
from telebot import types
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Инициализация бота
bot = telebot.TeleBot(API_TOKEN)

# Классы предметной области
class Entity(ABC):
    """Абстрактный базовый класс для всех сущностей"""
    @abstractmethod
    def display_info(self) -> str:
        """Абстрактный метод для отображения информации о сущности"""
        pass


class Guest(Entity):
    """Класс для представления гостя отеля"""
    _used_passports: Set[str] = set()
    
    def __init__(self, guest_id: int, name: str, passport: str, phone: str):
        self.guest_id = guest_id
        self.name = name
        self.passport = passport
        self.phone = phone
        self.bookings: List['Booking'] = []
        
        if passport in Guest._used_passports:
            raise ValueError("Гость с таким паспортом уже зарегистрирован")
        Guest._used_passports.add(passport)
    
    def add_booking(self, booking: 'Booking'):
        self.bookings.append(booking)
    
    def remove_booking(self, booking: 'Booking'):
        self.bookings.remove(booking)
    
    def get_active_bookings(self) -> List['Booking']:
        today = datetime.date.today()
        return [b for b in self.bookings if b.end_date >= today]
    
    def display_info(self) -> str:
        return (f"🏷 Гость #{self.guest_id}\n"
                f"👤 Имя: {self.name}\n"
                f"📄 Паспорт: {self.passport}\n"
                f"📞 Телефон: {self.phone}\n"
                f"🔢 Активных броней: {len(self.get_active_bookings())}")
    
    def __str__(self):
        return f"👤 #{self.guest_id} {self.name}"


class Capsule(Entity):
    """Класс для представления капсулы в отеле"""
    TYPE_STANDARD = "Стандарт"
    TYPE_LUX = "Люкс"
    TYPE_PREMIUM = "Премиум"
    
    BASE_PRICES = {
        TYPE_STANDARD: 1500,
        TYPE_LUX: 2500,
        TYPE_PREMIUM: 3500
    }
    
    def __init__(self, capsule_id: int, capsule_type: str):
        self.capsule_id = capsule_id
        self.type = capsule_type
        self.price_per_night = self._calculate_price()
        self.is_available = True
        self.current_booking: Optional['Booking'] = None
    
    def _calculate_price(self) -> float:
        base_price = self.BASE_PRICES.get(self.type, 1000)
        import random
        return base_price * (1 + random.uniform(-0.1, 0.1))
    
    @staticmethod
    def get_available_types() -> List[str]:
        return list(Capsule.BASE_PRICES.keys())
    
    def book(self, booking: 'Booking'):
        if not self.is_available:
            raise ValueError("Капсула уже занята")
        self.is_available = False
        self.current_booking = booking
    
    def release(self):
        self.is_available = True
        self.current_booking = None
    
    def display_info(self) -> str:
        status = "🟢 Доступна" if self.is_available else "🔴 Занята"
        return (f"🚪 Капсула #{self.capsule_id}\n"
                f"🏷 Тип: {self.type}\n"
                f"💰 Цена за ночь: {self.price_per_night:.2f} руб.\n"
                f"📌 Статус: {status}")
    
    def __str__(self):
        status = "🟢" if self.is_available else "🔴"
        return f"{status} Капсула #{self.capsule_id} ({self.type}) - {self.price_per_night:.2f} руб./ночь"


class Booking(Entity):
    """Класс для представления бронирования"""
    _booking_history: Deque['Booking'] = deque(maxlen=1000)
    
    def __init__(self, booking_id: int, guest: Guest, capsule: Capsule, 
                 start_date: datetime.date, end_date: datetime.date):
        if start_date >= end_date:
            raise ValueError("Дата выезда должна быть позже даты заезда")
        
        self.booking_id = booking_id
        self.guest = guest
        self.capsule = capsule
        self.start_date = start_date
        self.end_date = end_date
        self.is_paid = False
        self._validate_dates()
        
        self.capsule.book(self)
        self.guest.add_booking(self)
        Booking._booking_history.append(self)
    
    def _validate_dates(self):
        today = datetime.date.today()
        if self.start_date < today:
            raise ValueError("Дата заезда не может быть в прошлом")
        if (self.end_date - self.start_date).days > 30:
            raise ValueError("Максимальный срок бронирования - 30 дней")
    
    @classmethod
    def get_recent_bookings(cls, count: int = 5) -> List['Booking']:
        return list(cls._booking_history)[-count:]
    
    def calculate_total(self) -> float:
        nights = (self.end_date - self.start_date).days
        return nights * self.capsule.price_per_night
    
    def mark_as_paid(self):
        self.is_paid = True
    
    def cancel(self):
        self.capsule.release()
        self.guest.remove_booking(self)
    
    def display_info(self) -> str:
        paid_status = "✅ Оплачено" if self.is_paid else "❌ Не оплачено"
        return (f"📝 Бронирование #{self.booking_id}\n"
                f"👤 Гость: {self.guest.name} (#{self.guest.guest_id})\n"
                f"🚪 Капсула: {self.capsule.type} (#{self.capsule.capsule_id})\n"
                f"📅 Период: {self.start_date} - {self.end_date}\n"
                f"💰 Сумма: {self.calculate_total():.2f} руб.\n"
                f"📌 Статус оплаты: {paid_status}")
    
    def __str__(self):
        paid_status = "✅" if self.is_paid else "❌"
        return (f"{paid_status} Бронь #{self.booking_id}: {self.guest.name} "
                f"в капсуле #{self.capsule.capsule_id} ({self.start_date} - {self.end_date})")


class Hotel:
    """Класс для представления отеля"""
    def __init__(self, name: str):
        self.name = name
        self.guests: Dict[int, Guest] = {}
        self.capsules: Dict[int, Capsule] = {}
        self.bookings: Dict[int, Booking] = {}
        self._next_guest_id = 1
        self._next_capsule_id = 1
        self._next_booking_id = 1
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        for _ in range(3):
            self.add_capsule(Capsule.TYPE_STANDARD)
        for _ in range(2):
            self.add_capsule(Capsule.TYPE_LUX)
        self.add_capsule(Capsule.TYPE_PREMIUM)
        
        self.register_guest("Иван Иванов", "1234567890", "+79123456789")
        self.register_guest("Петр Петров", "0987654321", "+79098765432")
    
    def add_capsule(self, capsule_type: str) -> Capsule:
        capsule = Capsule(self._next_capsule_id, capsule_type)
        self.capsules[self._next_capsule_id] = capsule
        self._next_capsule_id += 1
        return capsule
    
    def register_guest(self, name: str, passport: str, phone: str) -> Guest:
        name = ' '.join(part.capitalize() for part in name.split())
        
        guest = Guest(self._next_guest_id, name, passport, phone)
        self.guests[self._next_guest_id] = guest
        self._next_guest_id += 1
        return guest
    
    def create_booking(self, guest_id: int, capsule_id: int, 
                      start_date: datetime.date, end_date: datetime.date) -> Booking:
        if guest_id not in self.guests:
            raise ValueError("Гость не найден")
        if capsule_id not in self.capsules:
            raise ValueError("Капсула не найдена")
        
        guest = self.guests[guest_id]
        capsule = self.capsules[capsule_id]
        
        booking = Booking(self._next_booking_id, guest, capsule, start_date, end_date)
        self.bookings[self._next_booking_id] = booking
        self._next_booking_id += 1
        return booking
    
    def get_available_capsules(self, date: Optional[datetime.date] = None) -> List[Capsule]:
        if date is None:
            date = datetime.date.today()
        
        available = []
        for capsule in self.capsules.values():
            if capsule.is_available or (capsule.current_booking and 
                                       not (capsule.current_booking.start_date <= date <= capsule.current_booking.end_date)):
                available.append(capsule)
        return available
    
    def check_out(self, booking_id: int):
        if booking_id not in self.bookings:
            raise ValueError("Бронирование не найдено")
        
        booking = self.bookings[booking_id]
        booking.cancel()
        del self.bookings[booking_id]
    
    def get_guest_statistics(self) -> Dict[str, float]:
        stats = defaultdict(float)
        for booking in self.bookings.values():
            stats[booking.guest.name] += booking.calculate_total()
        return stats


# Инициализация отеля
hotel = Hotel("Капсульный отель 'Космос'")

# Состояния для FSM (имитация)
user_states = {}

# Обработчики команд
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(
        message,
        "🏨 Добро пожаловать в систему управления капсульным отелем!\n\n"
        "Доступные команды:\n"
        "/guests - Список гостей\n"
        "/register - Зарегистрировать нового гостя\n"
        "/capsules - Список капсул\n"
        "/book - Создать бронирование\n"
        "/bookings - Список бронирований\n"
        "/checkout - Выселить гостя\n"
        "/stats - Статистика по гостям\n"
        "/recent - Последние бронирования"
    )


@bot.message_handler(commands=['guests'])
def list_guests(message):
    if not hotel.guests:
        bot.reply_to(message, "В отеле пока нет гостей.")
        return
    
    response = "📋 Список гостей:\n\n"
    for guest in sorted(hotel.guests.values(), key=lambda g: g.guest_id):
        response += f"{guest}\n{guest.display_info()}\n\n"
    
    bot.reply_to(message, response)


@bot.message_handler(commands=['register'])
def register_guest_start(message):
    msg = bot.reply_to(message, "Введите ФИО нового гостя:")
    bot.register_next_step_handler(msg, process_guest_name)


def process_guest_name(message):
    try:
        user_states[message.chat.id] = {'name': message.text}
        msg = bot.reply_to(message, "Введите паспортные данные гостя:")
        bot.register_next_step_handler(msg, process_guest_passport)
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")


def process_guest_passport(message):
    try:
        user_states[message.chat.id]['passport'] = message.text
        msg = bot.reply_to(message, "Введите телефон гостя:")
        bot.register_next_step_handler(msg, process_guest_phone)
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")


def process_guest_phone(message):
    try:
        data = user_states[message.chat.id]
        data['phone'] = message.text
        
        guest = hotel.register_guest(data['name'], data['passport'], data['phone'])
        bot.reply_to(message, f"✅ Гость успешно зарегистрирован:\n{guest.display_info()}")
        del user_states[message.chat.id]
    except ValueError as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")
    except Exception as e:
        bot.reply_to(message, f"❌ Неизвестная ошибка: {e}")


@bot.message_handler(commands=['capsules'])
def list_capsules(message):
    if not hotel.capsules:
        bot.reply_to(message, "В отеле пока нет капсул.")
        return
    
    response = "🚪 Список капсул:\n\n"
    for capsule in sorted(hotel.capsules.values(), key=lambda c: c.capsule_id):
        response += f"{capsule}\n{capsule.display_info()}\n\n"
    
    bot.reply_to(message, response)


@bot.message_handler(commands=['book'])
def book_start(message):
    if not hotel.guests:
        bot.reply_to(message, "Для бронирования сначала зарегистрируйте гостя.")
        return
    
    guests_list = "👥 Выберите гостя (введите ID):\n\n"
    for guest in hotel.guests.values():
        guests_list += f"{guest.guest_id}. {guest.name}\n"
    
    msg = bot.reply_to(message, guests_list)
    bot.register_next_step_handler(msg, process_booking_guest)


def process_booking_guest(message):
    try:
        guest_id = int(message.text)
        if guest_id not in hotel.guests:
            bot.reply_to(message, "❌ Неверный ID гостя. Попробуйте снова.")
            return
        
        user_states[message.chat.id] = {'guest_id': guest_id}
        
        available = hotel.get_available_capsules()
        if not available:
            bot.reply_to(message, "❌ Нет доступных капсул для бронирования.")
            return
        
        capsules_list = "🚪 Выберите капсулу (введите ID):\n\n"
        for capsule in available:
            capsules_list += f"{capsule.capsule_id}. {capsule.type} - {capsule.price_per_night:.2f} руб./ночь\n"
        
        msg = bot.reply_to(message, capsules_list)
        bot.register_next_step_handler(msg, process_booking_capsule)
    except ValueError:
        bot.reply_to(message, "❌ Пожалуйста, введите числовой ID гостя.")


def process_booking_capsule(message):
    try:
        capsule_id = int(message.text)
        if capsule_id not in hotel.capsules:
            bot.reply_to(message, "❌ Неверный ID капсулы. Попробуйте снова.")
            return
        
        user_states[message.chat.id]['capsule_id'] = capsule_id
        msg = bot.reply_to(message, "📅 Введите дату заезда (в формате ГГГГ-ММ-ДД):")
        bot.register_next_step_handler(msg, process_booking_start_date)
    except ValueError:
        bot.reply_to(message, "❌ Пожалуйста, введите числовой ID капсулы.")


def process_booking_start_date(message):
    try:
        start_date = datetime.date.fromisoformat(message.text)
        today = datetime.date.today()
        
        if start_date < today:
            bot.reply_to(message, "❌ Дата заезда не может быть в прошлом. Попробуйте снова.")
            return
        
        user_states[message.chat.id]['start_date'] = start_date
        msg = bot.reply_to(message, "📅 Введите дату выезда (в формате ГГГГ-ММ-ДД):")
        bot.register_next_step_handler(msg, process_booking_end_date)
    except ValueError:
        bot.reply_to(message, "❌ Неверный формат даты. Используйте ГГГГ-ММ-ДД.")


def process_booking_end_date(message):
    try:
        end_date = datetime.date.fromisoformat(message.text)
        data = user_states[message.chat.id]
        start_date = data['start_date']
        
        if end_date <= start_date:
            bot.reply_to(message, "❌ Дата выезда должна быть позже даты заезда. Попробуйте снова.")
            return
        
        if (end_date - start_date).days > 30:
            bot.reply_to(message, "❌ Максимальный срок бронирования - 30 дней. Попробуйте снова.")
            return
        
        try:
            booking = hotel.create_booking(
                data['guest_id'],
                data['capsule_id'],
                start_date,
                end_date
            )
            bot.reply_to(message, f"✅ Бронирование успешно создано!\n{booking.display_info()}")
            del user_states[message.chat.id]
        except ValueError as e:
            bot.reply_to(message, f"❌ Ошибка при создании бронирования: {e}")
    
    except ValueError:
        bot.reply_to(message, "❌ Неверный формат даты. Используйте ГГГГ-ММ-ДД.")


@bot.message_handler(commands=['bookings'])
def list_bookings(message):
    if not hotel.bookings:
        bot.reply_to(message, "Нет активных бронирований.")
        return
    
    response = "📋 Список бронирований:\n\n"
    for booking in sorted(hotel.bookings.values(), key=lambda b: b.booking_id):
        response += f"{booking}\n{booking.display_info()}\n\n"
    
    bot.reply_to(message, response)


@bot.message_handler(commands=['checkout'])
def checkout_start(message):
    if not hotel.bookings:
        bot.reply_to(message, "Нет активных бронирований для выселения.")
        return
    
    bookings_list = "📋 Выберите бронирование для выселения (введите ID):\n\n"
    for booking in hotel.bookings.values():
        bookings_list += f"{booking.booking_id}. {booking.guest.name} - Капсула #{booking.capsule.capsule_id}\n"
    
    msg = bot.reply_to(message, bookings_list)
    bot.register_next_step_handler(msg, process_check_out)


def process_check_out(message):
    try:
        booking_id = int(message.text)
        
        try:
            hotel.check_out(booking_id)
            bot.reply_to(message, f"✅ Гость успешно выселен, капсула освобождена.")
        except ValueError as e:
            bot.reply_to(message, f"❌ Ошибка: {e}")
    
    except ValueError:
        bot.reply_to(message, "❌ Пожалуйста, введите числовой ID бронирования.")


@bot.message_handler(commands=['stats'])
def show_stats(message):
    stats = hotel.get_guest_statistics()
    if not stats:
        bot.reply_to(message, "Нет данных для статистики.")
        return
    
    response = "📊 Статистика по гостям (общая сумма бронирований):\n\n"
    for name, total in sorted(stats.items(), key=lambda item: item[1], reverse=True):
        response += f"👤 {name}: {total:.2f} руб.\n"
    
    bot.reply_to(message, response)


@bot.message_handler(commands=['recent'])
def show_recent_bookings(message):
    recent = Booking.get_recent_bookings()
    if not recent:
        bot.reply_to(message, "Нет данных о последних бронированиях.")
        return
    
    response = "⏳ Последние бронирования:\n\n"
    for booking in recent:
        response += f"{booking}\n{booking.display_info()}\n\n"
    
    bot.reply_to(message, response)


# Запуск бота
if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()