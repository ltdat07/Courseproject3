"""Условия и циклы."""

TASKS = [
    {
        "id": 4,
        "topic_id": 2,
        "story": "У героя осталось мало здоровья, но щит всё ещё бодр и требует признания своих заслуг.",
        "question": "Что выведет программа?",
        "type": "code_output",
        "code": """int health = 40;
bool hasShield = true;

if (health < 50 && hasShield)
{
    Console.WriteLine(\"Щит спас героя\");
}
else
{
    Console.WriteLine(\"Пора бежать\");
}""",
        "options": [
            {
                "id": 1,
                "text": "Щит спас героя",
            },
            {
                "id": 2,
                "text": "Пора бежать",
            },
            {
                "id": 3,
                "text": "Обе строки",
            },
            {
                "id": 4,
                "text": "Ничего",
            },
        ],
        "correct_option_id": 1,
        "success_message": "Щит торжественно записал этот подвиг в резюме.",
        "error_message": "Проверь обе части выражения, соединённые оператором &&.",
        "explanation": "health < 50 истинно и hasShield равен true. Для && нужны оба истинных условия, поэтому выполняется первый блок.",
    },
    {
        "id": 5,
        "topic_id": 2,
        "story": "Телепорт switch открыл сразу несколько маршрутов и получил выговор от компилятора за незаконный переход между мирами.",
        "question": "Как исправить код, чтобы выполнялась только выбранная ветвь?",
        "type": "choose_fix",
        "code": """int door = 2;

switch (door)
{
    case 1:
        Console.WriteLine(\"Лес\");
    case 2:
        Console.WriteLine(\"Замок\");
    default:
        Console.WriteLine(\"Туман\");
}""",
        "options": [
            {
                "id": 1,
                "text": "Добавить break; после каждого Console.WriteLine(...)",
            },
            {
                "id": 2,
                "text": "Заменить switch на while",
            },
            {
                "id": 3,
                "text": "Удалить все case и оставить только default",
            },
            {
                "id": 4,
                "text": "Изменить int door на string door",
            },
        ],
        "correct_option_id": 1,
        "success_message": "Маршруты разделены. Телепорт снова получил лицензию!",
        "error_message": "Компилятор не разрешает непустой case просто продолжить следующим.",
        "explanation": "Каждая непустая секция switch должна завершать управление, например через break. Тогда при door == 2 выполнится только case 2.",
    },
    {
        "id": 6,
        "topic_id": 2,
        "story": "Лестница обещала три ступени, но герой прошёл уже четыреста и начал подозревать бесконечную аренду.",
        "question": "Почему цикл не завершается?",
        "type": "find_error",
        "code": """int steps = 3;

while (steps > 0)
{
    Console.WriteLine(steps);
}""",
        "options": [
            {
                "id": 1,
                "text": "Переменная steps не изменяется внутри цикла",
            },
            {
                "id": 2,
                "text": "Console.WriteLine нельзя вызывать в while",
            },
            {
                "id": 3,
                "text": "Тип int нельзя сравнивать с нулём",
            },
            {
                "id": 4,
                "text": "while всегда выполняется ровно один раз",
            },
        ],
        "correct_option_id": 1,
        "success_message": "Добавлено steps--. Лестница снова подчиняется геометрии!",
        "error_message": "Посмотри, может ли условие steps > 0 когда-нибудь стать ложным.",
        "explanation": "steps остаётся равным 3, поэтому условие всегда истинно. В теле цикла нужно изменять значение, например выполнить steps--.",
    },
    {
        "id": 39,
        "topic_id": 2,
        "story": "Смотритель рун решил проверить каждый элемент массива, но сделал ещё один героический шаг за его границу.",
        "question": "Почему цикл завершится исключением и как его исправить?",
        "type": "find_error",
        "code": """int[] runes = { 2, 4, 6 };

for (int i = 0; i <= runes.Length; i++)
{
    Console.WriteLine(runes[i]);
}""",
        "options": [
            {
                "id": 1,
                "text": "Массив нельзя перебирать циклом for.",
            },
            {
                "id": 2,
                "text": "Счётчик должен начинаться с единицы.",
            },
            {
                "id": 3,
                "text": "После WriteLine обязательно нужен break.",
            },
            {
                "id": 4,
                "text": "При i == runes.Length индекс недопустим; нужно условие i < runes.Length.",
            },
        ],
        "correct_option_id": 4,
        "success_message": "Смотритель остановился у последней руны и не шагнул в пустоту!",
        "error_message": "Последний индекс массива на единицу меньше его Length.",
        "explanation": "Для массива из трёх элементов допустимы индексы 0, 1 и 2. Условие <= допускает i == 3 и вызывает IndexOutOfRangeException.",
    },
    {
        "id": 50,
        "topic_id": 2,
        "story": "Сборщик очков пропускает второй зал, прекращает поход перед пятым, а номера остальных залов складывает в общий счёт.",
        "question": "Что выведет программа?",
        "type": "code_output",
        "code": """int score = 0;

for (int i = 1; i <= 5; i++)
{
    if (i == 2) continue;
    if (i == 5) break;
    score += i;
}

Console.WriteLine(score);""",
        "options": [
            {
                "id": 1,
                "text": "6",
            },
            {
                "id": 2,
                "text": "10",
            },
            {
                "id": 3,
                "text": "8",
            },
            {
                "id": 4,
                "text": "13",
            },
        ],
        "correct_option_id": 3,
        "success_message": "Маршрут просчитан: посещены залы 1, 3 и 4.",
        "error_message": "continue пропускает остаток текущей итерации, break завершает цикл.",
        "explanation": "При i = 2 сложение пропускается. При i = 5 цикл завершается до сложения. В score попадают 1, 3 и 4, поэтому результат равен 8.",
    },
]
