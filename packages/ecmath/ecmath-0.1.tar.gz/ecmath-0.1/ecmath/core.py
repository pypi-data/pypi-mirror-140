class Point:
    x: int
    y: int

class Curve:
    A: int
    B: int
    P: int

    def __ExtendedEuclid(self, a: int, b: int, x: list, y: list):
        old_r, r = a, b
        old_s, s = 1, 0
        old_t, t = 0, 1
        
        while (r != 0):
            quotient = old_r // r
            old_r, r = r, old_r - quotient * r
            old_s, s = s, old_s - quotient * s
            old_t, t = t, old_t - quotient * t
        
        x.append(old_s)
        y.append(old_t)
        
        return old_r

    def __ModInverse(self, a: int):
        x = []
        y = []
        g = self.__ExtendedEuclid(a, self.P, x, y)
        if (g != 1):
            return None
        else:
            return (x[0] % self.P + self.P) % self.P

    def Add(self, p: Point, q: Point) -> Point:
        s = 0
        if ((p.x == q.x) and (p.y == q.y)):
            modinverse = self.__ModInverse(2*p.y % self.P)
            if (modinverse == None):
                s = None
            else:
                s = (3*p.x**2 + self.A) * modinverse % self.P
        else:
            modinverse = self.__ModInverse((p.x - q.x) % self.P)
            if (modinverse == None):
                s = None
            else:
                s = (p.y - q.y) * modinverse % self.P

        r = Point()

        if (s == None):
            r.x = 0
        elif ((q.x == 0) and (q.y == 0)):
            r.x = p.x
        else:
            r.x = (s**2 - p.x - q.x) % self.P

        if (s == None):
            r.y = 0
        elif ((q.x == 0) and (q.y == 0)):
            r.y = p.y
        else:
            r.y = (-(p.y + s * (r.x - p.x))) % self.P

        return r

    def Multiply(self, p: Point, n: int) -> Point:
        if (n < 0):
            raise ValueError("n must be positive")

        q = Point()
        q.x = 0
        q.y = 0

        while (n > 0):
            if (n % 2 == 1):
                q = self.Add(p, q)
            p = self.Add(p, p)
            n = n // 2

        return q