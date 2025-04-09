import datetime
from typing import List, Dict, Optional

class Guest:
    """Класс для представления гостя отеля"""
    def __init__(self, guest_id: int, name: str, passport: str, phone: str):
        self.guest_id = guest_id
        self.name = name
        self.passport = passport
        self.phone = phone
        self.bookings: List['Booking'] = []
    
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
    
    def __str__(self):
        return f"Гость #{self.guest_id}: {self.name}, паспорт: {self.passport}"


class Capsule:
    """Класс для представления капсулы в отеле"""
    def __init__(self, capsule_id: int, capsule_type: str, price_per_night: float):
        self.capsule_id = capsule_id
        self.type = capsule_type
        self.price_per_night = price_per_night
        self.is_available = True
        self.current_booking: Optional['Booking'] = None
    
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
    
    def __str__(self):
        status = "доступна" if self.is_available else "занята"
        return f"Капсула #{self.capsule_id} ({self.type}), {status}, цена за ночь: {self.price_per_night}"


class Booking:
    """Класс для представления бронирования"""
    def __init__(self, booking_id: int, guest: Guest, capsule: Capsule, 
                 start_date: datetime.date, end_date: datetime.date):
        self.booking_id = booking_id
        self.guest = guest
        self.capsule = capsule
        self.start_date = start_date
        self.end_date = end_date
        self.is_paid = False
        self.capsule.book(self)
        self.guest.add_booking(self)
    
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
    
    def __str__(self):
        paid_status = "оплачено" if self.is_paid else "не оплачено"
        return (f"Бронирование #{self.booking_id}: {self.guest.name} в капсуле #{self.capsule.capsule_id} "
                f"с {self.start_date} по {self.end_date}, {paid_status}")


class Hotel:
    """Класс для представления отеля"""
    def __init__(self, name: str):
        self.name = name
        self.guests: Dict[int, Guest] = {}
        self.capsules: Dict[int, Capsule] = {}
        self.bookings: Dict[int, Booking] = {}
        self.next_guest_id = 1
        self.next_capsule_id = 1
        self.next_booking_id = 1
    
    def add_capsule(self, capsule_type: str, price_per_night: float) -> Capsule:
        """Добавить капсулу в отель"""
        capsule = Capsule(self.next_capsule_id, capsule_type, price_per_night)
        self.capsules[self.next_capsule_id] = capsule
        self.next_capsule_id += 1
        return capsule
    
    def register_guest(self, name: str, passport: str, phone: str) -> Guest:
        """Зарегистрировать гостя"""
        guest = Guest(self.next_guest_id, name, passport, phone)
        self.guests[self.next_guest_id] = guest
        self.next_guest_id += 1
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
        
        booking = Booking(self.next_booking_id, guest, capsule, start_date, end_date)
        self.bookings[self.next_booking_id] = booking
        self.next_booking_id += 1
        return booking
    
    def get_available_capsules(self) -> List[Capsule]:
        """Получить список доступных капсул"""
        return [c for c in self.capsules.values() if c.is_available]
    
    def check_out(self, booking_id: int):
        """Выселить гостя (освободить капсулу)"""
        if booking_id not in self.bookings:
            raise ValueError("Бронирование не найдено")
        
        booking = self.bookings[booking_id]
        booking.capsule.release()
        del self.bookings[booking_id]
    
    def __str__(self):
        return (f"Отель '{self.name}': {len(self.guests)} гостей, "
                f"{len(self.capsules)} капсул, {len(self.bookings)} активных бронирований")


class HotelBot:
    """Класс для управления отелем через бота"""
    def __init__(self, hotel_name: str):
        self.hotel = Hotel(hotel_name)
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Инициализировать тестовые данные"""
        # Добавляем капсулы
        self.hotel.add_capsule("Стандарт", 1500)
        self.hotel.add_capsule("Стандарт", 1500)
        self.hotel.add_capsule("Люкс", 2500)
        self.hotel.add_capsule("Люкс", 2500)
        self.hotel.add_capsule("Премиум", 3500)
        
        # Регистрируем гостей
        self.hotel.register_guest("Иван Иванов", "1234567890", "+79123456789")
        self.hotel.register_guest("Петр Петров", "0987654321", "+79098765432")
    
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
                elif choice == "0":
                    print("До свидания!")
                    break
                else:
                    print("Неверный выбор, попробуйте снова.")
            except Exception as e:
                print(f"Ошибка: {e}")
    
    def _show_all_capsules(self):
        """Показать все капсулы"""
        print("\nВсе капсулы в отеле:")
        for capsule in self.hotel.capsules.values():
            print(capsule)
    
    def _show_available_capsules(self):
        """Показать доступные капсулы"""
        available = self.hotel.get_available_capsules()
        print("\nДоступные капсулы:")
        for capsule in available:
            print(capsule)
    
    def _register_guest(self):
        """Зарегистрировать нового гостя"""
        print("\nРегистрация нового гостя:")
        name = input("ФИО: ")
        passport = input("Паспортные данные: ")
        phone = input("Телефон: ")
        
        guest = self.hotel.register_guest(name, passport, phone)
        print(f"Гость успешно зарегистрирован: {guest}")
    
    def _create_booking(self):
        """Создать бронирование"""
        print("\nСоздание бронирования:")
        
        # Показать гостей
        print("Список гостей:")
        for guest in self.hotel.guests.values():
            print(guest)
        
        guest_id = int(input("Введите ID гостя: "))
        
        # Показать доступные капсулы
        available = self.hotel.get_available_capsules()
        print("Доступные капсулы:")
        for capsule in available:
            print(capsule)
        
        capsule_id = int(input("Введите ID капсулы: "))
        
        # Ввод дат
        start_date_str = input("Дата заезда (ГГГГ-ММ-ДД): ")
        end_date_str = input("Дата выезда (ГГГГ-ММ-ДД): ")
        
        start_date = datetime.date.fromisoformat(start_date_str)
        end_date = datetime.date.fromisoformat(end_date_str)
        
        # Создание бронирования
        booking = self.hotel.create_booking(guest_id, capsule_id, start_date, end_date)
        print(f"Бронирование создано: {booking}")
        print(f"Общая стоимость: {booking.calculate_total()} руб.")
    
    def _show_all_bookings(self):
        """Показать все бронирования"""
        print("\nВсе активные бронирования:")
        for booking in self.hotel.bookings.values():
            print(booking)
    
    def _check_out(self):
        """Выселить гостя"""
        print("\nВыселение гостя:")
        self._show_all_bookings()
        
        booking_id = int(input("Введите ID бронирования для выселения: "))
        self.hotel.check_out(booking_id)
        print("Гость успешно выселен, капсула освобождена.")


# Основная функция для демонстрации работы
def main():
    bot = HotelBot("Космический капсульный отель")
    bot.run()


if __name__ == "__main__":
    main()