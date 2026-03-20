import mlflow

MLFLOW_TRACKING_URI = "http://localhost:5000"
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

SENTIMENT_V1 = """\
Определи тональность следующего текста.
Ответь одним словом: positive, negative или neutral.

Текст: {{text}}
"""

SENTIMENT_V2 = """\
Ты — эксперт по анализу тональности текста.
Проанализируй приведённый текст и верни JSON:
{{"sentiment": "positive|negative|neutral", "confidence": 0.0-1.0}}

Текст: {{text}}
"""

SENTIMENT_V3 = """\
Ты — эксперт по анализу тональности на русском и английском языках.
Определи тональность текста с объяснением.

Текст: {{text}}

Ответ (JSON):
{{"sentiment": "positive|negative|neutral", "confidence": 0.0-1.0, "reason": "краткое объяснение"}}
"""

MODEL_DOC_V1 = """\
Напиши краткое описание ML-модели.
Метрики модели: {{metrics}}
"""

MODEL_DOC_V2 = """\
Ты — технический писатель для ML-команды.
Напиши структурированное описание модели для документации.

Название: {{model_name}}
Метрики: {{metrics}}
Дата обучения: {{train_date}}

Включи: назначение, ключевые метрики, ограничения.
"""


def main():
    print("=== MLflow Prompt Storage: регистрация промптов ===\n")
    
    print("Промпт: sentiment-analysis")
    p = mlflow.register_prompt(
        name="sentiment-analysis",
        template=SENTIMENT_V1,
        commit_message="v1: базовая версия — только тональность",
        tags={"task": "sentiment", "lang": "ru"},
    )
    print(f"version {p.version} — {p.commit_message}")

    p = mlflow.register_prompt(
        name="sentiment-analysis",
        template=SENTIMENT_V2,
        commit_message="v2: JSON-ответ с полем confidence",
        tags={"task": "sentiment", "lang": "ru"},
    )
    print(f"version {p.version} — {p.commit_message}")
    p = mlflow.register_prompt(
        name="sentiment-analysis",
        template=SENTIMENT_V3,
        commit_message="v3: JSON + объяснение, двуязычный (ru+en)",
        tags={"task": "sentiment", "lang": "ru+en"},
    )
    print(f"version {p.version} — {p.commit_message}")
    
    print("\nПромпт: model-documentation")
    p = mlflow.register_prompt(
        name="model-documentation",
        template=MODEL_DOC_V1,
        commit_message="v1: краткое описание модели",
        tags={"task": "documentation"},
    )
    print(f"version {p.version} — {p.commit_message}")

    p = mlflow.register_prompt(
        name="model-documentation",
        template=MODEL_DOC_V2,
        commit_message="v2: структурированная документация с полями",
        tags={"task": "documentation"},
    )
    print(f"version {p.version} — {p.commit_message}")
    print("\n── Проверка загрузки ──")
    loaded = mlflow.load_prompt("prompts:/sentiment-analysis/3")
    rendered = loaded.format(text="Сегодня отличный день!")
    print(f"sentiment-analysis@v3 загружен. Пример:\n{rendered}")

    print(f"\nГотово. Откройте: {MLFLOW_TRACKING_URI}/#/prompts")


if __name__ == "__main__":
    main()
