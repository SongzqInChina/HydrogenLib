import time
class Vtime:
    def __init__(self, sec):
        self._sec = sec
        self._hor = 0
        self._min = 0
        self._day = 0

        self.Processing()

    def Processing(self):
        flag = 0
        while not flag:
            flag = 1
            if self._sec >= 60:
                self._min += self._sec // 60
                self._sec -= self._sec // 60 * 60
                flag = 0
            if self._min >= 60:
                self._hor += self._min // 60
                self._min -= self._min // 60 * 60
                flag = 0
            if self._hor >= 24:
                self._day += self._hor // 24
                self._hor -= self._hor // 24 * 24
                flag = 0

        self._min = int(self.min)
        self._hor = int(self.hor)
        self._day = int(self.day)

    def toInt(self):
        self._day = int(self.day)
        self._hor = int(self.hor)
        self._sec = int(self.sec)
        self._min = int(self.min)

    @property
    def sec(self):
        return self._sec

    @property
    def min(self):
        return self._min

    @property
    def hor(self):
        return self._hor

    @property
    def day(self):
        return self._day

    @sec.setter
    def sec(self, v: int | float):
        self._sec = v

    @min.setter
    def min(self, v: int | float):
        self._min = v

    @hor.setter
    def hor(self, v: int | float):
        self._hor = v

    @day.setter
    def day(self, v: int | float):
        self._day = v

    @property
    def time(self):
        return self.day, self.hor, self.min, self.sec

    @time.setter
    def time(self, v: tuple[int | float, ...] | list[int | float, ...]):
        lenght = len(v)
        if lenght >= 1:
            self.day = v[0]
        if lenght >= 2:
            self.hor = v[1]
        if lenght >= 3:
            self.min = v[2]
        if lenght >= 4:
            self.sec = v[3]

    def __str__(self):
        return f"{self.__class__.__name__}(day={self.day}, hor={self.hor}, min={self.min}, sec={self.sec})"

    __repr__ = __str__
