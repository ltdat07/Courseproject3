"""Практические задания для ИИ-наставника.

Эталонные решения хранятся только на сервере и не попадают в публичный API.
"""

AI_PRACTICES = [
    {
        "id": "safe_division",
        "topic_title": "Основы C# и исключения",
        "title": "Зелье точного деления",
        "story": (
            "Алхимик Делимус снова получил 2 вместо 2.5 и обвиняет луну. "
            "Исправь формулу и защити котёл от деления на ноль."
        ),
        "assignment": (
            "Реализуй метод Divide(int a, int b). Он должен возвращать точный "
            "результат типа double. Если b равен нулю, выброси "
            "DivideByZeroException с понятным сообщением. Примеры: Divide(5, 2) "
            "возвращает 2.5, Divide(-5, 2) возвращает -2.5."
        ),
        "starter_code": (
            "static double Divide(int a, int b)\n"
            "{\n"
            "    // Напиши решение здесь\n"
            "}"
        ),
        "reference_solution": (
            "static double Divide(int a, int b)\n"
            "{\n"
            "    if (b == 0)\n"
            "    {\n"
            "        throw new DivideByZeroException(\"Делитель не может быть равен нулю.\");\n"
            "    }\n\n"
            "    return (double)a / b;\n"
            "}"
        ),
        "evaluation_criteria": [
            "вычисляется дробное деление, например Divide(5, 2) == 2.5 и Divide(-5, 2) == -2.5",
            "при b == 0 явно выбрасывается DivideByZeroException с понятным сообщением",
            "метод принимает два int и возвращает double",
        ],
    },
    {
        "id": "find_max",
        "topic_title": "Методы и массивы",
        "title": "Поиск сильнейшей руны",
        "story": (
            "В сундуке лежит массив рун. Совет магов требует найти самую "
            "сильную, но запрещает надеяться, что все значения положительные."
        ),
        "assignment": (
            "Реализуй метод FindMax(int[] numbers) без LINQ. Для null или "
            "пустого массива выброси ArgumentException. Для остальных массивов "
            "верни наибольшее значение, включая случаи только с отрицательными числами."
        ),
        "starter_code": (
            "static int FindMax(int[] numbers)\n"
            "{\n"
            "    // Напиши решение здесь\n"
            "}"
        ),
        "reference_solution": (
            "static int FindMax(int[] numbers)\n"
            "{\n"
            "    if (numbers is null || numbers.Length == 0)\n"
            "    {\n"
            "        throw new ArgumentException(\"Массив не должен быть пустым.\", nameof(numbers));\n"
            "    }\n\n"
            "    int max = numbers[0];\n"
            "    for (int i = 1; i < numbers.Length; i++)\n"
            "    {\n"
            "        if (numbers[i] > max)\n"
            "        {\n"
            "            max = numbers[i];\n"
            "        }\n"
            "    }\n\n"
            "    return max;\n"
            "}"
        ),
        "evaluation_criteria": [
            "null и пустой массив обрабатываются до чтения первого элемента",
            "начальное максимальное значение берётся из массива, а не равно нулю",
            "цикл проверяет все оставшиеся элементы",
            "метод возвращает найденное максимальное значение",
            "решение не использует LINQ",
        ],
    },
    {
        "id": "hero_damage",
        "topic_title": "Классы и ООП",
        "title": "Броня против отрицательного здоровья",
        "story": (
            "После встречи с драконом здоровье героя стало −37. Лекарь говорит, "
            "что это уже не баг, а некромантия. Наведи порядок в классе Hero."
        ),
        "assignment": (
            "Создай класс Hero со свойствами Name (только чтение извне) и Health "
            "(изменяется только внутри класса). Конструктор принимает имя и начальное "
            "здоровье (отрицательное начальное значение замени на ноль). "
            "Метод TakeDamage(int damage) уменьшает здоровье, но не ниже нуля. "
            "Отрицательный урон должен приводить к ArgumentOutOfRangeException."
        ),
        "starter_code": (
            "public class Hero\n"
            "{\n"
            "    // Добавь свойства, конструктор и TakeDamage\n"
            "}"
        ),
        "reference_solution": (
            "public class Hero\n"
            "{\n"
            "    public string Name { get; }\n"
            "    public int Health { get; private set; }\n\n"
            "    public Hero(string name, int health)\n"
            "    {\n"
            "        Name = name;\n"
            "        Health = Math.Max(0, health);\n"
            "    }\n\n"
            "    public void TakeDamage(int damage)\n"
            "    {\n"
            "        if (damage < 0)\n"
            "        {\n"
            "            throw new ArgumentOutOfRangeException(nameof(damage));\n"
            "        }\n\n"
            "        Health = Math.Max(0, Health - damage);\n"
            "    }\n"
            "}"
        ),
        "evaluation_criteria": [
            "Name нельзя изменить извне после создания объекта",
            "Health имеет закрытый setter",
            "конструктор задаёт имя и не допускает отрицательное начальное здоровье",
            "TakeDamage отклоняет отрицательный урон",
            "после урона Health не опускается ниже нуля",
        ],
    },
    {
        "id": "sum_even",
        "topic_title": "Условия и циклы",
        "title": "Налог на чётные кристаллы",
        "story": "Гоблин-сборщик принимает только чётные кристаллы. Долги тоже учитываются: отрицательные числа не освобождают от бухгалтерии.",
        "assignment": (
            "Реализуй long SumEven(int[] numbers) с помощью цикла, без LINQ. "
            "Верни сумму всех чётных элементов, включая отрицательные. Для пустого "
            "массива верни 0, для null выброси ArgumentNullException. Сумму накапливай "
            "в long, чтобы сложение больших int не переполняло int. "
            "Примеры: [2, 3, -4, 6] → 4; [1, 5] → 0; [2147483646, 2] → 2147483648."
        ),
        "starter_code": "static long SumEven(int[] numbers)\n{\n    // Собери чётные кристаллы\n}",
        "reference_solution": """static long SumEven(int[] numbers)
{
    if (numbers is null)
    {
        throw new ArgumentNullException(nameof(numbers));
    }
    long sum = 0;
    foreach (int number in numbers)
    {
        if (number % 2 == 0)
        {
            sum += number;
        }
    }
    return sum;
}""",
        "evaluation_criteria": [
            "null приводит к ArgumentNullException до обхода массива",
            "цикл суммирует только чётные числа, включая отрицательные, без LINQ",
            "пустой массив и массив без чётных элементов дают 0",
            "возвращается long и сумма [2147483646, 2] равна 2147483648 без переполнения int",
        ],
    },
    {
        "id": "count_words",
        "topic_title": "Строки",
        "title": "Перепись слов заклинания",
        "story": "Писарь считает пробелы за отдельные заклинания. Его отчёт выглядит внушительно, но магии в нём подозрительно мало.",
        "assignment": (
            "Реализуй int CountWords(string text). Слово — непустой фрагмент между "
            "разделителями: обычным пробелом, табуляцией \\t, возвратом каретки \\r "
            "или переводом строки \\n. Несколько разделителей подряд не создают слов. "
            "Для null, пустой строки или строки из этих разделителей верни 0. "
            "Знаки препинания и дефисы внутри фрагмента не разделяют слова. "
            "Примеры: \"  огонь   и лёд  \" → 3; \"маг\\tдракон\\nмеч\" → 3; \"маг-стажёр\" → 1."
        ),
        "starter_code": "static int CountWords(string text)\n{\n    // Пересчитай слова, а не пробелы\n}",
        "reference_solution": """static int CountWords(string text)
{
    if (text is null)
    {
        return 0;
    }
    char[] separators = { ' ', '\\t', '\\r', '\\n' };
    return text.Split(separators, StringSplitOptions.RemoveEmptyEntries).Length;
}""",
        "evaluation_criteria": [
            "null и пустая строка дают 0 без исключения",
            "разделителями считаются пробел, табуляция, возврат каретки и перевод строки",
            "повторные разделители и разделители по краям не создают лишних слов",
            "знаки препинания и дефисы не делят непустой фрагмент на несколько слов",
        ],
    },
    {
        "id": "parse_level",
        "topic_title": "Преобразование типов и проверка ввода",
        "title": "Паспорт начинающего героя",
        "story": "Каждый второй гоблин пишет в анкете уровень «легендарный». Стражу нужен int, а не уверенность в себе.",
        "assignment": (
            "Реализуй int ParseLevel(string text) через int.TryParse. Допустимы целые "
            "уровни от 1 до 100 включительно. Если строку нельзя преобразовать в int "
            "или число вне диапазона, верни 1 без исключения. Пробелы по краям "
            "допускаются. Примеры: \" 42 \" → 42; \"100\" → 100; \"0\", \"101\", "
            "\"маг\", \"2.5\", \"2147483648\", пустая строка и null → 1."
        ),
        "starter_code": "static int ParseLevel(string text)\n{\n    // Проверь паспорт героя\n}",
        "reference_solution": """static int ParseLevel(string text)
{
    if (int.TryParse(text, out int level) && level >= 1 && level <= 100)
    {
        return level;
    }
    return 1;
}""",
        "evaluation_criteria": [
            "преобразование выполняется через int.TryParse",
            "границы 1 и 100 включены, допустимые значения возвращаются без изменения",
            "null, пустая строка, нечисловой текст и переполнение int дают 1 без исключения",
            "числа вне диапазона дают 1, пробелы по краям допустимого числа не мешают разбору",
        ],
    },
    {
        "id": "count_loot",
        "topic_title": "Коллекции и Dictionary",
        "title": "Инвентаризация драконьего склада",
        "story": "Дракон помнит каждую монету, но потерял счёт мечам. Наведи порядок, пока он не назначил тебя главным сокровищем.",
        "assignment": (
            "Реализуй Dictionary<string, int> CountLoot(string[] items): ключ — название "
            "предмета, значение — число его появлений. Перед подсчётом убирай пробелы "
            "по краям названия через Trim. Пропускай null и пустые/пробельные названия. "
            "Регистр важен: \"меч\" и \"Меч\" — разные ключи (Ordinal). Для null вместо "
            "массива выброси ArgumentNullException, для пустого массива верни пустой словарь. "
            "Пример: [\"меч\", \" меч \", \"щит\", null, \" \" ] → {\"меч\": 2, \"щит\": 1}. "
            "Порядок ключей не важен; исходный массив менять нельзя."
        ),
        "starter_code": "static Dictionary<string, int> CountLoot(string[] items)\n{\n    // Заполни складскую книгу\n}",
        "reference_solution": """static Dictionary<string, int> CountLoot(string[] items)
{
    if (items is null)
    {
        throw new ArgumentNullException(nameof(items));
    }
    var counts = new Dictionary<string, int>(StringComparer.Ordinal);
    foreach (string item in items)
    {
        if (string.IsNullOrWhiteSpace(item))
        {
            continue;
        }
        string name = item.Trim();
        counts.TryGetValue(name, out int count);
        counts[name] = count + 1;
    }
    return counts;
}""",
        "evaluation_criteria": [
            "null вместо массива вызывает ArgumentNullException, пустой массив даёт пустой Dictionary<string, int>",
            "null, пустые и пробельные элементы пропускаются; остальные названия обрабатываются через Trim",
            "каждое повторение увеличивает счётчик, сравнение названий порядковое с учётом регистра",
            "метод возвращает словарь подсчётов и не изменяет исходный массив",
        ],
    },
    {
        "id": "positive_runes",
        "topic_title": "LINQ и обработка данных",
        "title": "Сито благословлённых рун",
        "story": "Архимаг просит положительные руны по возрастанию и без копий. Отрицательные руны оставь отделу проклятий.",
        "assignment": (
            "Реализуй int[] PositiveRunes(int[] numbers) с использованием LINQ. "
            "Верни массив уникальных чисел строго больше нуля, отсортированных по "
            "возрастанию. Исходный массив не изменяй. Для null выброси "
            "ArgumentNullException. Пустой массив или отсутствие положительных чисел "
            "дают пустой массив. Пример: [3, -1, 2, 3, 0, 1] → [1, 2, 3]."
        ),
        "starter_code": "static int[] PositiveRunes(int[] numbers)\n{\n    // Отфильтруй, убери повторы и упорядочи руны\n}",
        "reference_solution": """static int[] PositiveRunes(int[] numbers)
{
    if (numbers is null)
    {
        throw new ArgumentNullException(nameof(numbers));
    }
    return numbers.Where(number => number > 0)
        .Distinct()
        .OrderBy(number => number)
        .ToArray();
}""",
        "evaluation_criteria": [
            "null вызывает ArgumentNullException до обращения к LINQ",
            "с помощью LINQ выбираются только числа строго больше нуля",
            "результат не содержит повторов и отсортирован по возрастанию",
            "возвращается int[], исходный массив не изменён; при отсутствии подходящих чисел результат пустой",
        ],
    },
    {
        "id": "sum_rewards_async",
        "topic_title": "Async/await",
        "title": "Два курьера — одна награда",
        "story": "Два курьера уже несут награды. Не замораживай всё королевство, пока ждёшь их у ворот.",
        "assignment": (
            "Реализуй async Task<int> SumRewardsAsync(Task<int> first, Task<int> second). "
            "Обе задачи уже запущены: асинхронно дождись обеих через Task.WhenAll "
            "и верни сумму результатов. Сумма гарантированно помещается в int. "
            "Если любой аргумент null, выброси ArgumentNullException до ожидания задач. "
            "Если задача завершилась с ошибкой, не скрывай исключение и не возвращай "
            "фиктивный результат. Не используй .Result, .Wait() или Task.Run. "
            "Пример: Task.FromResult(7) и Task.FromResult(5) → 12."
        ),
        "starter_code": "static async Task<int> SumRewardsAsync(Task<int> first, Task<int> second)\n{\n    // Дождись курьеров, не блокируя поток\n}",
        "reference_solution": """static async Task<int> SumRewardsAsync(Task<int> first, Task<int> second)
{
    if (first is null)
    {
        throw new ArgumentNullException(nameof(first));
    }
    if (second is null)
    {
        throw new ArgumentNullException(nameof(second));
    }
    int[] rewards = await Task.WhenAll(first, second);
    return rewards[0] + rewards[1];
}""",
        "evaluation_criteria": [
            "метод принимает два Task<int> и возвращает Task<int>; null проверяется до ожидания и даёт ArgumentNullException",
            "обе задачи ожидаются через await Task.WhenAll без .Result, .Wait() и Task.Run",
            "возвращается сумма результатов двух задач, в том числе если они завершились в обратном порядке",
            "ошибка входной задачи не скрывается и не подменяется результатом 0",
        ],
    },
]


def get_ai_practice(practice_id: str) -> dict[str, object] | None:
    return next(
        (practice for practice in AI_PRACTICES if practice["id"] == practice_id),
        None,
    )


def get_public_ai_practices() -> list[dict[str, object]]:
    public_fields = (
        "id",
        "topic_title",
        "title",
        "story",
        "assignment",
        "starter_code",
    )
    return [
        {field: practice[field] for field in public_fields}
        for practice in AI_PRACTICES
    ]
