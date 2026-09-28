"""Основы C#."""

TASKS = [
    {
        "id": 1,
        "topic_id": 1,
        "story": "Таможенник мира C# пропускает только строго типизированных героев. Без типа даже меч считается подозрительным объектом.",
        "question": "Какая запись создаёт целочисленную переменную score со значением 12 и выводит её?",
        "type": "single_choice",
        "options": [
            {
                "id": 1,
                "text": "int score = 12; Console.WriteLine(score);",
            },
            {
                "id": 2,
                "text": "string score = 12; Console.WriteLine(score);",
            },
            {
                "id": 3,
                "text": "score int = 12; Console.WriteLine(score);",
            },
            {
                "id": 4,
                "text": "int score == 12; Console.WriteLine(score);",
            },
        ],
        "correct_option_id": 1,
        "success_message": "Документы в порядке. Переменная официально зарегистрирована!",
        "error_message": "Таможенник стучит по строке кода: «Где корректные тип и присваивание?»",
        "explanation": "Тип int хранит целые числа. При объявлении сначала указываются тип и имя, затем оператор = и значение.",
    },
    {
        "id": 2,
        "topic_id": 1,
        "story": "Гоблин-бухгалтер пересчитывает монеты целыми числами. Дробные монеты его профсоюз не признаёт.",
        "question": "Что выведет программа?",
        "type": "code_output",
        "code": """int coins = 9;
coins += 4;

Console.WriteLine(coins / 2);""",
        "options": [
            {
                "id": 1,
                "text": "6",
            },
            {
                "id": 2,
                "text": "6.5",
            },
            {
                "id": 3,
                "text": "13",
            },
            {
                "id": 4,
                "text": "Ошибка компиляции",
            },
        ],
        "correct_option_id": 1,
        "success_message": "Верно! Казна поделена с точностью до целого гоблина.",
        "error_message": "Учти тип переменных: оба участника деления имеют тип int.",
        "explanation": "После coins += 4 значение равно 13. При делении двух int дробная часть отбрасывается, поэтому 13 / 2 даёт 6.",
    },
    {
        "id": 3,
        "topic_id": 1,
        "story": "Магическое зеркало должно назвать героя, но упрямо повторяет фигурные скобки вслух.",
        "question": "Как исправить вывод, чтобы получить строку «Герой: Лин»?",
        "type": "choose_fix",
        "code": """string name = \"Лин\";
Console.WriteLine(\"Герой: {name}\");""",
        "options": [
            {
                "id": 1,
                "text": "Console.WriteLine($\"Герой: {name}\");",
            },
            {
                "id": 2,
                "text": "Console.WriteLine(\"Герой: {name}\");",
            },
            {
                "id": 3,
                "text": "Console.WriteLine(\"Герой: \" - name);",
            },
            {
                "id": 4,
                "text": "Console.WriteLine({name});",
            },
        ],
        "correct_option_id": 1,
        "success_message": "Зеркало узнало героя. Неловкая пауза со скобками окончена!",
        "error_message": "Зеркало всё ещё не понимает, что значение нужно подставить в строку.",
        "explanation": "Символ $ перед строкой включает интерполяцию: выражение внутри {name} заменяется значением переменной.",
    },
    {
        "id": 37,
        "topic_id": 1,
        "story": "Казначей переливает целые кристаллы в сосуд типа double и уверен, что дробная половина появится сама. Компилятор загадочно молчит.",
        "question": "Что выведет программа?",
        "type": "code_output",
        "code": """int crystals = 7;
double share = crystals / 2;

Console.WriteLine(share);""",
        "options": [
            {
                "id": 1,
                "text": "3.5",
            },
            {
                "id": 2,
                "text": "7",
            },
            {
                "id": 3,
                "text": "3",
            },
            {
                "id": 4,
                "text": "Ошибка компиляции",
            },
        ],
        "correct_option_id": 3,
        "success_message": "Верно! Сосуд double не вернул потерянную половину кристалла.",
        "error_message": "Сначала вычисляется правая часть, и оба её операнда имеют тип int.",
        "explanation": "Выражение crystals / 2 выполняет целочисленное деление и даёт 3. Только после этого результат преобразуется в double. Для 3.5 нужно делить на 2.0 или заранее привести один операнд к double.",
    },
    {
        "id": 49,
        "topic_id": 1,
        "story": "Торговец принимает только точные decimal-монеты. Литерал 19.99 без опознавательного знака он считает подозрительным double.",
        "question": "Как корректно вычислить стоимость двух предметов в decimal?",
        "type": "choose_fix",
        "options": [
            {
                "id": 1,
                "text": "decimal price = 19.99; decimal total = price * 2;",
            },
            {
                "id": 2,
                "text": "decimal price = 19.99m; decimal total = price * 2;",
            },
            {
                "id": 3,
                "text": "int price = 19.99m; int total = price * 2;",
            },
            {
                "id": 4,
                "text": "var price = '19.99'; decimal total = price * 2;",
            },
        ],
        "correct_option_id": 2,
        "success_message": "Торговец принял расчёт с точностью до последней монеты!",
        "error_message": "Для литерала decimal требуется суффикс m.",
        "explanation": "Число 19.99 без суффикса имеет тип double и не присваивается decimal неявно. Суффикс m создаёт decimal-литерал, после чего умножение корректно.",
    },
]
