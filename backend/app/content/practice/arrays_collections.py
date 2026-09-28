"""Массивы и коллекции."""

TASKS = [
    {
        "id": 10,
        "topic_id": 4,
        "story": "Инвентарь добавил новое зелье и выбросил просроченное. Осталось проверить, не съел ли список что-нибудь ещё.",
        "question": "Что выведет программа?",
        "type": "code_output",
        "code": """List<int> potions = new List<int> { 2, 4 };

potions.Add(6);
potions.Remove(4);

Console.WriteLine($\"{potions.Count}:{potions[1]}\");""",
        "options": [
            {
                "id": 1,
                "text": "2:6",
            },
            {
                "id": 2,
                "text": "3:4",
            },
            {
                "id": 3,
                "text": "2:4",
            },
            {
                "id": 4,
                "text": "3:6",
            },
        ],
        "correct_option_id": 1,
        "success_message": "Инвентарь сошёлся. Ни одно зелье не исчезло в карманном измерении!",
        "error_message": "Проследи состояние List после Add и Remove.",
        "explanation": "После добавления 6 и удаления 4 список содержит 2 и 6. Count равен 2, а элемент с индексом 1 равен 6.",
    },
    {
        "id": 11,
        "topic_id": 4,
        "story": "Герой ищет щит в словаре добычи. Прямое обращение к отсутствующему ключу уже однажды разбудило KeyNotFoundException.",
        "question": "Как безопасно проверить наличие ключа «щит» и получить его значение?",
        "type": "single_choice",
        "code": """Dictionary<string, int> loot = new Dictionary<string, int>
{
    [\"меч\"] = 12
};""",
        "options": [
            {
                "id": 1,
                "text": "loot.TryGetValue(\"щит\", out int armor)",
            },
            {
                "id": 2,
                "text": "loot[\"щит\"]",
            },
            {
                "id": 3,
                "text": "loot.Find(\"щит\")",
            },
            {
                "id": 4,
                "text": "loot.ContainsValue(\"щит\")",
            },
        ],
        "correct_option_id": 1,
        "success_message": "Словарь вежливо сообщил, что щита нет, и не бросил исключение.",
        "error_message": "Нужен метод, который возвращает bool и записывает значение в out-параметр.",
        "explanation": "TryGetValue возвращает false, если ключ отсутствует, вместо KeyNotFoundException. При успехе значение записывается в armor.",
    },
    {
        "id": 12,
        "topic_id": 4,
        "story": "Архивариус решил взять руну с номером Length. Руна оказалась за пределами реальности массива.",
        "question": "Какая ошибка возникнет и как обратиться к последнему элементу?",
        "type": "find_error",
        "code": """string[] runes = { \"Огонь\", \"Лёд\", \"Свет\" };

Console.WriteLine(runes[runes.Length]);""",
        "options": [
            {
                "id": 1,
                "text": "IndexOutOfRangeException; нужен индекс runes.Length - 1",
            },
            {
                "id": 2,
                "text": "KeyNotFoundException; нужен индекс runes.Length + 1",
            },
            {
                "id": 3,
                "text": "Ошибки нет; будет выведено «Свет»",
            },
            {
                "id": 4,
                "text": "Массив string нельзя индексировать",
            },
        ],
        "correct_option_id": 1,
        "success_message": "Последняя руна найдена. Край массива снова огорожен!",
        "error_message": "При трёх элементах допустимы индексы 0, 1 и 2.",
        "explanation": "Length равен 3, но индекса 3 в массиве нет. Последний допустимый индекс равен Length - 1.",
    },
    {
        "id": 41,
        "topic_id": 4,
        "story": "Кладовщик ищет эликсир по ключу, которого может не оказаться в словаре. Прямое обращение уже разбудило KeyNotFoundException.",
        "question": "Как безопасно получить количество эликсиров?",
        "type": "choose_fix",
        "code": """Dictionary<string, int> stock = new()
{
    [\"potion\"] = 3
};

Console.WriteLine(stock[\"elixir\"]);""",
        "options": [
            {
                "id": 1,
                "text": "Console.WriteLine(stock.Get(\"elixir\"));",
            },
            {
                "id": 2,
                "text": "Console.WriteLine(stock[0]);",
            },
            {
                "id": 3,
                "text": "if (stock.TryGetValue(\"elixir\", out int count)) Console.WriteLine(count);",
            },
            {
                "id": 4,
                "text": "Console.WriteLine(stock.Add(\"elixir\", 0));",
            },
        ],
        "correct_option_id": 3,
        "success_message": "Кладовщик проверил ключ до открытия ячейки!",
        "error_message": "Нужен метод, который одновременно проверяет ключ и возвращает значение.",
        "explanation": "TryGetValue возвращает bool и записывает найденное значение в out-переменную. Индексатор словаря выбрасывает исключение, если ключ отсутствует.",
    },
    {
        "id": 52,
        "topic_id": 4,
        "story": "Архивариус назвал вторую переменную копией массива, но на самом деле выдал ей ключ от того же хранилища.",
        "question": "Что выведет программа?",
        "type": "code_output",
        "code": """int[] first = { 1, 2 };
int[] second = first;

second[0] = 9;
Console.WriteLine(first[0]);""",
        "options": [
            {
                "id": 1,
                "text": "9",
            },
            {
                "id": 2,
                "text": "1",
            },
            {
                "id": 3,
                "text": "0",
            },
            {
                "id": 4,
                "text": "Ошибка компиляции",
            },
        ],
        "correct_option_id": 1,
        "success_message": "Верно! Обе переменные открывали одно хранилище.",
        "error_message": "Присваивание массива копирует ссылку, а не его элементы.",
        "explanation": "first и second ссылаются на один массив. Изменение элемента через second видно через first. Для отдельной копии можно использовать Clone или ToArray.",
    },
]
