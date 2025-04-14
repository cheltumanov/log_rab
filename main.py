import datetime
from typing import List, Dict, Optional, Set, Deque
from collections import deque, defaultdict
from abc import ABC, abstractmethod


class Entity(ABC):
    """Абстрактный базовый класс для всех сущностей"""
    @abstractmethod
    def display_info(self):
        """Абстрактный метод для отображения информации о сущности"""
        pass


class Guest(Entity):
    """Класс для представления гостя отеля"""
    # Статическое поле для хранения всех использованных паспортных данных
    _used_passports: Set[str] = set()
    
    def __init__(self, guest_id: int, name: str, passport: str, phone: str):
        self.guest_id = guest_id
        self.name = name
        self.passport = passport
        self.phone = phone
        self.bookings: List['Booking'] = []
        
        # Проверка уникальности паспорта
        if passport in Guest._used_passports:
            raise ValueError("Гость с таким паспортом уже зарегистрирован")
        Guest._used_passports.add(passport)
    
    def add_booking(self, booking: 'Booking'):
        """Добавить бронирование для гостя"""
        self.bookings.append(booking)
    
    def remove_booking(self, booking: 'Booking'):
        """Удалить бронирование гостя"""
        self.bookings.remove(booking)
    
    def get_active_bookings(self) -> List['Booking']:
        """Получить активные бронирования"""
        today = datetime.date.today()
        return [b for b in self.bookings if b.end_date >= today]
    
    def display_info(self):
        """Реализация абстрактного метода"""
        print(f"Гость #{self.guest_id}: {self.name}, паспорт: {self.passport}, телефон: {self.phone}")
    
    def __str__(self):
        return f"Гость #{self.guest_id}: {self.name}"
    
    def __eq__(self, other):
        """Перегрузка оператора равенства"""
        if not isinstance(other, Guest):
            return False
        return self.passport == other.passport
    
    def __lt__(self, other):
        """Перегрузка оператора меньше (для сортировки)"""
        return self.name < other.name
    
    def __add__(self, nights: int):
        """Перегрузка оператора + для добавления дней к последнему бронированию"""
        if not self.bookings:
            raise ValueError("У гостя нет бронирований")
        last_booking = self.bookings[-1]
        last_booking.end_date += datetime.timedelta(days=nights)
        return self


class Capsule(Entity):
    """Класс для представления капсулы в отеле"""
    # Статические поля для типов капсул и их базовых цен
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
        """Рассчитать цену с учетом типа капсулы"""
        base_price = self.BASE_PRICES.get(self.type, 1000)
        # Добавляем случайное отклонение до 10% для динамического ценообразования
        import random
        return base_price * (1 + random.uniform(-0.1, 0.1))
    
    @staticmethod
    def get_available_types() -> List[str]:
        """Статический метод для получения доступных типов капсул"""
        return list(Capsule.BASE_PRICES.keys())
    
    def book(self, booking: 'Booking'):
        """Забронировать капсулу"""
        if not self.is_available:
            raise ValueError("Капсула уже занята")
        self.is_available = False
        self.current_booking = booking
    
    def release(self):
        """Освободить капсулу"""
        self.is_available = True
        self.current_booking = None
    
    def display_info(self):
        """Реализация абстрактного метода"""
        status = "доступна" if self.is_available else "занята"
        print(f"Капсула #{self.capsule_id} ({self.type}), {status}, цена за ночь: {self.price_per_night:.2f}")
    
    def __str__(self):
        status = "доступна" if self.is_available else "занята"
        return f"Капсула #{self.capsule_id} ({self.type}), {status}"
    
    def __eq__(self, other):
        """Перегрузка оператора равенства"""
        if not isinstance(other, Capsule):
            return False
        return self.capsule_id == other.capsule_id
    
    def __lt__(self, other):
        """Перегрузка оператора меньше (для сортировки)"""
        return self.price_per_night < other.price_per_night
    
    def __contains__(self, date: datetime.date):
        """Перегрузка оператора in для проверки доступности на дату"""
        if self.is_available:
            return True
        return not (self.current_booking.start_date <= date <= self.current_booking.end_date)


