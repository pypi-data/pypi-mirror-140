import datetime
import calendar

balance=int(input('Enter your Balance'))
interest=int(input('Enter your Interest Rate'))
rate_of_interest=interest*0.01
monthly_payment=int(input('Enter your Monthly Payment'))
print(f'current_balance is {balance} and date is {datetime.date.today()}')
def calc_future():
    today=datetime.date.today()
    # print(start_date)
    calender_month_dur=calendar.monthrange(today.year,today.month)[1]
    # print(calender_month_dur)
    date_till_next=today+datetime.timedelta(days=((calender_month_dur-today.day)+1))
    end_date=date_till_next
    global balance
    while balance>0:
        interest_bal=balance*(rate_of_interest/12)
        balance+=interest_bal
        balance-=monthly_payment
        
        balance=round(balance,2)
        if balance<0:
            balance=0
        print(f'{end_date}----->{balance}')
        calc_next_date=calendar.monthrange(end_date.year,end_date.month)[1]
        end_date=end_date+datetime.timedelta(days=((calc_next_date-end_date.day)+1))

if __name__ == '__main__':
    calc_future()
