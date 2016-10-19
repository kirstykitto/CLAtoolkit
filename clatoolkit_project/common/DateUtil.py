__author__ = 'Koji Nishimoto'
__date__ = '19/10/2016'

class DateUtil(object):

	@classmethod
	def format_date(self, date_str, splitter, connector, isMonthSubtract):
		ret = ''
		if date_str is None or date_str == '':
			return ret

		# If isMonthSubtract, then subtract 1 from month (to avoid calculation in JavaScript)
		# isMonthSubtract = True is recommended
		month_subtract = 1 if isMonthSubtract else 0
		dateAry = date_str.split(',')
		return dateAry[0] + connector + str(int(dateAry[1]) - month_subtract).zfill(2) + connector + dateAry[2]