class Booking(Entity):
    """Класс для представления бронирования"""
    # Статическое поле для хранения истории всех бронирований
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
        """Проверка корректности дат"""
        today = datetime.date.today()
        if self.start_date < today:
            raise ValueError("Дата заезда не может быть в прошлом")
        if (self.end_date - self.start_date).days > 30:
            raise ValueError("Максимальный срок бронирования - 30 дней")
    
    @classmethod
    def get_recent_bookings(cls, count: int = 5) -> List['Booking']:
        """Получить последние бронирования"""
        return list(cls._booking_history)[-count:]
    
    def calculate_total(self) -> float:
        """Рассчитать общую стоимость бронирования"""
        nights = (self.end_date - self.start_date).days
        return nights * self.capsule.price_per_night
    
    def mark_as_paid(self):
        """Пометить бронирование как оплаченное"""
        self.is_paid = True
    
    def cancel(self):
        """Отменить бронирование"""
        self.capsule.release()
        self.guest.remove_booking(self)
    
    def display_info(self):
        """Реализация абстрактного метода"""
        paid_status = "оплачено" if self.is_paid else "не оплачено"
        print(f"Бронирование #{self.booking_id}:")
        print(f"Гость: {self.guest.name}")
        print(f"Капсула: {self.capsule.type} (#{self.capsule.capsule_id})")
        print(f"Период: {self.start_date} - {self.end_date}")
        print(f"Статус оплаты: {paid_status}")
        print(f"Общая стоимость: {self.calculate_total():.2f} руб.")
    
    def __str__(self):
        paid_status = "оплачено" if self.is_paid else "не оплачено"
        return (f"Бронирование #{self.booking_id}: {self.guest.name} в капсуле #{self.capsule.capsule_id} "
                f"с {self.start_date} по {self.end_date}, {paid_status}")
    
    def __eq__(self, other):
        """Перегрузка оператора равенства"""
        if not isinstance(other, Booking):
            return False
        return (self.guest == other.guest and 
                self.capsule == other.capsule and 
                self.start_date == other.start_date)
    
    def __lt__(self, other):
        """Перегрузка оператора меньше (для сортировки)"""
        return self.start_date < other.start_date
    
    def __add__(self, days: int):
        """Перегрузка оператора + для продления бронирования"""
        self.end_date += datetime.timedelta(days=days)
        return self


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
        """Инициализировать тестовые данные"""
        # Добавляем капсулы разных типов
        for _ in range(3):
            self.add_capsule(Capsule.TYPE_STANDARD)
        for _ in range(2):
            self.add_capsule(Capsule.TYPE_LUX)
        self.add_capsule(Capsule.TYPE_PREMIUM)
        
        # Регистрируем гостей
        self.register_guest("Иван Иванов", "1234567890", "+79123456789")
        self.register_guest("Петр Петров", "0987654321", "+79098765432")
    
    def add_capsule(self, capsule_type: str) -> Capsule:
        """Добавить капсулу в отель"""
        capsule = Capsule(self._next_capsule_id, capsule_type)
        self.capsules[self._next_capsule_id] = capsule
        self._next_capsule_id += 1
        return capsule
    
    def register_guest(self, name: str, passport: str, phone: str) -> Guest:
        """Зарегистрировать гостя"""
        # Обработка строк - нормализация имени
        name = ' '.join(part.capitalize() for part in name.split())
        
        guest = Guest(self._next_guest_id, name, passport, phone)
        self.guests[self._next_guest_id] = guest
        self._next_guest_id += 1
        return guest
    
    def create_booking(self, guest_id: int, capsule_id: int, 
                      start_date: datetime.date, end_date: datetime.date) -> Booking:
        """Создать бронирование"""
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
        """Получить список доступных капсул на конкретную дату"""
        if date is None:
            date = datetime.date.today()
        
        available = []
        for capsule in self.capsules.values():
            if date in capsule:
                available.append(capsule)
        return available
    
    def check_out(self, booking_id: int):
        """Выселить гостя (освободить капсулу)"""
        if booking_id not in self.bookings:
            raise ValueError("Бронирование не найдено")
        
        booking = self.bookings[booking_id]
        booking.cancel()
        del self.bookings[booking_id]
    
    def get_guest_statistics(self) -> Dict[str, int]:
        """Получить статистику по гостям"""
        stats = defaultdict(int)
        for booking in self.bookings.values():
            stats[booking.guest.name] += booking.calculate_total()
        return stats
    
    def __str__(self):
        return (f"Отель '{self.name}': {len(self.guests)} гостей, "
                f"{len(self.capsules)} капсул, {len(self.bookings)} активных бронирований")
    
    def __contains__(self, guest_name: str):
        """Перегрузка оператора in для проверки наличия гостя"""
        return any(guest.name == guest_name for guest in self.guests.values())
    
    def __getitem__(self, key):
        """Перегрузка оператора [] для доступа к объектам"""
        if isinstance(key, int):
            if key in self.guests:
                return self.guests[key]
            if key in self.capsules:
                return self.capsules[key]
            if key in self.bookings:
                return self.bookings[key]
            raise KeyError("Объект с таким ID не найден")
        elif isinstance(key, str):
            # Поиск по имени гостя
            for guest in self.guests.values():
                if guest.name == key:
                    return guest
            raise KeyError("Гость с таким именем не найден")
        else:
            raise TypeError("Неверный тип ключа")


