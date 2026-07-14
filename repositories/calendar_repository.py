import json, os
from app.models.calendar import Calendar

class CalendarRepository():
    LOCAL_SAVE_LOCATION: str = "saves/calendar.json"

    def save_calendar(self, calendar: Calendar):
        data = calendar.to_dict()
        
        with open(self.LOCAL_SAVE_LOCATION, "w") as f:
            json.dump(data, f, sort_keys=True, indent=4)

    def load_calendar(self):
        loc = self.LOCAL_SAVE_LOCATION

        if (not os.path.isfile(loc)):
            calendar = Calendar()
            self.save_calendar(calendar)
            return calendar

        with open(loc, 'r') as f:
            data = json.load(f)
            return Calendar.from_dict(data)
        