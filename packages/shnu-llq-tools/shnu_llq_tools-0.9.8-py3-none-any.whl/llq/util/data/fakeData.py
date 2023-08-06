import numpy as np
import pandas as pd
from pandas import DataFrame

xingl = list('赵钱孙李周吴郑王冯陈褚蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏窦章苏潘葛奚范彭郎鲁韦昌马苗方俞任袁柳')
mingl = list("群平风华正茂仁义礼智强天霸红和丽平世莉界中华正义伟岸茂盛繁圆一懿贵妃彭丽媛习嬴政不韦近平荣群智慧睿兴风清扬自成世民嬴旺品网红文天学与翔斌霸学花文教学忠谋书")


def create_name(size, name='姓名', xm=None):
    x = np.random.choice(xm[0], (size, 1))
    m = np.random.choice(xm[1], (size, 2))
    nm = np.hstack((x, m))
    df: DataFrame = pd.DataFrame(nm)
    dff = pd.DataFrame()
    # df[2]=df[2].apply(lambda x: ('',x)[np.random.randint(0,2)])
    dff[name] = df[0] + df[1] + df[2]
    return dff[name]


def create_attrs(size, colums, bound):
    return pd.DataFrame(np.random.randint(*bound, size=(size, len(colums))),
                        columns=colums)


def create_attr(size, att_name, scope):
    nmm = np.random.choice(scope, (size, 1))
    return pd.DataFrame(nmm, columns=[att_name])


def gen(size=40):
    return pd.concat([
        create_name(size, '姓名', [xingl, mingl]),
        create_attr(size, '性别', ['男', '女']),
        create_attr(size, '学校', ['清华大学', '北京大学', '复旦大学', '上海师大', '上海交大']),
        create_attr(size, '班级', ['计算机科学与技术', '人工智能', '数据科学']),
        create_attrs(size, ['英语', '政治'], [20, 100]),
        create_attrs(size, ['线代', '概率'], [20, 100]),
        create_attrs(size, ['高数', '专业课', '面试'], [30, 150])],
        axis=1)


if __name__ == '__main__':
    print(gen(150))

from itertools import product

l1 = [1, 2, 3]
l2 = [4, 5, 6]
combinatios = product(l1, l2)
print(*combinatios)

from itertools import tee
from typing import Iterable


def slide_window(iterable: Iterable, window_size):
    hi = tee(iter(iterable), window_size)
    repeat = lambda x, y: [next(x) for _ in range(y)]
    [repeat(hi[i], i) for i in range(1, window_size)]
    return zip(*hi)




print(*slide_window(range(20), 5))



w=range(12)
b=[iter(w)]*2
print(next(b[0]),next(b[1]))
print('**3'*3)
print(*b[1])
print(*zip(*b))

x=range(12)
print(*zip(*[iter(x)]*4))

