"""Null и исключения."""

TASKS = [
    {
        "id": 16,
        "topic_id": 6,
        "story": "Гильдия не выбрана, но писарь всё равно требует длину её названия. Пустота уже готовит NullReferenceException.",
        "question": "Что выведет программа?",
        "type": "code_output",
        "code": """string? guild = null;
Console.WriteLine(guild?.Length ?? 0);""",
        "options": [
            {
                "id": 1,
                "text": "null",
            },
            {
                "id": 2,
                "text": "0",
            },
            {
                "id": 3,
                "text": "Пустую строку",
            },
            {
                "id": 4,
                "text": "Возникнет NullReferenceException",
            },
        ],
        "correct_option_id": 2,
        "success_message": "Пустота обезврежена запасным нулём.",
        "error_message": "Проследи работу операторов ?. и ??.",
        "explanation": "?. не обращается к Length, когда guild равна null, а ?? подставляет 0.",
    },
    {
        "id": 17,
        "topic_id": 6,
        "story": "Ловушка catch приготовилась к NullReferenceException, а из тумана вышла совсем другая ошибка.",
        "question": "Почему программа не обрабатывает ошибку?",
        "type": "find_error",
        "code": """try
{
    int level = int.Parse(\"меч\");
}
catch (NullReferenceException)
{
    Console.WriteLine(\"Неверный уровень\");
}""",
        "options": [
            {
                "id": 1,
                "text": "int.Parse возвращает 0, поэтому ошибки нет",
            },
            {
                "id": 2,
                "text": "Перехватывается неверный тип исключения",
            },
            {
                "id": 3,
                "text": "После catch обязательно нужен finally",
            },
            {
                "id": 4,
                "text": "int.Parse работает только с double",
            },
        ],
        "correct_option_id": 2,
        "success_message": "FormatException опознана и больше не пройдёт под чужим именем.",
        "error_message": "Определи, какое исключение вызывает нечисловая строка.",
        "explanation": "int.Parse для строки «меч» выбрасывает FormatException, поэтому catch (NullReferenceException) её не перехватит.",
    },
    {
        "id": 18,
        "topic_id": 6,
        "story": "Алхимик принимает любой ввод, но не хочет взрывать лабораторию каждый раз, когда вместо числа получает слово «дракон».",
        "question": "Как безопасно проверить ввод и получить число без исключения?",
        "type": "choose_fix",
        "options": [
            {
                "id": 1,
                "text": "bool ok = int.TryParse(input, out int level);",
            },
            {
                "id": 2,
                "text": "int level = Convert.ToInt32(input);",
            },
            {
                "id": 3,
                "text": "int level = int.Parse(input!);",
            },
            {
                "id": 4,
                "text": "int level = (int)(object)input;",
            },
        ],
        "correct_option_id": 1,
        "success_message": "Лаборатория цела, а неверный ввод получил спокойное false.",
        "error_message": "Нужен метод, который сообщает об успехе значением bool.",
        "explanation": "TryParse возвращает false для неверной строки и записывает число в level только при успешном преобразовании.",
    },
    {
        "id": 45,
        "topic_id": 6,
        "story": "Название древнего свитка отсутствует. Писарь использует безопасный доступ и заранее приготовил число на случай пустоты.",
        "question": "Что выведет программа?",
        "type": "code_output",
        "code": """string? title = null;

Console.WriteLine(title?.Length ?? -1);""",
        "options": [
            {
                "id": 1,
                "text": "0",
            },
            {
                "id": 2,
                "text": "-1",
            },
            {
                "id": 3,
                "text": "null",
            },
            {
                "id": 4,
                "text": "NullReferenceException",
            },
        ],
        "correct_option_id": 2,
        "success_message": "Пустота обработана, и древнее исключение продолжило спать.",
        "error_message": "Проследи сначала оператор ?., затем запасное значение ??.",
        "explanation": "Из-за null выражение title?.Length возвращает nullable-значение null. Оператор ?? заменяет его числом -1, исключение не возникает.",
    },
]
