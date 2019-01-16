from multiprocessing import Process, Queue
import time


def f(q):
   for a in range(5):
       print("Adding to Q!")
       time.sleep(1)
       q.put(a)

def g(q):
    i = 0
    v = True
    q.put("Adding to this q")
    while v == True:
        time.sleep(1)
        i = i + 1
        print("Get slept time " , i)
        try:
            print("From the q ",q.get(True,1))
        except Exception as e:
            print('exception raised {} {}'.format(e, type(e)))
            print("Empty")
        if i == 10:
            v = False
                
if __name__ == '__main__':
    q = Queue(10)
    print("First process")
    p = Process(target=f, args=(q,))
    p.start()

    print("Second Process")
    p1 = Process(target=g, args=(q,))
    p1.start()

    p.join()
    p1.join()