class HotelBot:
    """Класс для управления отелем через бота"""
    def __init__(self, hotel_name: str):
        self.hotel = Hotel(hotel_name)
    
    def show_menu(self):
        """Показать меню бота"""
        print("\nМеню управления капсульным отелем:")
        print("1. Показать все капсулы")
        print("2. Показать доступные капсулы")
        print("3. Зарегистрировать нового гостя")
        print("4. Создать бронирование")
        print("5. Показать все бронирования")
        print("6. Выселить гостя (освободить капсулу)")
        print("7. Показать информацию об отеле")
        print("8. Показать статистику по гостям")
        print("9. Показать последние бронирования")
        print("0. Выход")
    
    def run(self):
        """Запустить бота"""
        print(f"Добро пожаловать в систему управления отелем '{self.hotel.name}'!")
        
        while True:
            self.show_menu()
            choice = input("Выберите действие: ")
            
            try:
                if choice == "1":
                    self._show_all_capsules()
                elif choice == "2":
                    self._show_available_capsules()
                elif choice == "3":
                    self._register_guest()
                elif choice == "4":
                    self._create_booking()
                elif choice == "5":
                    self._show_all_bookings()
                elif choice == "6":
                    self._check_out()
                elif choice == "7":
                    print(self.hotel)
                elif choice == "8":
                    self._show_guest_statistics()
                elif choice == "9":
                    self._show_recent_bookings()
                elif choice == "0":
                    print("До свидания!")
                    break
                else:
                    print("Неверный выбор, попробуйте снова.")
            except ValueError as ve:
                print(f"Ошибка ввода данных: {ve}")
            except KeyError as ke:
                print(f"Ошибка поиска: {ke}")
            except Exception as e:
                print(f"Неожиданная ошибка: {e}")
    
    def _show_all_capsules(self):
        """Показать все капсулы"""
        print("\nВсе капсулы в отеле:")
        for capsule in sorted(self.hotel.capsules.values()):
            capsule.display_info()
    
    def _show_available_capsules(self):
        """Показать доступные капсулы"""
        date_str = input("Введите дату для проверки (ГГГГ-ММ-ДД) или оставьте пустым для сегодня: ")
        date = datetime.date.today() if not date_str else datetime.date.fromisoformat(date_str)
        
        available = self.hotel.get_available_capsules(date)
        print(f"\nДоступные капсулы на {date}:")
        for capsule in sorted(available):
            capsule.display_info()
    
    def _register_guest(self):
        """Зарегистрировать нового гостя"""
        print("\nРегистрация нового гостя:")
        name = input("ФИО: ").strip()
        passport = input("Паспортные данные: ").strip()
        phone = input("Телефон: ").strip()
        
        guest = self.hotel.register_guest(name, passport, phone)
        print(f"Гость успешно зарегистрирован: {guest}")
    
    def _create_booking(self):
        """Создать бронирование"""
        print("\nСоздание бронирования:")
        
        # Показать гостей
        print("Список гостей:")
        for guest in sorted(self.hotel.guests.values()):
            print(f"{guest.guest_id}. {guest.name}")
        
        guest_id = int(input("Введите ID гостя: "))
        
        # Показать доступные капсулы
        date_str = input("Введите дату заезда (ГГГГ-ММ-ДД): ")
        start_date = datetime.date.fromisoformat(date_str)
        
        available = self.hotel.get_available_capsules(start_date)
        print("Доступные капсулы на выбранную дату:")
        for capsule in sorted(available):
            print(f"{capsule.capsule_id}. {capsule.type} - {capsule.price_per_night:.2f} руб./ночь")
        
        capsule_id = int(input("Введите ID капсулы: "))
        
        # Ввод даты выезда
        end_date_str = input("Дата выезда (ГГГГ-ММ-ДД): ")
        end_date = datetime.date.fromisoformat(end_date_str)
        
        # Создание бронирования
        booking = self.hotel.create_booking(guest_id, capsule_id, start_date, end_date)
        print("\nБронирование создано:")
        booking.display_info()
    
    def _show_all_bookings(self):
        """Показать все бронирования"""
        print("\nВсе активные бронирования:")
        for booking in sorted(self.hotel.bookings.values()):
            booking.display_info()
            print()
    
    def _check_out(self):
        """Выселить гостя"""
        print("\nВыселение гостя:")
        self._show_all_bookings()
        
        booking_id = int(input("Введите ID бронирования для выселения: "))
        self.hotel.check_out(booking_id)
        print("Гость успешно выселен, капсула освобождена.")
    
    def _show_guest_statistics(self):
        """Показать статистику по гостям"""
        print("\nСтатистика по гостям (общая сумма бронирований):")
        stats = self.hotel.get_guest_statistics()
        for guest_name, total in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            print(f"{guest_name}: {total:.2f} руб.")
    
    def _show_recent_bookings(self):
        """Показать последние бронирования"""
        print("\nПоследние бронирования:")
        recent = Booking.get_recent_bookings()
        for booking in recent:
            booking.display_info()
            print()


def main():
    bot = HotelBot("Капсульный отель 'Космос'")
    bot.run()


if __name__ == "__main__":
    main()