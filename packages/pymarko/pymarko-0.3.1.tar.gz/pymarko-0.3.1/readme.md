# PyMarko

**in development**

## Example

``` python
#!/usr/bin/env python3

import time
from pymarko import get_ip
import sys
from pymarko.pubsub import Subscriber, Publisher


def subfunc():

    def myfunc(data):
        if data:
            msg = data.decode('utf8')
            print(f">> Subscriber got: {msg}")

    sub = Subscriber()
    # sub.bind("bob", 9500)
    sub.connect("bob", get_ip(), 9500)
    sub.subscribe(myfunc)
    sub.loop()

def pubfunc():
    pub = Publisher()
    pub.bind("bob", 9500)
    pub.listen()

    i = 0
    while True:
        msg = f"hello {i}".encode("utf8")
        pub.publish(msg)
        time.sleep(1)
        i += 1


if __name__ == "__main__":

    if len(sys.argv) > 1:
        func = sys.argv[1]
    else:
        func = "p"

    try:
        if func == "s":
            subfunc()
        elif func == "p":
            pubfunc()

    except KeyboardInterrupt:
        print("shutting down")
    finally:
        print("end ------------------")
```

# MIT License

**Copyright (c) 2018 Kevin J. Walchko**

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
