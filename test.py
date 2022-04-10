import unittest
import utils
import os
import datetime
import random
import copy

class UtilsTest(unittest.TestCase):
    def test_readData_writeCSV(self):
        """
        Test readData and writeCSV. Creates and deletes a file and depends
        on the existence of "sample_temperature_data_for_coding_challenge.csv", which
        is not ideal, but should suffice for now. Also reading and writing should
        ideally be tested separately.
        """
        data = utils.readData()
        utils.writeCSV(".test.csv", data)
        with open("sample_temperature_data_for_coding_challenge.csv", "r") as f:
            original = f.readlines()
        with open(".test.csv", "r") as f:
            readwrite = f.readlines()
        
        os.remove(".test.csv")  
        self.assertEqual(original, readwrite)
        
    
    def test_convertDatetime(self):
        """
        Test convertDatetime. Tests only the format used in this challenge
        """
        strings = ["2019-04-13T17:51:16.000+0000", "2019-07-04T07:40:00.000+0000", "2019-04-30T08:37:41.000+0000"]
        result = utils.convertDatetime(strings)
        correct = [datetime.datetime(year = 2019, month = 4, day = 13, hour=17, minute=51, second=16, microsecond=0, tzinfo=datetime.timezone.utc),
                   datetime.datetime(year = 2019, month = 7, day = 4, hour=7, minute=40, second=0, microsecond=0, tzinfo=datetime.timezone.utc),
                   datetime.datetime(year = 2019, month = 4, day = 30, hour=8, minute=37, second=41, microsecond=0, tzinfo=datetime.timezone.utc)]
                   
        self.assertEqual(result, correct)
        
        # First: wrong microsecond
        # Second: wrong minute
        # Third: no timezone-information
        incorrect = [datetime.datetime(year = 2019, month = 4, day = 13, hour=17, minute=51, second=16, microsecond=1, tzinfo=datetime.timezone.utc),
                     datetime.datetime(year = 2019, month = 7, day = 4, hour=7, minute=41, second=0, microsecond=0, tzinfo=datetime.timezone.utc),
                     datetime.datetime(year = 2019, month = 4, day = 30, hour=8, minute=37, second=41, microsecond=0)]
        
        for s, i in zip(strings, incorrect):
            self.assertNotEqual(utils.convertDatetime([s]), i)
        
        
        # Tests could be extended to all properties saved in datetime, like year, month, day, ...
        # Also could check things like leap years, but in principle, this is all part of the datetime package, which is already
        # thoroughly tested.
        with self.assertRaises(Exception):
            # Inserted datetime, not string
            d = utils.convertDatetime([correct[0]])
        with self.assertRaises(Exception):
            # Invalid day
            d = utils.convertDatetime(["2019-02-30T17:51:16.000+0000"])
        with self.assertRaises(Exception):
            # Invalid month switched
            d = utils.convertDatetime(["2019-13-04T17:51:16.000+0000"])
        with self.assertRaises(Exception):
            # Missing timezone information
            d = utils.convertDatetime(["2019-04-13T17:51:16.000"])
        with self.assertRaises(Exception):
            # Missing microseconds
            d = utils.convertDatetime(["2019-04-13T17:51:16+0000"])


    def test_datetimeToString(self):
        """
        Test convertDatetime. Tests only the format used in this challenge
        """
        correct = ["2019-04-13T17:51:16.000+0000", "2019-07-04T07:40:00.000+0000", "2019-04-30T08:37:41.000+0000"]
        tests = [datetime.datetime(year = 2019, month = 4, day = 13, hour=17, minute=51, second=16, microsecond=0, tzinfo=datetime.timezone.utc),
                 datetime.datetime(year = 2019, month = 7, day = 4, hour=7, minute=40, second=0, microsecond=0, tzinfo=datetime.timezone.utc),
                 datetime.datetime(year = 2019, month = 4, day = 30, hour=8, minute=37, second=41, microsecond=0, tzinfo=datetime.timezone.utc)]
        
        result = utils.datetimeToString(tests)
        
        self.assertEqual(result, correct)
        
        # First: wrong microsecond
        # Second: wrong minute
        # Third: no timezone-information
        incorrect = ["2019-04-13T17:51:16.001+0000", "2019-07-04T07:41:00.000+0000", "2019-04-30T08:37:41.000"]
        
        for t, i in zip(tests, incorrect):
            self.assertNotEqual(utils.datetimeToString([t]), i)
        
        
        # Tests could be extended to all properties saved in datetime, like year, month, day, ...
        # Also could check things like leap years, but in principle, this is all part of the datetime package, which is already
        # thoroughly tested.
        with self.assertRaises(Exception):
            # Inserted string, not datetime
            d = utils.datetimeToString([correct[0]])
        with self.assertRaises(Exception):
            # Invalid day
            inv = datetime.datetime(year = 2019, month = 2, day = 30, hour=17, minute=51, second=16, microsecond=0, tzinfo=datetime.timezone.utc)
            d = utils.datetimeToString([inv])
        with self.assertRaises(Exception):
            # Invalid month
            inv = datetime.datetime(year = 2019, month = 13, day = 13, hour=17, minute=51, second=16, microsecond=0, tzinfo=datetime.timezone.utc)
            d = utils.datetimeToString([inv])


    def test_cast(self):
        """
        Test cast. Tests only a small subset of conceivable cases
        """
        vals = [i + 0.1 for i in range(10)]
        vals_str = [str(v) for v in vals]
        vals_int = [int(v) for v in vals]

        self.assertEqual(utils.cast(vals, int), vals_int)
        self.assertEqual(utils.cast(vals, str), vals_str)
        self.assertEqual(utils.cast(vals_str, float), vals)
        
        self.assertNotEqual(utils.cast(vals, int), vals)

        with self.assertRaises(Exception):
            utils.cast(vals_str, int)

    def test_splitProperties(self):
        """
        Test splitProperties. Tests only a small subset of conceivable cases
        """
        data = {"0": [i for i in range(10)],
                "1": [-i for i in range(10)],
                "2": [("A" if i < 5 else "B") for i in range(10)],
               }
    
        correct = {"A": {"0": [i for i in range(5)],
                         "1": [-i for i in range(5)],
                         "2": ["A" for i in range(5)],
                        },
                   "B": {"0": [i for i in range(5, 10)],
                         "1": [-i for i in range(5, 10)],
                         "2": ["B" for i in range(5, 10)],
                        }
                  }
        
        result = utils.splitProperties(data, prop = "2")
        
        self.assertEqual(result, correct)


        data = {"0": [i for i in range(10)],
                "1": [-i for i in range(10)],
                "2": [("A" if i < 5 else "B") for i in range(10)],
                "3": [("A" if i < 5 else "B") for i in range(10)]
               }
    
        with self.assertRaises(Exception):
            # Raise exception because there are duplicates in column "2"
            result = utils.splitProperties(data, prop = "2", check_duplicates = ["2"])
        with self.assertRaises(Exception):
        # Raise exception because there are duplicates in column "3"
            result = utils.splitProperties(data, prop = "2", check_duplicates = ["3"])
    
    
    def test_flattenDict(self):
        """
        Test flattenDict. Tests one case out of multiple conceivable cases
        """
        data_split = {"A": {"0": [i for i in range(5)],
                            "1": [-i for i in range(5)],
                            "2": ["A" for i in range(5)],
                           },
                      "B": {"0": [i for i in range(5, 10)],
                            "1": [-i for i in range(5, 10)],
                            "2": ["B" for i in range(5, 10)],
                           }
                     }

        correct = {"0": [i for i in range(10)],
                   "1": [-i for i in range(10)],
                   "2": [("A" if i < 5 else "B") for i in range(10)],
                  }
        
        self.assertEqual(utils.flattenDict(data_split, property_name = "2", sort_by = "0"), correct)
    
    
    def test_identifyTimeIntervals(self):
        """
        Test identifyTimeIntervals. Tests only if interval is complete range if max_interval is
        None or sufficiently large.
        """
        
        tests = sorted([datetime.datetime(year = random.randint(1900, 2022), month = random.randint(1, 12),
                                   day = random.randint(1, 28), hour=random.randint(0, 23),
                                   minute=random.randint(0, 59), second=random.randint(0, 59)) for i in range(100)])
        
        correct = [[tests[0], tests[-1]]]
        
        self.assertEqual(utils.identifyTimeIntervals(tests, max_interval=None), correct)
        self.assertEqual(utils.identifyTimeIntervals(tests, max_interval=1E10), correct)

    def test_padData(self):
        """
        Test padData. Tests only a subset of conceivable cases. Does not check what happens, if
        pad_to_len_of == pad_len_of or if length at pad_to_len_of is smaller than length at pad_len_of. 
        """
        
        correct1 = {"0": [i for i in range(8)],
                    "1": [-i for i in range(10)],
                    "2": ["A" for i in range(10)],
                   }
                   
        correct2 = {"0": [i for i in range(8)],
                    "1": [-i for i in range(10)],
                    "2": ["A" for i in range(8)],
                   }
        
        data = {"0": [i for i in range(8)],
                "1": [-i for i in range(10)],
                "2": ["A" for i in range(3)]
               }
        
        
        test1 = copy.deepcopy(data)
        test2 = copy.deepcopy(data)
        test3 = copy.deepcopy(data)
        
        utils.padData(test1, pad_to_len_of = "1", pad_len_of = "2")
        utils.padData(test2, pad_to_len_of = "0", pad_len_of = "2")
        
        self.assertEqual(test1, correct1)
        self.assertEqual(test2, correct2)


        with self.assertRaises(Exception):
            # Column "0" has more than one unique value
            utils.padData(test3, pad_to_len_of = "1", pad_len_of = "0")
        

if __name__ == "__main__":
    random.seed(42)
    unittest.main()

