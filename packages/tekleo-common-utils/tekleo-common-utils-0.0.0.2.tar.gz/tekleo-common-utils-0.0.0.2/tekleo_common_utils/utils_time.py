from datetime import datetime
import calendar
from injectable import injectable


@injectable
class UtilsTime:
    def get_current_timestamp_ms(self) -> int:
        return int(round(datetime.now().timestamp() * 1000))

    def get_number_of_days_in_month(self, year: int, month: int) -> int:
        x, number_of_days_in_month = calendar.monthrange(year, month)
        return number_of_days_in_month
