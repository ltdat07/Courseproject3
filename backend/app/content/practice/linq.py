"""LINQ и работа с данными."""

TASKS = [
    {
        "id": 19,
        "topic_id": 7,
        "story": "Оракул получил четыре числа и обещал оставить чётные, поставить сильнейшие первыми и увеличить их в десять раз.",
        "question": "Что выведет программа?",
        "type": "code_output",
        "code": """int[] values = { 5, 2, 4, 1 };

var result = values
    .Where(x => x % 2 == 0)
    .OrderByDescending(x => x)
    .Select(x => x * 10);

Console.WriteLine(string.Join(\", \", result));""",
        "options": [
            {
                "id": 1,
                "text": "20, 40",
            },
            {
                "id": 2,
                "text": "40, 20",
            },
            {
                "id": 3,
                "text": "5, 4, 2, 1",
            },
            {
                "id": 4,
                "text": "50, 20, 40, 10",
            },
        ],
        "correct_option_id": 2,
        "success_message": "Пророчество LINQ исполнено в правильном порядке.",
        "error_message": "Проследи цепочку Where → OrderByDescending → Select.",
        "explanation": "Where оставляет 2 и 4, сортировка даёт 4 и 2, а Select превращает их в 40 и 20.",
    },
    {
        "id": 20,
        "topic_id": 7,
        "story": "Писарь приказал OrderBy навести порядок, проигнорировал ответ и удивился, что исходный список остался прежним.",
        "question": "Почему список не стал отсортированным?",
        "type": "find_error",
        "code": """var scores = new List<int> { 30, 10, 20 };

scores.OrderBy(x => x);

Console.WriteLine(string.Join(\" \", scores));""",
        "options": [
            {
                "id": 1,
                "text": "OrderBy сортирует только по убыванию",
            },
            {
                "id": 2,
                "text": "Результат OrderBy был проигнорирован",
            },
            {
                "id": 3,
                "text": "LINQ нельзя применять к List<int>",
            },
            {
                "id": 4,
                "text": "LINQ сортирует в случайном порядке",
            },
        ],
        "correct_option_id": 2,
        "success_message": "Ответ Оракула сохранён, и числа наконец построились.",
        "error_message": "OrderBy не изменяет исходную коллекцию.",
        "explanation": "OrderBy возвращает новую последовательность. Нужно сохранить результат, например: var sorted = scores.OrderBy(x => x).ToList();",
    },
    {
        "id": 21,
        "topic_id": 7,
        "story": "Хронист хочет получить снимок отряда сейчас, чтобы позднее прибывшие герои не переписали историю.",
        "question": "Какой вариант немедленно создаст отдельный список?",
        "type": "single_choice",
        "options": [
            {
                "id": 1,
                "text": "var result = heroes.Where(h => h.Length > 3).ToList();",
            },
            {
                "id": 2,
                "text": "var result = heroes.Where(h => h.Length > 3);",
            },
            {
                "id": 3,
                "text": "var result = heroes.Select(h => h);",
            },
            {
                "id": 4,
                "text": "var result = heroes.OrderBy(h => h);",
            },
        ],
        "correct_option_id": 1,
        "success_message": "Хроника зафиксирована и больше не зависит от будущих пополнений.",
        "error_message": "Нужна операция, которая материализует последовательность прямо сейчас.",
        "explanation": "ToList() немедленно выполняет запрос и создаёт отдельный список. Остальные варианты обычно остаются отложенными последовательностями.",
    },
    {
        "id": 47,
        "topic_id": 7,
        "story": "Оракул оставляет только чётные числа, усиливает каждое в десять раз и складывает получившиеся значения.",
        "question": "Что выведет программа?",
        "type": "code_output",
        "code": """int[] numbers = { 1, 2, 3, 4 };

int result = numbers
    .Where(number => number % 2 == 0)
    .Select(number => number * 10)
    .Sum();

Console.WriteLine(result);""",
        "options": [
            {
                "id": 1,
                "text": "6",
            },
            {
                "id": 2,
                "text": "40",
            },
            {
                "id": 3,
                "text": "100",
            },
            {
                "id": 4,
                "text": "60",
            },
        ],
        "correct_option_id": 4,
        "success_message": "Оракул получил 60 и довольно закрыл журнал вычислений.",
        "error_message": "Сначала оставь 2 и 4, затем примени Select и только потом Sum.",
        "explanation": "Where оставляет 2 и 4. Select превращает их в 20 и 40, а Sum возвращает 60. Исходный массив при этом не меняется.",
    },
]
