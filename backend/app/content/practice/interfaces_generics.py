"""Интерфейсы и обобщения."""

TASKS = [
    {
        "id": 31,
        "topic_id": 11,
        "story": "Гильдия принимает големов только по контракту IDamageable. Подпись должна совпасть до последнего параметра.",
        "question": "Какой класс корректно реализует показанный интерфейс?",
        "type": "single_choice",
        "code": """interface IDamageable
{
    void TakeDamage(int amount);
}""",
        "options": [
            {
                "id": 1,
                "text": "class Golem : IDamageable { void TakeDamage(int amount) { } }",
            },
            {
                "id": 2,
                "text": "class Golem : IDamageable { public int TakeDamage(int amount) => amount; }",
            },
            {
                "id": 3,
                "text": "class Golem : IDamageable { public void TakeDamage(string amount) { } }",
            },
            {
                "id": 4,
                "text": "class Golem : IDamageable { public void TakeDamage(int amount) { } }",
            },
        ],
        "correct_option_id": 4,
        "success_message": "Контракт подписан публично и без мелкого шрифта!",
        "error_message": "Проверь модификатор доступа, возвращаемый тип и тип параметра.",
        "explanation": "Обычная реализация должна быть public и точно повторять сигнатуру: void TakeDamage(int amount).",
    },
    {
        "id": 32,
        "topic_id": 11,
        "story": "Универсальный распределитель добычи не интересуется видом предмета: он всегда возвращает второй предложенный артефакт.",
        "question": "Что выведет программа?",
        "type": "code_output",
        "code": """static T Pick<T>(T first, T second)
{
    return second;
}

Console.WriteLine(Pick(\"меч\", \"щит\"));""",
        "options": [
            {
                "id": 1,
                "text": "меч",
            },
            {
                "id": 2,
                "text": "щит",
            },
            {
                "id": 3,
                "text": "T",
            },
            {
                "id": 4,
                "text": "Ошибка компиляции",
            },
        ],
        "correct_option_id": 2,
        "success_message": "Распределитель выбрал щит и сохранил его настоящий тип!",
        "error_message": "Компилятор выводит T как string, а метод возвращает второй аргумент.",
        "explanation": "Оба аргумента имеют тип string, поэтому T становится string. Метод возвращает second, то есть строку щит.",
    },
    {
        "id": 33,
        "topic_id": 11,
        "story": "Жрец обещал Гильдии умение исцелять без условий, но принёс метод с другим списком параметров.",
        "question": "Какой вариант исправит ошибку реализации интерфейса?",
        "type": "choose_fix",
        "code": """interface IHealer
{
    void Heal();
}

class Priest : IHealer
{
    public void Heal(int points)
    {
        Console.WriteLine($\"+{points} здоровья\");
    }
}""",
        "options": [
            {
                "id": 1,
                "text": "public void Heal() { Console.WriteLine(\"Исцеление\"); }",
            },
            {
                "id": 2,
                "text": "public int Heal() => 10;",
            },
            {
                "id": 3,
                "text": "private void Heal() { }",
            },
            {
                "id": 4,
                "text": "public void Heal(string target) { }",
            },
        ],
        "correct_option_id": 1,
        "success_message": "Жрец выполнил контракт без внезапных аргументов!",
        "error_message": "Метод интерфейса не принимает параметров, возвращает void и должен быть публичным.",
        "explanation": "Heal(int) — другой метод и не реализует Heal(). Первый вариант полностью совпадает с контрактом.",
    },
    {
        "id": 44,
        "topic_id": 11,
        "story": "Универсальный лекарь вызывает Heal у любого T, но компилятор не верит, что каждый возможный тип владеет таким методом.",
        "question": "Как исправить обобщённый метод?",
        "type": "find_error",
        "code": """static void Restore<T>(T target)
{
    target.Heal();
}""",
        "options": [
            {
                "id": 1,
                "text": "Добавить ограничение where T : IHealer, содержащее метод Heal().",
            },
            {
                "id": 2,
                "text": "Заменить T на var в списке параметров.",
            },
            {
                "id": 3,
                "text": "Добавить оператор new T() перед каждым вызовом.",
            },
            {
                "id": 4,
                "text": "Сделать метод async void.",
            },
        ],
        "correct_option_id": 1,
        "success_message": "Контракт подтвердил право лекаря вызывать Heal!",
        "error_message": "Компилятору нужно заранее сообщить, какие возможности имеет T.",
        "explanation": "Ограничение where T : IHealer гарантирует, что аргумент реализует интерфейс с методом Heal. После этого вызов становится типобезопасным.",
    },
]
