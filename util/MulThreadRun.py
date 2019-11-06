import threading
from functools import wraps
from concurrent.futures import ThreadPoolExecutor

# threading.Thread(target=multiplePrint, args=("11111", "222222")).start()


class MultiThread(object):

    def __init__(self, threadnum):
        self.t_num = threadnum
        pass

    def __call__(self, func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            for item in args:
                if isinstance(item, (list, tuple)):
                    cut_result = []
                    length = int(len(item) / self.t_num)
                    for index in range(self.t_num):
                        if index != self.t_num - 1:
                            cut_result.append(item[index * length:(index + 1) * length])
                        else:
                            cut_result.append(item[index * length:len(item)])
                    for t_item in cut_result:
                        args = (t_item)
                        # threading.Thread(target=func, args=(args, kwargs)).start()

        return wrapped_function

@MultiThread(1)
def test(paras):
    print(paras)

if __name__ == '__main__':
    testp = ['1', '2', '3', '4', '5', '6', '7', '8']
    test(testp)