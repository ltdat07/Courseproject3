"""Файлы и JSON."""

TASKS = [
    {
        "id": 34,
        "topic_id": 12,
        "story": "Архивариус создаёт летопись, затем аккуратно дописывает продолжение, не стирая первую страницу.",
        "question": "Что выведет программа после успешных файловых операций?",
        "type": "code_output",
        "code": """string path = \"log.txt\";

File.WriteAllText(path, \"A\");
File.AppendAllText(path, \"B\");

Console.WriteLine(File.ReadAllText(path));""",
        "options": [
            {
                "id": 1,
                "text": "A",
            },
            {
                "id": 2,
                "text": "AB",
            },
            {
                "id": 3,
                "text": "B",
            },
            {
                "id": 4,
                "text": "Ошибка: AppendAllText нельзя использовать после WriteAllText",
            },
        ],
        "correct_option_id": 2,
        "success_message": "Обе страницы летописи сохранились в правильном порядке!",
        "error_message": "Первый метод перезаписывает файл, второй дописывает текст в конец.",
        "explanation": "WriteAllText записывает A, затем AppendAllText добавляет B. После чтения содержимое равно AB.",
    },
    {
        "id": 35,
        "topic_id": 12,
        "story": "Архивариус хотел положить сохранение в каталог saves, но вручную склеил части пути и получил файл saveshero.json.",
        "question": "Как правильно создать каталог и построить путь к файлу?",
        "type": "find_error",
        "code": """string folder = \"saves\";
string path = folder + \"hero.json\";

File.WriteAllText(path, \"{}\");""",
        "options": [
            {
                "id": 1,
                "text": "string path = folder - \"hero.json\";",
            },
            {
                "id": 2,
                "text": "string path = Path.GetFileName(folder);",
            },
            {
                "id": 3,
                "text": "Directory.CreateDirectory(folder); string path = Path.Combine(folder, \"hero.json\");",
            },
            {
                "id": 4,
                "text": "string path = File.ReadAllText(folder);",
            },
        ],
        "correct_option_id": 3,
        "success_message": "Сохранение легло в архив, разделители больше не вырезаются вручную!",
        "error_message": "Нужно гарантировать существование каталога и безопасно соединить части пути.",
        "explanation": "Directory.CreateDirectory подготавливает каталог, Path.Combine добавляет правильный разделитель. Простая конкатенация создаёт saveshero.json.",
    },
    {
        "id": 36,
        "topic_id": 12,
        "story": "Кристалл десериализации иногда возвращает null, но летописец сразу обращается к имени героя.",
        "question": "Как лучше обработать возможный null после десериализации?",
        "type": "choose_fix",
        "code": """string json = File.ReadAllText(\"hero.json\");
HeroSave save = JsonSerializer.Deserialize<HeroSave>(json);

Console.WriteLine(save.Name);""",
        "options": [
            {
                "id": 1,
                "text": "HeroSave? save = JsonSerializer.Deserialize<HeroSave>(json); Console.WriteLine(save?.Name ?? \"Неизвестный герой\");",
            },
            {
                "id": 2,
                "text": "HeroSave save = JsonSerializer.Deserialize<HeroSave>(json)!; Console.WriteLine(save.Name);",
            },
            {
                "id": 3,
                "text": "var save = json.ToString(); Console.WriteLine(save.Name);",
            },
            {
                "id": 4,
                "text": "HeroSave save = new(); JsonSerializer.Serialize(save);",
            },
        ],
        "correct_option_id": 1,
        "success_message": "Даже пустая летопись теперь не уничтожит имя героя!",
        "error_message": "Оператор ! подавляет предупреждение, но не заменяет проверку результата.",
        "explanation": "Deserialize<T> может вернуть null. Nullable-переменная, ?. и запасное значение через ?? устраняют риск обращения к пустой ссылке. Повреждённый JSON отдельно обрабатывается через JsonException.",
    },
    {
        "id": 46,
        "topic_id": 12,
        "story": "Летописец хочет сохранить JSON так, чтобы его могли прочитать не только машины, но и уставшие после похода люди.",
        "question": "Какая настройка JsonSerializer добавляет отступы и переносы строк?",
        "type": "single_choice",
        "options": [
            {
                "id": 1,
                "text": "PropertyNameCaseInsensitive = true",
            },
            {
                "id": 2,
                "text": "IncludeFields = false",
            },
            {
                "id": 3,
                "text": "WriteIndented = true",
            },
            {
                "id": 4,
                "text": "DefaultIgnoreCondition = Never",
            },
        ],
        "correct_option_id": 3,
        "success_message": "Летопись получила аккуратные строки и достойные отступы!",
        "error_message": "Нужна настройка, отвечающая именно за форматирование записи.",
        "explanation": "JsonSerializerOptions.WriteIndented = true включает форматированный JSON с отступами и переносами. Эта настройка не меняет сами данные.",
    },
]
