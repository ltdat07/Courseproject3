"""Методы."""

TASKS = [
    {
        "id": 7,
        "topic_id": 3,
        "story": "Кузнец методов просит формулу сложения. В прошлый раз ученик вернул void, и казна получила буквально ничего.",
        "question": "Какой метод корректно принимает два int и возвращает их сумму?",
        "type": "single_choice",
        "options": [
            {
                "id": 1,
                "text": "static int Add(int a, int b) { return a + b; }",
            },
            {
                "id": 2,
                "text": "static void Add(int a, int b) { return a + b; }",
            },
            {
                "id": 3,
                "text": "static int Add(a, b) { a + b; }",
            },
            {
                "id": 4,
                "text": "static string Add(int a, int b) { return a + b; }",
            },
        ],
        "correct_option_id": 1,
        "success_message": "Формула принята. Кузница официально производит суммы!",
        "error_message": "Сверь тип результата, типы параметров и наличие return.",
        "explanation": "Метод объявлен с типом результата int, принимает два параметра int и возвращает выражение типа int.",
    },
    {
        "id": 8,
        "topic_id": 3,
        "story": "Заклинание усиливает копию характеристики. Оригинал тем временем делает вид, что его это не касается.",
        "question": "Какие две строки выведет программа?",
        "type": "code_output",
        "code": """static int Upgrade(int power)
{
    power += 2;
    return power * 2;
}

int power = 3;

Console.WriteLine(Upgrade(power));
Console.WriteLine(power);""",
        "options": [
            {
                "id": 1,
                "text": "10, затем 3",
            },
            {
                "id": 2,
                "text": "10, затем 5",
            },
            {
                "id": 3,
                "text": "6, затем 3",
            },
            {
                "id": 4,
                "text": "Ошибка компиляции",
            },
        ],
        "correct_option_id": 1,
        "success_message": "Копия характеристики прокачана, оригинал не пострадал.",
        "error_message": "Параметр int без ref получает копию переданного значения.",
        "explanation": "Внутри Upgrade локальная копия power становится 5, и метод возвращает 10. Внешняя переменная power остаётся равной 3.",
    },
    {
        "id": 9,
        "topic_id": 3,
        "story": "Кузнец создал урон внутри мастерской, но попытался вынести переменную наружу без пропуска.",
        "question": "Почему код не компилируется?",
        "type": "find_error",
        "code": """static void Forge()
{
    int damage = 12;
}

Forge();
Console.WriteLine(damage);""",
        "options": [
            {
                "id": 1,
                "text": "damage существует только внутри метода Forge",
            },
            {
                "id": 2,
                "text": "Метод void нельзя вызывать",
            },
            {
                "id": 3,
                "text": "Console.WriteLine не умеет выводить int",
            },
            {
                "id": 4,
                "text": "Метод обязательно должен называться Main",
            },
        ],
        "correct_option_id": 1,
        "success_message": "Граница области видимости найдена. Контрабанда переменных остановлена!",
        "error_message": "Проверь, внутри каких фигурных скобок объявлена damage.",
        "explanation": "Локальная переменная damage доступна только в теле Forge. Чтобы использовать значение снаружи, метод может вернуть его через return.",
    },
    {
        "id": 40,
        "topic_id": 3,
        "story": "Алхимик усилил копию показателя силы внутри метода и удивился, почему настоящий герой не почувствовал изменений.",
        "question": "Что выведет программа?",
        "type": "code_output",
        "code": """static void Boost(int power)
{
    power += 5;
}

int power = 10;
Boost(power);

Console.WriteLine(power);""",
        "options": [
            {
                "id": 1,
                "text": "10",
            },
            {
                "id": 2,
                "text": "15",
            },
            {
                "id": 3,
                "text": "5",
            },
            {
                "id": 4,
                "text": "Ошибка компиляции",
            },
        ],
        "correct_option_id": 1,
        "success_message": "Верно! Усилена только локальная копия параметра.",
        "error_message": "Обычный параметр int передаётся методу по значению.",
        "explanation": "Boost получает копию числа 10. Изменение параметра power внутри метода не влияет на переменную вызывающего кода. Метод мог бы вернуть новое значение или принять параметр ref.",
    },
    {
        "id": 51,
        "topic_id": 3,
        "story": "Метод обещает всегда вернуть целую награду, но для героя без бонуса молча доходит до конца свитка.",
        "question": "Почему метод не компилируется и как его исправить?",
        "type": "find_error",
        "code": """static int GetReward(bool hasBonus)
{
    if (hasBonus)
    {
        return 20;
    }
}""",
        "options": [
            {
                "id": 1,
                "text": "Методы не могут возвращать int.",
            },
            {
                "id": 2,
                "text": "Параметр bool нужно передавать с ref.",
            },
            {
                "id": 3,
                "text": "Следует заменить return на break.",
            },
            {
                "id": 4,
                "text": "Не все пути возвращают значение; после if нужно добавить, например, return 0.",
            },
        ],
        "correct_option_id": 4,
        "success_message": "Теперь метод выдаёт ответ и героям без бонуса!",
        "error_message": "Метод с типом int обязан вернуть число на каждом возможном пути.",
        "explanation": "Когда hasBonus равен false, блок if пропускается и выполнение достигает конца метода без return. Добавление return 0 после if закрывает этот путь.",
    },
]
