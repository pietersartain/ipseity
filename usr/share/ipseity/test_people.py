import unittest

# Here's our "unit tests".
class PeopleTests(unittest.TestCase):

  def setUp(self):
    self.people = People()

  def testBar(self):
    self.failUnless(True)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
