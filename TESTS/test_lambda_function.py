# coding: utf-8

import unittest
import sys
sys.path.append('../')
import MyJST
import datetime
from lambda_function import *



class TestSample(unittest.TestCase):

    def get_sample_instance(self) :
        return {
            u'State': {u'Code': 48, u'Name': 'terminated'}, 
            u'InstanceId': 'i-12345',
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '8', u'Key': 'Scheduled-Start'}, 
                      {u'Value': '23', u'Key': 'Scheduled-Stop'}]
            }
    
    def setUp(self):
        self.instance = self.get_sample_instance()
        

    def adjust(self, year, month, day, h):
        jst.jst_now = datetime.datetime(year, month, day, hour=h)

    def test_1(self):
        instance = self.get_sample_instance()
        tags = get_tags(instance)
        self.assertEqual("Name" in tags, True)
        self.assertEqual("Scheduled-Start" in tags, True)
        self.assertEqual("Scheduled-Stop" in tags, True)
        self.assertEqual("Scheduled-Stop-Holiday" in tags, False)

    def test_2(self):
        self.adjust(2017, 1, 1, 1)
        self.assertEqual(is_holiday(), True)
        self.assertEqual(is_weekday(), False)

    def test_3(self):
        self.adjust(2017, 4, 2, 1)
        self.assertEqual(is_holiday(), False)
        self.assertEqual(is_weekday(), False)

    def test_4(self):
        self.adjust(2017, 4, 3, 1)
        self.assertEqual(is_holiday(), False)
        self.assertEqual(is_weekday(), True)

    def test_5(self):
        self.assertNotEqual(get_jst_now(), None)

    def test_6(self):
        instance = {
            u'State': {u'Code': 0, u'Name': 'pending'}, 
            u'InstanceId': 'i-23456',
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'Scheduled-Start'}] 
            }
        self.adjust(2017, 4, 3, 10)
        self.assertEqual(is_boot(instance), True)
        self.assertEqual(is_shutdown(instance), False)

        self.adjust(2017, 4, 3, 11)
        self.assertEqual(is_boot(instance), True)
        self.assertEqual(is_shutdown(instance), False)

    def test_7(self):
        instance = {
            u'State': {u'Code': 48, u'Name': 'terminated'}, 
            u'InstanceId': 'i-23456',
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'Scheduled-Start'}] 
            }
        self.adjust(2017, 4, 3, 10)
        self.assertEqual(is_boot(instance), True)
        self.assertEqual(is_shutdown(instance), False)

        self.adjust(2017, 4, 3, 11)
        self.assertEqual(is_boot(instance), True)
        self.assertEqual(is_shutdown(instance), False)

    def test_8(self):
        instance = {u'State': {u'Code': 48, u'Name': 'terminated'}}
        self.assertEqual(get_status(instance), "terminated")

        instance = {u'State': {u'Code': 0, u'Name': 'pending'}}
        self.assertEqual(get_status(instance), "pending")

        instance = {u'State': {u'Code': 16, u'Name': 'running'}}
        self.assertEqual(get_status(instance), "running")
        
    def test_9(self):
        instance = { u'InstanceId': 'i-23456'}
        self.assertEqual(get_instance_id(instance), 'i-23456')

        instance = { u'InstanceId': ''}
        self.assertEqual(get_instance_id(instance), '')

    def test_10(self):
        instance = {
            u'InstanceId': 'i-12345',
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}]}
        self.assertNotEqual(get_instance_name(instance), None)

        instance = {u'InstanceId': 'i-12345'}
        self.assertNotEqual(get_instance_name(instance), None)

    def test_11(self):
        instance = {
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'Scheduled-Start'}] 
            }
        self.assertEqual(get_boot_hour(instance), 10)
        self.assertEqual(get_shutdown_hour(instance), None)

    def test_12(self):
        instance = {
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'Scheduled-Stop'}] 
            }
        self.assertEqual(get_boot_hour(instance), None)
        self.assertEqual(get_shutdown_hour(instance), 10)

    def test_13(self):
        instance = {
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'Scheduled-Stop-Holiday'}] 
            }
        self.assertEqual(get_boot_hour(instance), None)
        self.assertEqual(get_shutdown_hour(instance), None)

    def test_14(self):
        instance = {
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'Scheduled-Start'},
                      {u'Value': '11', u'Key': 'Scheduled-Stop'}] 
            }
        self.assertEqual(get_boot_hour(instance), 10)
        self.assertEqual(get_shutdown_hour(instance), 11)

    def test_15(self):
        instance = {
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'scheduled-start'}, # lower case letters
                      {u'Value': '11', u'Key': 'scheduled-stop'}]  # lower case letters
            }
        self.assertEqual(get_boot_hour(instance), None)
        self.assertEqual(get_shutdown_hour(instance), None)

    def test_16(self):
        instance = {
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'Scheduled_Start'}, # under score
                      {u'Value': '11', u'Key': 'Scheduled_Stop'}]  # under score
            }
        self.assertEqual(get_boot_hour(instance), None)
        self.assertEqual(get_shutdown_hour(instance), None)

    def test_17(self):
        instance = {
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'Scheduled-Start'},
                      {u'Value': '11', u'Key': 'Scheduled-Stop'},
                      {u'Value': '', u'Key': 'Scheduled-Stop-Holiday'}]
            }
        self.assertEqual(get_boot_hour(instance), 10)
        self.assertEqual(get_shutdown_hour(instance), 11)

    def test_18(self):
        instance = {
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'Scheduled-Start'},
                      {u'Value': '11', u'Key': 'Scheduled-Stop'}]}
        self.assertEqual(get_shutdown_holiday(instance), None)

    def test_19(self):
        instance = {
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'Scheduled-Start'},
                      {u'Value': '11', u'Key': 'Scheduled-Stop'},
                      {u'Value': '12', u'Key': 'Scheduled-Stop-Holiday'}]
            }
        self.assertEqual(get_shutdown_holiday(instance), 12)

    def test_20(self):
        instance = {
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'Scheduled-Start'},
                      {u'Value': '', u'Key': 'Scheduled-Stop-Holiday'}]
            }
        self.assertEqual(get_shutdown_holiday(instance), True)

    def test_21(self):
        instance = {
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'Scheduled-Start'},
                      {u'Value': '止めて下さい', u'Key': 'Scheduled-Stop-Holiday'}]
            }
        self.assertEqual(get_shutdown_holiday(instance), True)



    #
    #
    #
    def test_101(self):
        """
        is_match_trigger_hour テスト
        """
        instance = {
            u'State': {u'Code': 16, u'Name': 'running'}, 
            u'InstanceId': 'i-12121',
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}]}
        
        self.adjust(2017, 1, 1, 0)
        self.assertEqual(is_match_trigger_hour(instance), None)
        self.adjust(2017, 4, 1, 10)
        self.assertEqual(is_match_trigger_hour(instance), None)
        self.adjust(2017, 4, 3, 20)
        self.assertEqual(is_match_trigger_hour(instance), None)


    def test_102(self):
        """
        is_match_trigger_hour テスト
        """
        instance = {
            u'State': {u'Code': 16, u'Name': 'running'}, 
            u'InstanceId': 'i-12121',
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'Scheduled-Start'},
                      {u'Value': '20', u'Key': 'Scheduled-Stop'}]
            }
        
        self.adjust(2017, 4, 3, 0)
        self.assertEqual(is_match_trigger_hour(instance), None)
        self.adjust(2017, 4, 3, 10)
        self.assertEqual(is_match_trigger_hour(instance), True)
        self.adjust(2017, 4, 3, 20)
        self.assertEqual(is_match_trigger_hour(instance), False)


    def test_103(self):
        """
        is_match_trigger_hour テスト
        """
        instance = {
            u'State': {u'Code': 16, u'Name': 'running'}, 
            u'InstanceId': 'i-12121',
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'Scheduled-Start'},
                      {u'Value': '10', u'Key': 'Scheduled-Stop'}]
            }
        
        self.adjust(2017, 4, 3, 0)
        self.assertEqual(is_match_trigger_hour(instance), None)
        self.adjust(2017, 4, 3, 10)
        self.assertEqual(is_match_trigger_hour(instance), True)
        self.adjust(2017, 4, 3, 20)
        self.assertEqual(is_match_trigger_hour(instance), None)


    def test_201(self):
        """
        is_match_trigger_stop_holiday テスト
        """
        instance = {
            u'State': {u'Code': 16, u'Name': 'running'}, 
            u'InstanceId': 'i-23232',
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'Scheduled-Start'},
                      {u'Value': '20', u'Key': 'Scheduled-Stop'},
                      {u'Value': '', u'Key': 'Scheduled-Stop-Holiday'}]
            }
        
        self.adjust(2017, 4, 3, 0) # monday
        self.assertEqual(is_match_trigger_stop_holiday(instance), None)
        self.adjust(2017, 4, 3, 10) # monday
        self.assertEqual(is_match_trigger_stop_holiday(instance), None)
        self.adjust(2017, 4, 3, 20) # monday
        self.assertEqual(is_match_trigger_stop_holiday(instance), None)

    def test_202(self):
        """
        is_match_trigger_stop_holiday テスト
        """
        instance = {
            u'State': {u'Code': 16, u'Name': 'running'}, 
            u'InstanceId': 'i-23232',
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'Scheduled-Start'},
                      {u'Value': '20', u'Key': 'Scheduled-Stop'},
                      {u'Value': '', u'Key': 'Scheduled-Stop-Holiday'}]
            }
        
        self.adjust(2017, 4, 2, 0) # sunday
        self.assertEqual(is_match_trigger_stop_holiday(instance), True)
        self.adjust(2017, 4, 2, 10) # sunday
        self.assertEqual(is_match_trigger_stop_holiday(instance), True)
        self.adjust(2017, 4, 2, 20) # sunday
        self.assertEqual(is_match_trigger_stop_holiday(instance), True)

    def test_203(self):
        """
        is_match_trigger_stop_holiday テスト
        """
        instance = {
            u'State': {u'Code': 16, u'Name': 'running'}, 
            u'InstanceId': 'i-23232',
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'Scheduled-Start'},
                      {u'Value': '20', u'Key': 'Scheduled-Stop'},
                      {u'Value': '', u'Key': 'Scheduled-Stop-Holiday'}]
            }
        
        self.adjust(2017, 5, 3, 0) # 建国記念日, 水曜
        self.assertEqual(is_match_trigger_stop_holiday(instance), True)
        self.adjust(2017, 5, 3, 10) # 建国記念日, 水曜
        self.assertEqual(is_match_trigger_stop_holiday(instance), True)
        self.adjust(2017, 5, 3, 20) # 建国記念日, 水曜
        self.assertEqual(is_match_trigger_stop_holiday(instance), True)

    def test_204(self):
        """
        is_match_trigger_stop_holiday テスト
        """

        instance = {
            u'State': {u'Code': 16, u'Name': 'running'}, 
            u'InstanceId': 'i-23232',
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'Scheduled-Start'},
                      {u'Value': '20', u'Key': 'Scheduled-Stop'},
                      {u'Value': '15', u'Key': 'Scheduled-Stop-Holiday'}]
            }
        
        self.adjust(2017, 5, 3, 0) # 建国記念日, 水曜
        self.assertEqual(is_match_trigger_stop_holiday(instance), None)
        self.adjust(2017, 5, 3, 10) # 建国記念日, 水曜
        self.assertEqual(is_match_trigger_stop_holiday(instance), None)
        self.adjust(2017, 5, 3, 15) # 建国記念日, 水曜
        self.assertEqual(is_match_trigger_stop_holiday(instance), True)
        self.adjust(2017, 5, 3, 20) # 建国記念日, 水曜
        self.assertEqual(is_match_trigger_stop_holiday(instance), None)


    def test_301(self):
        """
        manipulate_instance テスト
        """
        instance = {
            u'State': {u'Code': 0, u'Name': 'pending'}, 
            u'InstanceId': 'i-34567',
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'Scheduled-Start'},
                      {u'Value': '20', u'Key': 'Scheduled-Stop'},
                      {u'Value': '', u'Key': 'Scheduled-Stop-Holiday'}]
            }
        
        self.adjust(2017, 4, 3, 0) # weekday
        self.assertEqual(manipulate_instance(instance), None)
        self.adjust(2017, 4, 3, 10)
        self.assertEqual(manipulate_instance(instance), True)
        self.adjust(2017, 4, 3, 15)
        self.assertEqual(manipulate_instance(instance), None)
        self.adjust(2017, 4, 3, 20)
        self.assertEqual(manipulate_instance(instance), False)

    def test_302(self):
        """
        manipulate_instance テスト
        """
        instance = {
            u'State': {u'Code': 16, u'Name': 'running'}, 
            u'InstanceId': 'i-34567',
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'Scheduled-Start'},
                      {u'Value': '20', u'Key': 'Scheduled-Stop'}]
            }
        
        self.adjust(2017, 1, 1, 0) # 正月
        self.assertEqual(manipulate_instance(instance), None)
        self.adjust(2017, 1, 1, 10)
        self.assertEqual(manipulate_instance(instance), True)
        self.adjust(2017, 1, 1, 15)
        self.assertEqual(manipulate_instance(instance), None)
        self.adjust(2017, 1, 1, 20)
        self.assertEqual(manipulate_instance(instance), False)

    def test_303(self):
        """
        manipulate_instance テスト
        """
        instance = {
            u'State': {u'Code': 16, u'Name': 'running'}, 
            u'InstanceId': 'i-34567',
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'Scheduled-Start'},
                      {u'Value': '20', u'Key': 'Scheduled-Stop'}]
            }
        
        self.adjust(2017, 5, 3, 0) # 憲法記念日, 水曜
        self.assertEqual(manipulate_instance(instance), None)
        self.adjust(2017, 5, 3, 10)
        self.assertEqual(manipulate_instance(instance), True)
        self.adjust(2017, 5, 3, 15)
        self.assertEqual(manipulate_instance(instance), None)
        self.adjust(2017, 5, 3, 20)
        self.assertEqual(manipulate_instance(instance), False)


    def test_304(self):
        """
        manipulate_instance テスト
        """
        instance = {
            u'State': {u'Code': 0, u'Name': 'pending'}, 
            u'InstanceId': 'i-34567',
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'Scheduled-Start'},
                      {u'Value': '20', u'Key': 'Scheduled-Stop'},
                      {u'Value': '', u'Key': 'Scheduled-Stop-Holiday'}]
            }
        
        self.adjust(2017, 1, 1, 0)
        self.assertEqual(manipulate_instance(instance), False)
        self.adjust(2017, 1, 1, 10)
        self.assertEqual(manipulate_instance(instance), False)
        self.adjust(2017, 1, 1, 15)
        self.assertEqual(manipulate_instance(instance), False)
        self.adjust(2017, 1, 1, 20)
        self.assertEqual(manipulate_instance(instance), False)

    def test_305(self):
        """
        manipulate_instance テスト
        """
        instance = {
            u'State': {u'Code': 0, u'Name': 'pending'}, 
            u'InstanceId': 'i-34567',
            u'Tags': [{u'Value': 'hogehoge', u'Key': 'Name'}, 
                      {u'Value': '10', u'Key': 'Scheduled-Start'},
                      {u'Value': '20', u'Key': 'Scheduled-Stop'},
                      {u'Value': '15', u'Key': 'Scheduled-Stop-Holiday'}]
            }
        
        self.adjust(2017, 4, 3, 0) # monday
        self.assertEqual(manipulate_instance(instance), None)
        self.adjust(2017, 4, 3, 10)
        self.assertEqual(manipulate_instance(instance), True)
        self.adjust(2017, 4, 3, 15)
        self.assertEqual(manipulate_instance(instance), None)
        self.adjust(2017, 4, 3, 20)
        self.assertEqual(manipulate_instance(instance), False)

        


if __name__ == "__main__":
    unittest.main()
