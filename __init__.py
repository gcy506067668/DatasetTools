# import threading
# import time
#
# def multiplePrint(text1, text2):
#     for i in range(10):
#         dq = ""
#         for num in range(i):
#             dq += ">"
#
#         print("\033[35m\r"+dq+"\033[0m", end="", flush=True)
#         time.sleep(1)
#     pass
#
# threading.Thread(target=multiplePrint,args=("\033[35m111115\033[0m","123")).start()