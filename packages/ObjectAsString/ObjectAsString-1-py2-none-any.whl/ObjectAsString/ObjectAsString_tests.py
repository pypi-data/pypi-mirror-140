import unittest
from ObjectAsString import *


class MyTestCase(unittest.TestCase):
    def test_all(self):
        self.assertEquals(len(ObjectAsString("ssf")), 3)
        self.assertEquals(len(ObjectAsString("sf") + "sx"), 4)
        self.assertEquals(len(ObjectAsString("sf") + 5), 3)
        self.assertEquals(len(ObjectAsString(2) + "fs"), 3)
        self.assertEquals(len(ObjectAsString([4, 5, 3])), 3)
        self.assertEquals(len(ObjectAsString([4, 5, 3]) * 2), 6)
        self.assertEquals(len(ObjectAsString(2) * [4, 5, 3]), 6)
        self.assertEquals(len(ObjectAsString([4, 5, 3]) + [5, 2]), 5)
        self.assertEquals(ObjectAsString("sf") + "sx", "sfsx")
        self.assertEquals(ObjectAsString("sf") + 5, "sf5")
        self.assertEquals(ObjectAsString(56) + "llp", "56llp")
        self.assertEquals(ObjectAsString(5) + 6, mpf("11"))
        self.assertEquals(ObjectAsString(mpf("5.13")) + mpf("6.12"), mpf("11.25"))
        self.assertEquals(ObjectAsString([6, 3, 2] + [5, 1, 7]), [6, 3, 2, 5, 1, 7])
        self.assertEquals(ObjectAsString(mpf("12.32")) - mpf("3.14"), mpf("9.18"))
        self.assertEquals(ObjectAsString(mpf("12.32")) - mpf("3.44"), mpf("8.88"))
        self.assertEquals(ObjectAsString(mpf("12.32")) - mpf("4.57"), mpf("7.75"))
        self.assertEquals(ObjectAsString(78) - 66, mpf("12"))
        self.assertEquals(ObjectAsString(5) * 6, mpf("30"))
        self.assertEquals(ObjectAsString(mpf("5.12")) * mpf("2.5"), mpf("12.8"))
        self.assertEquals(ObjectAsString([5, 1, 3]) * 2, [5, 1, 3, 5, 1, 3])
        self.assertEquals(ObjectAsString([2, 3]) * 3, [2, 3, 2, 3, 2, 3])
        self.assertEquals(ObjectAsString(3) * [2, 3], [2, 3, 2, 3, 2, 3])
        self.assertEquals(ObjectAsString(56) / 7, mpf("8"))
        self.assertEquals(ObjectAsString(mpf("6.28")) / mpf("3.14"), mpf("2"))
        self.assertEquals(ObjectAsString(7) // 2, mpf("3"))
        self.assertEquals(ObjectAsString(7) % 2, mpf("1"))
        self.assertEquals(ObjectAsString(mpf("7.5")) % mpf("3"), mpf("1.5"))
        self.assertEquals(ObjectAsString(7) ** 2, mpf("49"))
        self.assertEquals(ObjectAsString(mpf("7.5")) ** mpf("2"), mpf("56.25"))
        self.assertTrue(ObjectAsString(mpf("5.7")) > mpf("4.3"))
        self.assertTrue(ObjectAsString(mpf("5.7")) >= mpf("4.3"))
        self.assertTrue(ObjectAsString(mpf("3.7")) < mpf("4.3"))
        self.assertTrue(ObjectAsString(mpf("3.7")) <= mpf("4.3"))
        self.assertTrue(ObjectAsString("ssd") == "ssd")
        self.assertTrue(ObjectAsString("ssd") != "ssdx")


if __name__ == '__main__':
    unittest.main()
