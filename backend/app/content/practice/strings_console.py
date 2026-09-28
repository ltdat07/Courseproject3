"""Строки и консольный ввод/вывод."""

TASKS = [
    {
        "id": 25,
        "topic_id": 9,
        "story": "Привратник Башни спрашивает возраст героя, но некоторые путники отвечают «достаточно взрослый». Пропускной пункт должен это пережить.",
        "question": "Какая запись безопасно пытается преобразовать введённую строку в число?",
        "type": "single_choice",
        "options": [
            {
                "id": 1,
                "text": "int age = Console.ReadLine();",
            },
            {
                "id": 2,
                "text": "bool success = int.TryParse(Console.ReadLine(), out int age);",
            },
            {
                "id": 3,
                "text": "int age = int.Parse(Console.WriteLine());",
            },
            {
                "id": 4,
                "text": "int.TryParse(Console.ReadLine(), int age);",
            },
        ],
        "correct_option_id": 2,
        "success_message": "Привратник получил число и даже пережил неправильный ввод!",
        "error_message": "Башня требует не просто преобразование, а возможность спокойно узнать, удалось ли оно.",
        "explanation": "int.TryParse возвращает true или false и записывает результат в out-переменную. В отличие от Parse, неверный текст не приводит к FormatException.",
    },
    {
        "id": 26,
        "topic_id": 9,
        "story": "Руна форматирования удаляет лишнюю пыль, переводит заклинание в нижний регистр и скрепляет его части дефисом.",
        "question": "Что выведет программа?",
        "type": "code_output",
        "code": """string spell = \"  fire BALL  \";

spell = spell.Trim().ToLower().Replace(\" \", \"-\");

Console.WriteLine($\"{spell}:{spell.Length}\");""",
        "options": [
            {
                "id": 1,
                "text": "fire ball:9",
            },
            {
                "id": 2,
                "text": "FIRE-BALL:9",
            },
            {
                "id": 3,
                "text": "fire-ball:11",
            },
            {
                "id": 4,
                "text": "fire-ball:9",
            },
        ],
        "correct_option_id": 4,
        "success_message": "Руна очищена: ни одного лишнего пробела не уцелело!",
        "error_message": "Проследи по порядку работу Trim, ToLower и Replace, затем пересчитай символы.",
        "explanation": "Trim удаляет пробелы только по краям, ToLower меняет регистр, а Replace превращает внутренний пробел в дефис. Строка fire-ball содержит девять символов.",
    },
    {
        "id": 27,
        "topic_id": 9,
        "story": "Зеркало имён иногда получает пустоту. Архивариус всё равно вызывает Trim и тем самым призывает NullReferenceException.",
        "question": "Как обработать null и одновременно удалить пробелы по краям?",
        "type": "choose_fix",
        "code": """Console.Write(\"Имя героя: \");
string? name = Console.ReadLine();

Console.WriteLine($\"Герой: {name.Trim()}\");""",
        "options": [
            {
                "id": 1,
                "text": "string name = Console.ReadLine()!.Trim();",
            },
            {
                "id": 2,
                "text": "string? name = Console.ReadLine(); Console.WriteLine(name ?? Trim());",
            },
            {
                "id": 3,
                "text": "string name = Console.ReadLine()?.Trim() ?? \"Безымянный\"; Console.WriteLine($\"Герой: {name}\");",
            },
            {
                "id": 4,
                "text": "string name = Console.ReadLine().ToString();",
            },
        ],
        "correct_option_id": 3,
        "success_message": "Даже молчаливый странник теперь получит официальное имя!",
        "error_message": "Оператор ! успокаивает компилятор, но не защищает программу при выполнении.",
        "explanation": "?. вызывает Trim только для непустой ссылки, а ?? подставляет запасное имя, если ReadLine вернул null.",
    },
    {
        "id": 38,
        "topic_id": 9,
        "story": "Врата Башни понимают команду START, но путники вводят start, Start и другие варианты. Страж устал спорить о регистре букв.",
        "question": "Как проверить команду без учёта регистра?",
        "type": "choose_fix",
        "code": """string command = Console.ReadLine() ?? \"\";

if (command == \"START\")
{
    Console.WriteLine(\"Врата открыты\");
}""",
        "options": [
            {
                "id": 1,
                "text": "if (command = \"START\")",
            },
            {
                "id": 2,
                "text": "if (command.Equals(\"START\", StringComparison.OrdinalIgnoreCase))",
            },
            {
                "id": 3,
                "text": "if (command.Contains(\"start\"))",
            },
            {
                "id": 4,
                "text": "if (command.Length == 5)",
            },
        ],
        "correct_option_id": 2,
        "success_message": "Врата приняли команду, как бы путник ни менял регистр!",
        "error_message": "Нужна проверка равенства всей строки с явным правилом сравнения.",
        "explanation": "StringComparison.OrdinalIgnoreCase сравнивает строки без учёта регистра и не зависит от языковых настроек системы. Contains и проверка длины не гарантируют равенство команды.",
    },
]
