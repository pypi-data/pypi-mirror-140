import pytz
import datetime
import calendar
import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

fetch_actual_NYC = pytz.timezone('America/New_York')


def get_next_monthly_recurring_date(input_date , input_date_format, output_date_format):
    if input_date is None:
        input_date = get_today_date(input_date_format)

    input_date_obj = datetime.strptime(input_date, input_date_format)
    input_date_time_obj = datetime.strptime(input_date, input_date_format)

    input_date_str = input_date_obj.strftime(input_date_format)
    input_month = input_date_obj.month
    input_year = input_date_obj.year
    input_day = input_date_obj.day

    rng = calendar.monthrange(input_year, input_month)
    last_date_of_current_month = datetime(input_year, input_month, rng[1]).strftime(input_date_format)
    if input_date_str == last_date_of_current_month:
        if input_month != 2:
            next_monthly_recurring_date_obj = get_next_recurring_date(input_date_obj, 'M')
            if input_day > next_monthly_recurring_date_obj.day:
                month_range = calendar.monthrange(next_monthly_recurring_date_obj.year,
                                                  next_monthly_recurring_date_obj.month)
                last_date_of_next_month = datetime(next_monthly_recurring_date_obj.year,
                                                   next_monthly_recurring_date_obj.month,
                                                   month_range[1]).strftime(output_date_format)
                return last_date_of_next_month
            else:
                if input_date is not None and input_date_time_obj.day == 31:
                    month_range = calendar.monthrange(next_monthly_recurring_date_obj.year,
                                                      next_monthly_recurring_date_obj.month)
                    last_date_of_next_month = datetime(next_monthly_recurring_date_obj.year,
                                                       next_monthly_recurring_date_obj.month,
                                                       month_range[1]).strftime(output_date_format)
                    return last_date_of_next_month
                else:
                    current_day_of_next_month = datetime(next_monthly_recurring_date_obj.year,
                                                         next_monthly_recurring_date_obj.month,
                                                         input_day).strftime(output_date_format)
                    return current_day_of_next_month

        else:
            next_monthly_recurring_date_obj = get_next_recurring_date(input_date_obj, 'M')
            next_month_range = calendar.monthrange(next_monthly_recurring_date_obj.year,
                                              next_monthly_recurring_date_obj.month)
            current_month_range = calendar.monthrange(input_date_time_obj.year,
                                              input_date_time_obj.month)
            if input_date is not None and input_day == current_month_range[1]:
                next_month_recurring_date = datetime(next_monthly_recurring_date_obj.year,
                                                   next_monthly_recurring_date_obj.month,
                                                   next_month_range[1]).strftime(output_date_format)
                return next_month_recurring_date
            else:
                current_day_of_next_month = datetime(next_monthly_recurring_date_obj.year,
                                                     next_monthly_recurring_date_obj.month,
                                                     input_day).strftime(output_date_format)
                return current_day_of_next_month

    else:
        next_monthly_recurring_date_obj = get_next_recurring_date(input_date_obj, 'M')
        if next_monthly_recurring_date_obj.month == 2 and (input_day == 29 or input_day == 30 or input_day == 31):
            month_range = calendar.monthrange(next_monthly_recurring_date_obj.year,
                                              next_monthly_recurring_date_obj.month)
            last_date_of_next_month = datetime(next_monthly_recurring_date_obj.year, next_monthly_recurring_date_obj.month,
                                          month_range[1]).strftime(output_date_format)
            return last_date_of_next_month
        else:
            current_day_of_next_month = datetime(next_monthly_recurring_date_obj.year, next_monthly_recurring_date_obj.month,
                                          input_day).strftime(output_date_format)
            return current_day_of_next_month



def get_next_annual_recurring_date(enrollmentDate, input_date_format, output_date_format):
    if enrollmentDate is not None:
        current_date_obj = datetime.strptime(enrollmentDate, input_date_format)
    else:
        current_date_obj = datetime.today()

    enrollment_date_time_obj = datetime.strptime(enrollmentDate, input_date_format)
    logging.debug("enrollment_date_time_obj  {}".format(enrollment_date_time_obj))

    current_date_str = current_date_obj.strftime(input_date_format)
    current_month = current_date_obj.month
    current_year = current_date_obj.year

    rng = calendar.monthrange(current_year, current_month)
    logging.debug("rng {}".format(rng))
    last_date_of_month = datetime(current_year, current_month, rng[1]).strftime(input_date_format)

    if calendar.isleap(current_year) is False or current_month != 2 or current_date_str != last_date_of_month:
        next_recurring_date_obj = get_next_recurring_date(current_date_obj, 'A')
        next_recurring_date_str = next_recurring_date_obj.strftime(output_date_format)

        if enrollmentDate is not None and calendar.isleap(
                next_recurring_date_obj.year) is False and next_recurring_date_obj.month == 2 and next_recurring_date_obj.day == 28 and enrollment_date_time_obj.month == 2 and enrollment_date_time_obj.day == 29:
            next_recurring_date_obj = get_next_recurring_date(current_date_obj, 'A')
            month_range = calendar.monthrange(next_recurring_date_obj.year, next_recurring_date_obj.month)
            last_date_of_month = datetime(next_recurring_date_obj.year, next_recurring_date_obj.month,
                                          month_range[1]).strftime(output_date_format)
            logging.debug("last_date_of_month {}".format(last_date_of_month))
            return last_date_of_month
        else:
            logging.debug("next_recurring_date_str {}".format(next_recurring_date_str))
            return next_recurring_date_str

    else:
        next_recurring_date_obj = get_next_recurring_date(current_date_obj, 'A')
        next_recurring_date_str = next_recurring_date_obj.strftime(input_date_format)
        month_range = calendar.monthrange(next_recurring_date_obj.year, next_recurring_date_obj.month)
        last_date_of_month = datetime(next_recurring_date_obj.year, next_recurring_date_obj.month,
                                      month_range[1]).strftime(output_date_format)
        #next_recurring_date_str("last_date_of_month {} ".format(last_date_of_month))
        return last_date_of_month



def get_next_recurring_date(inputDateObj, subscriptionType):
    if subscriptionType == 'A' or subscriptionType == 'Annual':
        next_recurring_date_obj = (inputDateObj + relativedelta(years=1))
        return next_recurring_date_obj
    else:
        next_recurring_date_obj = (inputDateObj + relativedelta(months=1))
        return next_recurring_date_obj



def get_today_date(date_format):
    current_time = datetime.now(fetch_actual_NYC)
    return current_time.strftime(date_format)


def get_current_utc_timestamp():
    current_time = datetime.now(pytz.timezone('US/Eastern'))
    timestamp_string = current_time.strftime("%Y%m%d%H:%M:%S%z")
    timestamp_string = "{0}:{1}".format(
        timestamp_string[:-2],
        timestamp_string[-2:]
    )
    return timestamp_string