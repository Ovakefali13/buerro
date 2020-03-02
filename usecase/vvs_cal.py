import datetime as dt
from datetime import datetime, timedelta
import pytz
import sys

from adapter import VVSAdapter, CalAdapter

# get trips from vvs and put them in calendar

if __name__ == "__main__":
    name_origin = sys.argv[1]
    name_dest = sys.argv[2]
    arr_dep = sys.argv[3]

    # expects event_time in format %H%M, e.g. 0900
    if(len(sys.argv) > 4):
        event_time = datetime.strptime(sys.argv[4], "%H%M").time()
    else:
        event_time = datetime.now().time()

    print(pytz.country_names['de'])
    
    event_dt = datetime.combine(dt.date.today(), event_time)
    local_tz = pytz.timezone('Europe/Berlin')
    event_dt = local_tz.localize(event_dt)

    print(event_time)
    print(event_dt)

    event_buffer = timedelta(minutes=10)
    vvs_adapter = VVSAdapter(event_buffer=event_buffer)
    journeys = vvs_adapter.get_journeys(name_origin, name_dest, arr_dep, event_dt)

    recommended_journey = None
    if arr_dep is 'arr':
    
        def time_from_event(journey):
            return (event_dt - event_buffer) - journey.get_arr_time()

        """ three requirements for choosing a tram:
                1. I am on time
                2. I am not there too early (just on time)
                3. It doesn't take too long (advantage over others > 5 minutes)
            solution:
                1. filter such that none are too late
                2. sort in reverse order (latest to earliest)
                3. only consider ealier ones if they take significantly less time
        """
        none_too_late = list(filter(lambda journey: time_from_event(journey) >= timedelta(0), journeys))
        sorted_by_arrival = sorted(none_too_late, reverse=True, 
                key=lambda journey : journey.get_arr_time())
        journeys = sorted_by_arrival

        recommended_journey = sorted_by_arrival[0]
        that_much_faster = 5
        for journey in sorted_by_arrival:
            if(recommended_journey.get_duration() >= that_much_faster + journey.get_duration()):
                print('rechoose')
                recommended_journey = journey
    else:
        # TODO recommmend journey for dep
        recommended_journey = journeys[0]
    
    [print(str(i) + ':\n' + str(j) + '\n') for i, j in enumerate(journeys)]

    if recommended_journey:
        print('Recommended: \n' + str(recommended_journey))

    chosen_journey = journeys[int(input("Which do you want to take? "))]

    print('Chosen: \n' + str(chosen_journey)) 

    cal_adapter = CalAdapter()
    
   # TODO add event 
