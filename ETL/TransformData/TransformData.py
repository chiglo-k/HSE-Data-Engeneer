import pandas as pd
import heapq
from dataclasses import dataclass
from typing import List
from datetime import datetime as dt


@dataclass
class WeatherAnalyse:

    data_temp: pd.DataFrame

    def __filter_out_in(self):
        """Отфильтруйте out/in = in;"""
        self.data_temp['out/in'] = self.data_temp['out/in'].eq('in')
        self.__transform_date(self.data_temp)

    def __transform_date(self, data_temp:pd.DataFrame):
        """Поле noted_date переведите в формат
        ‘yyyy-MM-dd’ с типом данных date;
        """
        self.data_temp['noted_date'] = (pd.to_datetime(self.data_temp['noted_date'], format='%d-%m-%Y %H:%M')
                                   .dt.date)

        self.__clear_duplicates(self.data_temp)

    def __clear_duplicates(self,data_temp:pd.DataFrame):
        """Удаление дубликатов по дню наблюдения"""
        self.data_temp = self.data_temp.drop_duplicates(subset='noted_date')

        self.__clear_5_95_quantile(self.data_temp)

    def __clear_5_95_quantile(self, data_temp:pd.DataFrame):
        """Очистка температуры по 5-му и 95-му квантилю."""
        qu_5 = self.data_temp['temp'].quantile(0.05)
        qu_95 = self.data_temp['temp'].quantile(0.95)
        self.data_temp = self.data_temp.query(f"{qu_5} < temp < {qu_95}")

    def run(self):
        self.__filter_out_in()


class OutputWeather(WeatherAnalyse):

    def most_min_temperature(self)->str:
        """5 самых жарких и самых холодных дней за весну;"""
        hottest_days: List[str] = self.data_temp.nlargest(5, 'temp')['noted_date'].astype(str).values.tolist()
        coldest_days: List[str] = self.data_temp.nsmallest(5, 'temp')['noted_date'].astype(str).values.tolist()
        print(f"5 самых жарких дней весны: {hottest_days}\n5 самых холодных дней весны: {coldest_days}")
    
    def run(self):
        super(OutputWeather, self).run()
        return  self.most_min_temperature()



weather_function = OutputWeather(data_temp=pd.read_csv("IOT-temp.csv"))
weather_function.run()
