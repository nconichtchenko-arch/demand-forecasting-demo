import pandas as pd
import numpy as np
import supplycm.forecasting as f
import matplotlib.pyplot as plt

# Загружаем данные
df = pd.read_csv('data/daily_revenue.csv', parse_dates=['order_date'])
df = df.sort_values('order_date').reset_index(drop=True)

# Берем последние 30 дней как "тест" (то, что мы будем предсказывать)
train = df.iloc[:-30].copy()
test = df.iloc[-30:].copy()

# Список значений (для алгоритмов)
train_values = train['revenue'].tolist()

print(f"Обучающая выборка: {len(train)} дней, Тестовая: {len(test)} дней")

# 1. Простое скользящее среднее (окно 7 дней)
# Для прогноза на 30 дней вперед используем последнее значение
last_ma = f.simple_moving_average(train_values, window=7)[-1]
forecast_ma = [last_ma] * len(test)

# 2. Метод Хольта-Винтерса (сезонность 7 дней)
# Возвращает (сглаженные значения, тренд, сезонность)
hw_level, hw_trend, hw_season = f.holt_winters(train_values, season_length=7)
# Берем последнее значение как прогноз (плоский прогноз)
last_hw = hw_level[-1]
forecast_hw = [last_hw] * len(test)

# 3. Метод Кростона (для "рваного" спроса)
# Возвращает (сглаженный спрос, сглаженный интервал)
croston_demand, croston_interval = f.crostons_method(train_values)
# Прогноз Кростона = спрос / интервал (но упростим — берем последнее значение спроса)
last_croston = croston_demand[-1]
forecast_croston = [last_croston] * len(test)

# Оценка точности (MAPE)
def mape(actual, forecast):
    actual = np.array(actual)
    forecast = np.array(forecast)
    mask = actual != 0
    return np.mean(np.abs((actual[mask] - forecast[mask]) / actual[mask])) * 100

print(f"MAPE (Moving Average): {mape(test['revenue'], forecast_ma):.2f}%")
print(f"MAPE (Holt-Winters): {mape(test['revenue'], forecast_hw):.2f}%")
print(f"MAPE (Croston): {mape(test['revenue'], forecast_croston):.2f}%")

# График
plt.figure(figsize=(12, 6))
plt.plot(test['order_date'], test['revenue'], label='Факт', color='black', linewidth=2)
plt.plot(test['order_date'], forecast_ma, label='Moving Average', linestyle='--')
plt.plot(test['order_date'], forecast_hw, label='Holt-Winters', linestyle='--')
plt.plot(test['order_date'], forecast_croston, label='Croston', linestyle='--')
plt.title('Прогноз спроса на 30 дней (сравнение методов)')
plt.xlabel('Дата')
plt.ylabel('Выручка')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('data/forecast_comparison.png')
plt.show()