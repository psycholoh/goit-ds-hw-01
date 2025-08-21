import os
import pickle
from collections import UserDict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be exactly 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value: str):
        try:
            datetime.strptime(value, "%d.%m.%Y") 
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value) 

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return
        raise ValueError(f"Phone {phone} not found.")

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError(f"Phone {old_phone} not found.")

    def __str__(self):
        phones_str = "; ".join(phone.value for phone in self.phones)
        birthday_str = self.birthday.value if self.birthday else "No birthday set"
        return f"Name: {self.name.value}, Phones: {phones_str}, Birthday: {birthday_str}"

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

class AddressBook(UserDict):
    def find(self, name):
        return self.data.get(name)

    def add_record(self, record):
        self.data[record.name.value] = record

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError(f"No contact with name '{name}' found.")

    def __str__(self):
        if not self.data:
            return "AddressBook is empty."
        return '\n'.join(str(record) for record in self.data.values())

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        end_date = today + timedelta(days=7)
        upcoming = []

        for record in self.data.values():
            if not record.birthday:
                continue
            birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            birthday_this_year = birthday_date.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            if today <= birthday_this_year <= end_date:
                congrat_date = birthday_this_year
                if congrat_date.weekday() == 5:  
                    congrat_date += timedelta(days=2)
                elif congrat_date.weekday() == 6:  
                    congrat_date += timedelta(days=1)

                upcoming.append({
                    "name": record.name.value,
                    "birthday": congrat_date.strftime("%d.%m.%Y")
                })
        return upcoming

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError as e:
            return f"Value error: {e}"
        except IndexError:
            return "Enter user name and phone."
        except AttributeError:
            return "Contact not found."
        except Exception as e:
            return f"Unexpected error: {e}"
    return inner

def parse_input(user_input):
    return user_input.strip().split()

@input_error
def add_contact(command_parts, book):
    if len(command_parts) < 3:
        raise IndexError
    _, name, phone = command_parts
    record = book.find(name)
    if not record:
        record = Record(name)
        book.add_record(record)
    record.add_phone(phone)
    return "Contact added."

@input_error
def change_contact(command_parts, book):
    if len(command_parts) < 4:
        raise IndexError
    name, old_phone, new_phone = command_parts
    record = book.find(name)
    record.edit_phone(old_phone, new_phone)
    return "Contact changed."

@input_error
def show_phone(command_parts, book):
    name = command_parts[1]
    record = book.find(name)
    phones = "; ".join(p.value for p in record.phones)
    return f"Phones for {name}: {phones}"



@input_error
def add_birthday(command_parts, book):
    _, name, birthday = command_parts
    record = book.find(name)
    record.add_birthday(birthday)
    return f"Birthday for {name} added."

@input_error
def show_birthday(command_parts, book):
    name = command_parts[1]
    record = book.find(name)
    if not record.birthday:
        return f"{name} has no birthday set."
    return f"Birthday for {name}: {record.birthday.value}"




@input_error
def birthdays(command_parts, book):
    bdays = book.get_upcoming_birthdays()
    if not bdays:
        return "No upcoming birthdays in the next 7 days."
    return "\n".join([f"{bd['name']}: {bd['birthday']}" for bd in bdays])

@input_error
def hello(command_parts, book):
    return "Hello, how can I help you?"

@input_error
def exit(command_parts, book):
    return "Good bye!"

def show_all(book):
    return str(book)

DATA_FILE = "addressbook.pkl"

def save_data(book):
    with open(DATA_FILE, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            return pickle.load(f)
    return AddressBook()

def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input(">>> ")
        command_parts = parse_input(user_input)

        if not command_parts:
            print("Invalid command.")
            continue

        command = command_parts[0].lower()

        if command == "add":
            result = add_contact(command_parts, book)
        elif command == "change":
            result = change_contact(command_parts, book)
        elif command == "phone":
            result = show_phone(command_parts, book)        
        elif command == "add-birthday":
            result = add_birthday(command_parts, book)
        elif command == "show-birthday":
            result = show_birthday(command_parts, book)
        elif command == "birthdays":
            result = birthdays(command_parts, book)
        elif command == "hello":
            result = hello(command_parts, book)
        elif command in ["exit", "close"]:
            save_data(book)
            print(exit(command_parts, book))
            break
        elif command == "all":
            result = show_all(book)
        else: 
            result = "Unknown command. Please try again."

        if result:
            print(result)

if __name__ == "__main__":
    main()