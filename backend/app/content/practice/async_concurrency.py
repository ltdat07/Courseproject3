"""Асинхронность и многопоточность."""

TASKS = [
    {
        "id": 22,
        "topic_id": 8,
        "story": "Финальный маг произносит async и ждёт появления нового потока. Новый поток не приходит, потому что его никто не приглашал.",
        "question": "Что выведет программа?",
        "type": "code_output",
        "code": """static async Task SpellAsync()
{
    Console.Write(\"A\");
    await Task.CompletedTask;
    Console.Write(\"B\");
}

Console.Write(\"1\");
await SpellAsync();
Console.Write(\"2\");""",
        "options": [
            {
                "id": 1,
                "text": "12AB",
            },
            {
                "id": 2,
                "text": "1A2B",
            },
            {
                "id": 3,
                "text": "1AB2",
            },
            {
                "id": 4,
                "text": "Порядок всегда случайный",
            },
        ],
        "correct_option_id": 3,
        "success_message": "Верно: завершённый Task не заставил метод сделать паузу.",
        "error_message": "Task.CompletedTask уже завершён, а async не создаёт поток автоматически.",
        "explanation": "await видит уже завершённую задачу и продолжает синхронно. Поэтому вывод получается 1AB2.",
    },
    {
        "id": 23,
        "topic_id": 8,
        "story": "Десять тысяч наёмников одновременно кладут монеты в один сундук. Операция coins++ внезапно оказывается не такой цельной, как казалось.",
        "question": "Как безопасно увеличить общий счётчик в параллельных итерациях?",
        "type": "choose_fix",
        "code": """int coins = 0;
Parallel.For(0, 10_000, _ => coins++);""",
        "options": [
            {
                "id": 1,
                "text": "Interlocked.Increment(ref coins);",
            },
            {
                "id": 2,
                "text": "coins = coins + 1;",
            },
            {
                "id": 3,
                "text": "lock (new object()) { coins++; }",
            },
            {
                "id": 4,
                "text": "Thread.Sleep(1); coins++;",
            },
        ],
        "correct_option_id": 1,
        "success_message": "Interlocked пересчитал монеты без потерь и двойной бухгалтерии.",
        "error_message": "Нужна общая атомарная операция, а не новая блокировка для каждой итерации.",
        "explanation": "coins++ состоит из чтения, изменения и записи. Interlocked.Increment выполняет увеличение атомарно.",
    },
    {
        "id": 24,
        "topic_id": 8,
        "story": "Финальный босс запер две двери. Каждый страж держит один ключ и бесконечно ждёт второй. Очень злодейски, но не очень продуктивно.",
        "question": "Какая проблема может возникнуть?",
        "type": "find_error",
        "code": """object gateA = new();
object gateB = new();

void OpenFirst()
{
    lock (gateA)
    {
        Thread.Sleep(10);
        lock (gateB) { }
    }
}

void OpenSecond()
{
    lock (gateB)
    {
        Thread.Sleep(10);
        lock (gateA) { }
    }
}

Parallel.Invoke(OpenFirst, OpenSecond);""",
        "options": [
            {
                "id": 1,
                "text": "Возможен deadlock из-за разного порядка захвата блокировок",
            },
            {
                "id": 2,
                "text": "new() возвращает null и вызовет NullReferenceException",
            },
            {
                "id": 3,
                "text": "Компилятор запрещает вложенные блоки lock",
            },
            {
                "id": 4,
                "text": "Thread.Sleep автоматически освобождает блокировку",
            },
        ],
        "correct_option_id": 1,
        "success_message": "Deadlock раскрыт. Цитадель пала под единым порядком блокировок!",
        "error_message": "Проследи, какой gate удерживает каждый поток и какой ждёт.",
        "explanation": "Один поток может удерживать gateA и ждать gateB, пока другой удерживает gateB и ждёт gateA. Блокировки нужно захватывать в одинаковом порядке.",
    },
    {
        "id": 48,
        "topic_id": 8,
        "story": "Два независимых гонца отправляются за свитками. Архимаг хочет ожидать их одновременно, а не посылать второго лишь после возвращения первого.",
        "question": "Как правильно дождаться двух уже запущенных независимых задач?",
        "type": "single_choice",
        "options": [
            {
                "id": 1,
                "text": "Task first = LoadFirstAsync(); Task second = LoadSecondAsync(); await Task.WhenAll(first, second);",
            },
            {
                "id": 2,
                "text": "LoadFirstAsync().Wait(); LoadSecondAsync().Wait();",
            },
            {
                "id": 3,
                "text": "await Task.Delay(0);",
            },
            {
                "id": 4,
                "text": "async void LoadBoth() { }",
            },
        ],
        "correct_option_id": 1,
        "success_message": "Оба гонца отправились сразу и вернулись под наблюдением WhenAll!",
        "error_message": "Сначала запусти обе задачи, затем асинхронно дождись их вместе.",
        "explanation": "Task.WhenAll создаёт задачу, завершающуюся после всех переданных операций. Wait блокирует поток, а пустой async void не организует ожидание.",
    },
]
