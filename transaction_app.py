import os
import csv
from datetime import datetime
from abc import ABC, abstractmethod

class Transaction:
    """Класс, представляющий одну транзакцию"""
    def __init__(self, id, date_time, amount, description):
        self.id = id
        self.date_time = date_time
        self.amount = amount
        self.description = description

    def __repr__(self):
        return (f"Transaction(id={self.id}, date_time={self.date_time}, "
                f"amount={self.amount}, description='{self.description}')")

    def __str__(self):
        return f"№{self.id} | {self.date_time} | {self.amount:.2f} | {self.description}"

    def __setattr__(self, name, value):
        # Валидация при установке атрибутов
        if name == 'id' and (not isinstance(value, int) or value < 0):
            raise ValueError("ID должен быть положительным целым числом")
        elif name == 'date_time' and not isinstance(value, datetime):
            raise ValueError("Дата должна быть объектом datetime")
        elif name == 'amount' and not isinstance(value, (int, float)):
            raise ValueError("Сумма должна быть числом")
        elif name == 'description' and not isinstance(value, str):
            raise ValueError("Описание должно быть строкой")
        super().__setattr__(name, value)


class TransactionCollection(ABC):
    """Абстрактный базовый класс для коллекций транзакций"""
    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def __getitem__(self, index):
        pass

    @abstractmethod
    def add_transaction(self, transaction):
        pass

    @staticmethod
    def validate_transaction_data(id, date_time, amount, description):
        """Статический метод для валидации данных транзакции"""
        if not isinstance(id, int) or id < 0:
            return False
        if not isinstance(date_time, datetime):
            return False
        if not isinstance(amount, (int, float)):
            return False
        if not isinstance(description, str):
            return False
        return True


class TransactionManager(TransactionCollection):
    """Класс для управления коллекцией транзакций"""
    def __init__(self):
        self._transactions = []

    def __iter__(self):
        """Итератор по транзакциям"""
        return iter(self._transactions)

    def __getitem__(self, index):
        """Доступ к транзакциям по индексу"""
        return self._transactions[index]

    def __repr__(self):
        return f"TransactionManager(transactions={self._transactions})"

    def __len__(self):
        return len(self._transactions)

    def add_transaction(self, transaction):
        """Добавление транзакции в коллекцию"""
        if not isinstance(transaction, Transaction):
            raise ValueError("Можно добавлять только объекты Transaction")
        self._transactions.append(transaction)

    def sort_by_description(self):
        """Сортировка транзакций по описанию"""
        self._transactions.sort(key=lambda x: x.description)

    def sort_by_amount(self):
        """Сортировка транзакций по сумме"""
        self._transactions.sort(key=lambda x: x.amount)

    def filter_by_amount(self, min_amount):
        """Генератор для фильтрации транзакций по минимальной сумме"""
        for transaction in self._transactions:
            if transaction.amount >= min_amount:
                yield transaction

    def print_transactions(self):
        """Вывод всех транзакций"""
        for transaction in self._transactions:
            print(transaction)

    @classmethod
    def from_csv(cls, filename):
        """Альтернативный конструктор для загрузки из CSV"""
        manager = cls()
        manager.load_from_csv(filename)
        return manager

    def load_from_csv(self, filename):
        """Загрузка транзакций из CSV-файла"""
        try:
            with open(filename, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    transaction = Transaction(
                        id=int(row['№']),
                        date_time=datetime.strptime(row['дата и время'], '%Y-%m-%d %H:%M:%S'),
                        amount=float(row['сумма']),
                        description=row['описание транзакции']
                    )
                    self.add_transaction(transaction)
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл {filename} не найден!")

    def save_to_csv(self, filename):
        """Сохранение транзакций в CSV-файл"""
        with open(filename, mode='w', encoding='utf-8', newline='') as file:
            fieldnames = ['№', 'дата и время', 'сумма', 'описание транзакции']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for t in self._transactions:
                writer.writerow({
                    '№': t.id,
                    'дата и время': t.date_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'сумма': t.amount,
                    'описание транзакции': t.description
                })


class ExtendedTransactionManager(TransactionManager):
    """Расширенный менеджер транзакций с дополнительной функциональностью"""
    def __init__(self):
        super().__init__()
        self._history = []

    def add_transaction(self, transaction):
        """Переопределенный метод с добавлением истории изменений"""
        super().add_transaction(transaction)
        self._history.append((datetime.now(), "ADD", str(transaction)))

    def get_transactions_by_description(self, keyword):
        """Генератор для поиска транзакций по ключевому слову в описании"""
        for transaction in self._transactions:
            if keyword.lower() in transaction.description.lower():
                yield transaction

    def get_history(self):
        """Генератор для получения истории изменений"""
        for record in self._history:
            yield record


def count_files_in_directory(directory):
    """Подсчитывает количество файлов в указанной директории"""
    return len([name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))])


def main():
    # 1. Подсчет файлов в директории
    directory = input("Введите путь к директории: ")
    file_count = count_files_in_directory(directory)
    print(f"\nКоличество файлов в директории: {file_count}")

    # 2. Чтение данных из файла
    filename = 'data.csv'
    try:
        manager = ExtendedTransactionManager.from_csv(filename)
        print("\nЗагружено транзакций:", len(manager))
    except FileNotFoundError:
        print(f"\nФайл {filename} не найден!")
        return

    while True:
        print("\nМеню:")
        print("1. Вывести все транзакции")
        print("2. Сортировать по описанию (строковое поле)")
        print("3. Сортировать по сумме (числовое поле)")
        print("4. Фильтровать по минимальной сумме")
        print("5. Найти по ключевому слову в описании")
        print("6. Добавить новую транзакцию")
        print("7. Сохранить изменения")
        print("8. Показать историю изменений")
        print("0. Выход")

        choice = input("Выберите действие: ")

        if choice == '1':
            print("\nВсе транзакции:")
            manager.print_transactions()

        elif choice == '2':
            manager.sort_by_description()
            print("\nТранзакции, отсортированные по описанию:")
            manager.print_transactions()

        elif choice == '3':
            manager.sort_by_amount()
            print("\nТранзакции, отсортированные по сумме:")
            manager.print_transactions()

        elif choice == '4':
            min_amount = float(input("Введите минимальную сумму: "))
            print(f"\nТранзакции с суммой ≥ {min_amount}:")
            for transaction in manager.filter_by_amount(min_amount):
                print(transaction)

        elif choice == '5':
            keyword = input("Введите ключевое слово для поиска: ")
            print(f"\nТранзакции, содержащие '{keyword}':")
            for transaction in manager.get_transactions_by_description(keyword):
                print(transaction)

        elif choice == '6':
            try:
                new_trans = Transaction(
                    id=len(manager) + 1,
                    date_time=datetime.now(),
                    amount=float(input("Введите сумму: ")),
                    description=input("Введите описание: ")
                )
                manager.add_transaction(new_trans)
                print("Транзакция добавлена!")
            except ValueError as e:
                print(f"Ошибка: {e}")

        elif choice == '7':
            manager.save_to_csv(filename)
            print("Изменения сохранены в файл!")

        elif choice == '8':
            print("\nИстория изменений:")
            for time, action, details in manager.get_history():
                print(f"{time}: {action} - {details}")

        elif choice == '0':
            break

        else:
            print("Неверный ввод!")


if __name__ == "__main__":
    main()

