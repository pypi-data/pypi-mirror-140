import unittest
from HTMLTestRunner import HTMLTestRunner
test_dir = ""
discover = unittest.defaultTestLoader.discover(test_dir, pattern="*_test.py")

if __name__ == "__main__":
    print("...")

    print(": %s" % discover.countTestCases())

    filename = "result.html"

    fp = open(filename, "wb")
    runner = HTMLTestRunner(
        stream=fp,
        title="Guest Manage System Interface Test Report",
        description="Implementation Example with: ",
    )
    runner.run(discover)

    fp.close()
