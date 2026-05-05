class Sequeue(object):
    def _init_(self):
        self.Queuesize=20
        self.s=[None for x in range(0,self.Queuesize)]
        self.front=0
        self.rear=0

x=[1,2,3,4,5]
res=map(lambda i:i*2,x)
print(list(res))