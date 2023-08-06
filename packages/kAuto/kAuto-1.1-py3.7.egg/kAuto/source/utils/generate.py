import calendar
import datetime
import random
import time
from urllib import parse

from utils.read_config import read_config


class Generate:
    # 生成随机车牌
    def random_carNo(self):
        city = ["京", "津", "沪", "渝", "蒙", "新", "藏", "宁", "桂", "港", "澳", "黑", "吉", "辽", "晋", "冀", "青", "鲁", "豫", "苏", "皖",
                "浙", "闽", "赣", "湘", "鄂", "粤", "琼", "甘", "陕", "黔", "滇", "川"]
        carNo = random.choice(city)
        after = ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
                 "U", "V", "W", "X", "Y", "Z", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
        for i in range(6):
            carNo = carNo + random.choice(after)

        return carNo

    # 生成随机车类型
    def random_carType(self) -> int:
        return random.randint(0, 4)

    # 生成当前时间
    def generate_localTime(self) -> str:
        in_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        in_time = datetime.datetime.strptime(in_time, "%Y-%m-%d %H:%M:%S")
        return str(in_time)

    # 调整时间
    def just_time(self, inTime, seconds=0, minutes=0, days=0) -> str:
        just = datetime.datetime.strptime(inTime, "%Y-%m-%d %H:%M:%S")
        if seconds != 0:
            return str(just + datetime.timedelta(seconds=seconds))
        if minutes != 0:
            return str(just + datetime.timedelta(minutes=minutes))
        if days != 0:
            return str(just + datetime.timedelta(days=days))

    # 生成当天时间零点
    def generate_day_start(self):
        day = self.generate_localTime()
        day = day.replace(day.split(" ")[1], "00:00:00")
        return day

    # 生成当天时间最后时间
    def generate_day_end(self):
        day = self.generate_localTime()
        day = day.replace(day.split(" ")[1], "23:59:59")
        return day

    # 当天
    def generate_today(self) -> str:
        return time.strftime('%Y-%m-%d', time.localtime(time.time()))

    # 生成当前月份
    def generate_current_month(self):
        return time.strftime('%Y-%m', time.localtime(time.time()))

    # 生成当前月份第一天
    def generate_current_month_first_day(self):
        t = datetime.date.today()
        return str(datetime.date(t.year, t.month, 1))

    def generate_current_month_last_day(self):
        t = datetime.date.today()
        first_day = datetime.date(t.year, t.month, 1)
        days_num = calendar.monthrange(first_day.year, first_day.month)[1]
        last_day_of_current_month = first_day + datetime.timedelta(days=days_num - 1)
        return str(last_day_of_current_month)


generate = Generate()

