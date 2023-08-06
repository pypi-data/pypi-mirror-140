# stopwatch
an insanely simple stopwatch library

### Usage:
```python
from main import StopWatch,utils
import time

s = StopWatch()
s.start()
time.sleep(5)

print(str(s.duration))
print("bef pause ^")
s.pause()
time.sleep(5)
print(str(s.duration))
print("while pause ^")
s.unpause()
time.sleep(5)
print(str(s.duration))
print("after pause ^")
s.stop()
s.reset()
time.sleep(2)
print(str(s.duration))
print("after reset ^")
print("now starting..")
s.start()
print("running: " + str(s.running))
time.sleep(1)
print(str(s.duration))
print("bef restart ^")
s.restart()
time.sleep(3)
print(str(s.duration))
print("after restart ^")








