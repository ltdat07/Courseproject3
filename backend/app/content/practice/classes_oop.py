"""Классы и ООП."""

TASKS = [
    {
        "id": 13,
        "topic_id": 5,
        "story": "Сундук спрятал золото за private-замком. Взломать поле нельзя, но архитектор предусмотрел парадный вход.",
        "question": "Как получить количество золота из внешнего кода?",
        "type": "single_choice",
        "code": """var chest = new Chest();

class Chest
{
    private int gold = 50;
    public int GetGold() => gold;
}""",
        "options": [
            {
                "id": 1,
                "text": "chest.gold",
            },
            {
                "id": 2,
                "text": "chest.GetGold()",
            },
            {
                "id": 3,
                "text": "Chest.gold",
            },
            {
                "id": 4,
                "text": "Chest.GetGold()",
            },
        ],
        "correct_option_id": 2,
        "success_message": "Сундук открыл официальный канал выдачи золота!",
        "error_message": "Поле gold закрыто модификатором private.",
        "explanation": "Внешний код не может обратиться к private-полю, но может вызвать публичный метод экземпляра chest.GetGold().",
    },
    {
        "id": 14,
        "topic_id": 5,
        "story": "Маг записался в переменную типа Hero, но на проверке навыков всё равно достал настоящее заклинание.",
        "question": "Что выведет программа?",
        "type": "code_output",
        "code": """Hero unit = new Mage();
Console.WriteLine(unit.Skill());

class Hero
{
    public virtual string Skill() => \"удар\";
}

class Mage : Hero
{
    public override string Skill() => \"заклинание\";
}""",
        "options": [
            {
                "id": 1,
                "text": "удар",
            },
            {
                "id": 2,
                "text": "заклинание",
            },
            {
                "id": 3,
                "text": "Hero",
            },
            {
                "id": 4,
                "text": "Mage",
            },
        ],
        "correct_option_id": 2,
        "success_message": "Полиморфизм сработал: маг отказался притворяться воином.",
        "error_message": "Учти реальный тип объекта и ключевые слова virtual/override.",
        "explanation": "Объект имеет тип Mage, поэтому виртуальный вызов использует переопределённый метод Skill наследника.",
    },
    {
        "id": 15,
        "topic_id": 5,
        "story": "Наследник Warrior явился без пропуска в базовый конструктор. Страж Hero требует имя каждого посетителя.",
        "question": "Как исправить конструктор Warrior?",
        "type": "choose_fix",
        "code": """class Hero
{
    public string Name { get; }

    public Hero(string name)
    {
        Name = name;
    }
}

class Warrior : Hero
{
    public Warrior(string name) { }
}""",
        "options": [
            {
                "id": 1,
                "text": "public Warrior(string name) : base(name) { }",
            },
            {
                "id": 2,
                "text": "public Warrior(string name) : this(name) { }",
            },
            {
                "id": 3,
                "text": "public Warrior(string name) { base(name); }",
            },
            {
                "id": 4,
                "text": "public Warrior() : base() { }",
            },
        ],
        "correct_option_id": 1,
        "success_message": "Базовый конструктор получил имя и пропустил наследника.",
        "error_message": "Нужно вызвать существующий конструктор Hero до тела конструктора Warrior.",
        "explanation": "Наследник вызывает конструктор базового класса через base(name). У Hero нет конструктора без параметров.",
    },
    {
        "id": 43,
        "topic_id": 5,
        "story": "Два лекаря уверены, что держат разные карточки героя, хотя обе переменные указывают на один и тот же объект.",
        "question": "Что выведет программа?",
        "type": "code_output",
        "code": """Hero first = new() { Health = 100 };
Hero second = first;

second.Health -= 30;
Console.WriteLine(first.Health);

class Hero
{
    public int Health { get; set; }
}""",
        "options": [
            {
                "id": 1,
                "text": "100",
            },
            {
                "id": 2,
                "text": "30",
            },
            {
                "id": 3,
                "text": "0",
            },
            {
                "id": 4,
                "text": "70",
            },
        ],
        "correct_option_id": 4,
        "success_message": "Верно! Обе карточки вели к одному и тому же герою.",
        "error_message": "Класс — ссылочный тип, а присваивание не создаёт копию объекта.",
        "explanation": "Переменные first и second содержат ссылки на один экземпляр Hero. Изменение Health через second видно и через first.",
    },
    {
        "id": 53,
        "topic_id": 5,
        "story": "Совет Академии разрешает всем видеть здоровье героя, но изменять его должны только методы самого класса.",
        "question": "Какое свойство лучше поддерживает такую инкапсуляцию?",
        "type": "single_choice",
        "options": [
            {
                "id": 1,
                "text": "public int Health;",
            },
            {
                "id": 2,
                "text": "public int Health { get; private set; }",
            },
            {
                "id": 3,
                "text": "private int Health { set; }",
            },
            {
                "id": 4,
                "text": "public static int Health { private get; set; }",
            },
        ],
        "correct_option_id": 2,
        "success_message": "Здоровье видно всем, но изменяется только по правилам класса!",
        "error_message": "Нужен открытый getter и закрытый setter экземпляра.",
        "explanation": "Свойство с public get и private set можно читать снаружи, но присваивать ему значение разрешено только внутри класса. Это защищает состояние объекта.",
    },
]
