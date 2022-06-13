import time
import pulsectl

pulse = pulsectl.Pulse('event-printer')
  # print('Event types:', pulsectl.PulseEventTypeEnum)
  # print('Event facilities:', pulsectl.PulseEventFacilityEnum)
  # print('Event masks:', pulsectl.PulseEventMaskEnum)

def event_handler(ev):
    #print('Pulse event:', ev)
    event_handler.event = ev
    raise pulsectl.PulseLoopStop
    #    print(pulse.sink_input_info())
    # pulse.event_listen()
    ### Raise PulseLoopStop for event_listen() to return before timeout (if any)





pulse.event_mask_set('all')
pulse.event_callback_set(event_handler)
while True:
    pulse.event_listen()
    if event_handler.event.t == pulsectl.PulseEventTypeEnum.new:
        client = None
        for s in pulse.sink_input_list():
            if s.index == event_handler.event.index:
                props = s.proplist
                if props['application.name'] == 'Shairport Sync':
                    client = 'AIRPLAY'
                elif props['media.role'] == 'music':
                    client = 'BLUETOOTH'
                else:
                    print(props)

        if client is not None:
            print('NEW', client)
        else:
            print("UNKNOWN", pulse.sink_input_list(), event_handler.event)
            for s in pulse.sink_input_list():
                print("UNKNOWN INPUT", s.proplist)
    elif event_handler.event.t == pulsectl.PulseEventTypeEnum.remove:
        print("REMOVE")
