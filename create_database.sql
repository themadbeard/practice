PRAGMA foreign_keys = ON;

CREATE TABLE Ингредиенты (
код INTEGER PRIMARY KEY AUTOINCREMENT,
название TEXT UNIQUE,
остаток INTEGER
);

CREATE TABLE Пицца (
код INTEGER PRIMARY KEY AUTOINCREMENT,
название TEXT UNIQUE
);

CREATE TABLE ПиццаИнгр (
код INTEGER PRIMARY KEY AUTOINCREMENT,
код_ингр INTEGER REFERENCES Ингредиенты(код),
код_пиццы INTEGER REFERENCES Пицца(код)
);

CREATE TABLE Статус(
код INTEGER PRIMARY KEY AUTOINCREMENT,
название TEXT UNIQUE
)

CREATE TABLE Заказ (
код INTEGER PRIMARY KEY AUTOINCREMENT,
статус TEXT UNIQUE
);

CREATE TABLE ПиццаЗаказ(
код INTEGER PRIMARY KEY AUTOINCREMENT,
код_пиццы INTEGER REFERENCES Пицца(код),
код_заказа INTEGER REFERENCES Заказ(код),
код_клиента INTEGER REFERENCES Клиенты(код)
)


CREATE TABLE Клиенты (
код INTEGER PRIMARY KEY AUTOINCREMENT,
имя TEXT UNIQUE,
адрес TEXT
);

commit


insert into Ингредиенты values
(1, 'Помидор', 3),
(2, 'Моцарелла', 5)


insert into Пицца values
(1,'Margarita'),
(2, 'Pesto'),
(3, 'Chicken')

insert into Клиенты values
(1, 'Иван', 'Ул. Пушкина'),
(2, 'Андрей', 'Ул. Колотушкина'),
(3, 'Илья', 'Проспект Мира')

insert into Заказ values
(1, ' Готовится'),
(2, 'В доставке')

insert into ПиццаЗаказ values
(1, 1, 1, 2);

