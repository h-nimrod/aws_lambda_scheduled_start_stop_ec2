# coding: utf-8

import time
from pytz import timezone
import datetime
import japanese_holiday

GOOGLE_CALENDER_API_KEY = '' # GoogleカレンダーのAPIキーを設定してください

class MyJST:
    jst_now = None
    holidays = None

    def __init__(self):
        self.get_jst_now(True)
        self.is_holiday(True)
    
    def get_jst_now(self, force=False):
        if force == False and self.jst_now != None:
            return self.jst_now
            
        utc_now = datetime.datetime.now(timezone('UTC'))
        self.jst_now = utc_now.astimezone(timezone('Asia/Tokyo'))
        return self.jst_now
            

    def is_weekday(self):
        if self.is_holiday():
            return False

        WEEKDAY_SAT = 5
        WEEKDAY_SUN = 6

        today = self.get_jst_now()
        wday = today.weekday()
        return wday != WEEKDAY_SAT and wday != WEEKDAY_SUN


    def is_holiday(self, force=False):
        today = self.get_jst_now()
        if force or self.holidays == None:
            date_from = datetime.date(today.year, 1, 1)
            date_to = datetime.date(today.year, 12, 31)

            try:
                self.holidays = japanese_holiday.getholidays(
                    GOOGLE_CALENDER_API_KEY,
                    japanese_holiday.HOLIDAY_TYPE_OFFICIAL_JA,
                    date_from.strftime('%Y-%m-%d'),
                    date_to.strftime('%Y-%m-%d')
                    )
            except Exception, e:
                print "google calender api exception occurs: "  + str(e)
    
        if self.holidays == None:
            return False

        today_str = today.strftime('%Y-%m-%d')
        match = False

        for holiday in self.holidays:
            if today_str == holiday['start']['date'] :
                match = True
                break
            
        return match
