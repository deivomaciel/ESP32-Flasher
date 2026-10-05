from datetime import datetime
now = datetime.today()

def get_datetime():
    return now.strftime("%d/%m/%YT%H:%M:%S")

print(get_datetime())