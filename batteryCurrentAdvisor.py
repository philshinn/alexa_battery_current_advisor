from __future__ import print_function
import urllib, json, string, datetime

#---------------- Code to read in the tide data for today ----------------------
def get_raw_data(url):
    dbg = False
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    return data["predictions"]
    
def lopSeconds(time):
    dbg = True
    if string.find(str(time),'day')> 1:
        foo = str(time)
        junk,foo = foo.split(',')
        time = foo.strip()
    timeSize = str(time).count(':')
    if timeSize == 1:
        return time
    elif timeSize == 2:
        hr,mins,secs = str(time).split(':')
        return hr+':'+mins
    
def addTimes(time1,time2):
    dbg = True
    time1 = lopSeconds(time1)
    time2 = lopSeconds(time2)
    t1_hours,t1_mins = string.split(time1,':')
    t2_hours,t2_mins = string.split(time2,':')
    newTime = datetime.timedelta(hours=int(t1_hours), minutes=int(t1_mins)) + datetime.timedelta(hours=int(t2_hours), minutes=int(t2_mins))
    newTime = lopSeconds(newTime)
    hrs,mins = string.split(str(newTime),':')
    if string.find(str(newTime),'day')> 1:
        newTime = datetime.timedelta(hours=int(hrs),minutes=int(mins)) - datetime.timedelta(hours=24)
    return newTime

class TideDatum:
    """
    Contains the type of tide (high or low), the day, the time and the height
    """
    def __init__(self,rawDatum):
        self.type = rawDatum['type']
        self.day,self.time = string.split(rawDatum['t'],' ')
        self.height = rawDatum['v']
        if self.type == 'H':
            self.nextSlack = str(addTimes(self.time,'2:20:00'))             # the north river (Hudson) High Water Slack starts 2:20 after high water at the battery
            self.nextSlackEnd = str(addTimes(self.nextSlack,'00:35:00'))    # the HWS ends after 35 minutes
        elif self.type == 'L':
            self.nextSlack = str(addTimes(self.time,'2:40:00'))             # the north river (Hudson) Low Water Slack starts 2:40 after low water at the battery
            self.nextSlackEnd = str(addTimes(self.nextSlack,'00:35:00'))    # and ends 35 minutes after that.
        
def parse_raw_data(rawDatum):
    return TideDatum(rawDatum)

def read_data():  # this reads the data for today
    dbg = False
    url = "https://tidesandcurrents.noaa.gov/api/datagetter?product=predictions&application=NOS.COOPS.TAC.WL&date=today&datum=MLLW&station=8518750&time_zone=lst_ldt&units=english&interval=hilo&format=json"
    myData = get_raw_data(url)
    tideDataList = []
    for rawDatum in myData:
        parsedDatum = parse_raw_data(rawDatum)
        tideDataList.append(parsedDatum)
    return tideDataList
    
def getTomorrow():
    d = datetime.date.today() + datetime.timedelta(days=1)
    return d.strftime("%Y%m%d")
    
def read_tomorrow_data(): # this reads the data for tomorrow
    dbg = False
    tom = str(getTomorrow())
    url = "https://tidesandcurrents.noaa.gov/api/datagetter?product=predictions&application=NOS.COOPS.TAC.WL&begin_date="+tom+"&end_date="+tom+"&datum=MLLW&station=8518750&time_zone=lst_ldt&units=english&interval=hilo&format=json"
    myData = get_raw_data(url)
    tideDataList = []
    for rawDatum in myData:
        parsedDatum = parse_raw_data(rawDatum)
        tideDataList.append(parsedDatum)
    return tideDataList


def read_dates_data(aDate):  # this reads the data for any date in the format yyyymmdd for start date and end date being the same date
    dbg = False
    aDate = aDate.replace('-','')
    url = "https://tidesandcurrents.noaa.gov/api/datagetter?product=predictions&application=NOS.COOPS.TAC.WL&begin_date="+aDate+"&end_date="+aDate+"&datum=MLLW&station=8518750&time_zone=lst_ldt&units=english&interval=hilo&format=json"
    myData = get_raw_data(url)
    tideDataList = []
    for rawDatum in myData:
        parsedDatum = parse_raw_data(rawDatum)
        tideDataList.append(parsedDatum)
    return tideDataList
    

# ------------------------ How to articulate all when high tide is first tide

highTideArray = [
    "The first predicted high tide at the battery is at %s in the morning. ",
    "The Hudson will continue to flood (water moving north) until slack water starts at %s. ",
    "Slack water ends 35 minutes later at %s when the ebb tide starts and the water begins to move south. ",
    "The ebb continues through the next low tide, which is at %s. ",
    "Ebb ends when the low water slack begins at %s. ",
    "The flood starts when slack water ends at %s and the Hudson flows north. ",
    "The second high tide of the day is at %s. ",
    "The next slack after that starts at %s. ",
    "That slack ends and the river heads south again starting at %s. ",
    "The second low tide is at %s. ",
    "The ebb continues until slack at %s. ",
    "And the flood starts at %s. "    
    ]
    
# -------------------------- How to articulate all when low tide is the first tide

lowTideArray = [
    "The first predicted low tide at the battery is at %s in the morning. ",
    "The Hudson will continue to ebb (water moving south) until slack water starts at %s. ",
    "Slack water ends 35 minutes later at %s when the flood tide starts and the water begins to move north. ",
    "The flood continues through the next high tide, which is at %s. ",
    "Flood ends when the high water slack begins at %s. ",
    "The ebb starts when slack water ends at %s and the Hudson flows south. ",
    "The second low tide of the day is at %s. ",
    "The next slack after that starts at %s. ",
    "That slack ends and the river heads north again starting at %s. ",
    "The second high tide is at %s. ",
    "The flood continues until slack at %s. ",
    "And the ebb starts at %s. "    
    ]
    
def speechify_all(data):
    ctr = 0
    outPhrase = "test Test"
    prefix = '<say-as interpret-as="time">'
    suffix = '</say-as>'
    times = []
    for datum in data:                      # go through the array of high/low tides
        times.append(datum.time)                # this is the first high or low tide
        times.append(datum.nextSlack)           # this is the start of the next slack
        times.append(datum.nextSlackEnd)        # end of the slack
    if data[0].type == 'H':
        outputTemplate = highTideArray
    elif data[0].type == 'L':
        outputTemplate = lowTideArray
    outPhrases = ""
    for time in times:
        newSuffix = suffix
        if ctr > 6:
            if time[0] == '0':
                newSuffix = suffix + ' the next day'
        inFix = prefix + time + newSuffix
        outPhrase = outputTemplate[ctr] %inFix
        outPhrases = outPhrases + outPhrase
        ctr = ctr + 1
    return outPhrases
    
def speechify_high_tides(data):
    dbg = True
    if dbg: print("in speechify_high_tides")
    prefix1 = 'High tide is at <say-as interpret-as="time">'
    prefix2 = 'High tides are at <say-as interpret-as="time">'
    suffix = '</say-as>.'
    infix = '</say-as> and <say-as interpret-as="time">'
    highTideTimes = []
    lowTideTimes = []
    slackWaterTimes = []
    for item in data:
        if item.type == 'H':
            highTideTimes.append(item.time)
        if item.type == 'L':
            lowTideTimes.append(item.time)
    highTideText = ''
    if len(highTideTimes) > 1:
        highTideText = prefix2+highTideTimes[0]+infix+highTideTimes[1]+suffix
    else:
        if len(highTideTimes) == 1:
            highTideText = prefix1+highTideTimes[0]+suffix
    return highTideText
    
def speechify_low_tides(data):
    prefix1 = 'Low tide is at <say-as interpret-as="time">'
    prefix2 = 'Low tides are at <say-as interpret-as="time">'
    suffix = '</say-as>.'
    infix = '</say-as> and <say-as interpret-as="time">'
    lowTideTimes = []
    for item in data:
        if item.type == 'L':
            lowTideTimes.append(item.time)
    lowTideText = ''
    if len(lowTideTimes) > 1:
        lowTideText = prefix2+lowTideTimes[0]+infix+lowTideTimes[1]+suffix
    else:
        if len(lowTideTimes) == 1:
            lowTideText = prefix1+lowTideTimes[0]+suffix
    return lowTideText
    
def speechify_slack_waters(data):
    print("in speechify_slack_waters")
    prefix1 = 'Slack water is at <say-as interpret-as="time">'
    prefix2 = 'Slack waters are at <say-as interpret-as="time">'
    suffix = '</say-as>.'
    infix = '</say-as> and <say-as interpret-as="time">'
    slackTimes = []
    for item in data:
        slackTimes.append(item.nextSlack)
    slackText = ''
    if len(slackTimes) > 1:
        slackText = prefix2+slackTimes[0]+infix+slackTimes[1]+suffix
    else:
        if len(slackTimes) == 1:
            slackText = prefix1+slackTimes[0]+suffix
    return slackText
      
def get_current_events():
    # get today's tide data
    tideDataList = read_data()
    # turn it into a text file
    myText = speechify_all(tideDataList)
    session_attributes = {}
    card_title = "All Events"
    speech_output = myText
    reprompt_text = myText 
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
def get_current_events_date(intent,session):
    prefix = '<say-as interpret-as="time">'
    suffix = '</say-as>'
    if 'Date' in intent['slots']:
        recognized_date = intent['slots']['Date']['value']
        tideDataList = read_dates_data(recognized_date)
        speech_output = speechify_all(tideDataList)
        session_attributes = {}
        card_title = "All " + recognized_date
        reprompt_text = speech_output 
        should_end_session = True
        return build_response({}, build_speechlet_response(
            card_title, speech_output, "", should_end_session))
    else:
        return get_current_events()
        
def get_high_tide_response():
    # get today's tide data
    tideDataList = read_data()
    # turn it into a text file
    myText = speechify_high_tides(tideDataList)
    session_attributes = {}
    card_title = "High Tide Today"
    speech_output = myText
    reprompt_text = myText 
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
def get_high_tide_response_date(intent,session):
    prefix = '<say-as interpret-as="time">'
    suffix = '</say-as>'
    if 'Date' in intent['slots']:
        recognized_date = intent['slots']['Date']['value']
        tideDataList = read_dates_data(recognized_date)
        speech_output = speechify_high_tides(tideDataList)
        session_attributes = {}
        card_title = "High Tide " + recognized_date
        reprompt_text = speech_output 
        should_end_session = True
        return build_response({}, build_speechlet_response(
            card_title, speech_output, "", should_end_session))
    else:
        return get_high_tide_response()
        
def get_slack_water_response():
    # get today's tide data
    tideDataList = read_data()
    # turn it into a text file
    myText = speechify_slack_waters(tideDataList)
    session_attributes = {}
    card_title = "Slack Water Today"
    speech_output = myText
    reprompt_text = myText 
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
def get_slack_water_response_date(intent,session):
    prefix = '<say-as interpret-as="time">'
    suffix = '</say-as>'
    if 'Date' in intent['slots']:
        recognized_date = intent['slots']['Date']['value']
        tideDataList = read_dates_data(recognized_date)
        speech_output = speechify_slack_waters(tideDataList)
        session_attributes = {}
        card_title = "Slack Water " + recognized_date
        reprompt_text = speech_output 
        should_end_session = True
        return build_response({}, build_speechlet_response(
            card_title, speech_output, "", should_end_session))
    else:
        return get_slack_water_response()

def get_low_tide_response():
    # get today's tide data
    tideDataList = read_data()
    # turn it into a text file
    myText = speechify_low_tides(tideDataList)
    session_attributes = {}
    card_title = "Low Tide Today"
    speech_output = myText
    reprompt_text = myText 
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
 
def get_low_tide_response_date(intent,session):
    prefix = '<say-as interpret-as="time">'
    suffix = '</say-as>'
    if 'Date' in intent['slots']:
        recognized_date = intent['slots']['Date']['value']
        tideDataList = read_dates_data(recognized_date)
        speech_output = speechify_low_tides(tideDataList)
        session_attributes = {}
        card_title = "Low Tide " + recognized_date
        reprompt_text = speech_output 
        should_end_session = True
        return build_response({}, build_speechlet_response(
            card_title, speech_output, "", should_end_session))
    else:
        return get_low_tide_response()    
                
# --------------- Helpers that build all of the responses ----------------------
def stripMarkup(text):
    target1 = '<say-as interpret-as="time">'
    target2 = '</say-as>'
    targetList = [target1,target2]
    for targ in targetList:
        text = text.replace(targ,"")
    return text   
    
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    output = stripMarkup(output)
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': '<speak>' + output + '</speak>'
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': '<speak>' + reprompt_text + '</speak>'
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():

    session_attributes = {}
    card_title = "Introduction"
    speech_output = "Hello.  I can tell you the predicted high and low tides times, and the slack water times, on the " \
    "Hudson River near The Battery. An odd thing about the Hudson River is the water keeps coming in after high tide for awhile, " \
    " and keeps moving out after low tide for awhile.  So, the slack water time (when the river is not moving) is different from the high or low tide time. " \
    "In fact, slack water occurs about 2 hours and 20 minutes after a high tide, and about 2 hours and 40 minutes after a low tide.  "\
    "The slack water duration is about 35 minutes. " \
    "If you're planning on rowing a boat on the Hudson, you really care about slack water, since sometimes the river flows faster than you can paddle. "  \
    "This app should help you plan your trip so you can make it back OK. "  \
    "This data is published by NOAA and Sandy Hook Pilots, and is based on astronomical events.  Actual water flows "\
    "can be affected by unusual rain or wind, so use this as an approximation. To use the app you can say things like "\
    "'when is high tide',  'when is low tide November 10', or 'when is slack water today'.  For a summary of all the data, say 'what are the current events?'. " \
    "You can launch the app by saying, for example, 'Alexa, ask Battery Current Advisor, when is slack water tomorrow?'" 
    reprompt_text = "Say 'help' or 'goodbye'. " 
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
def get_my_date_response(intent,session):
    card_title = "Recognized AMAZON.DATE"
    speech_output = "we are almost there "
    prefix = '<say-as interpret-as="time">'
    suffix = '</say-as>'
    if 'Date' in intent['slots']:
        recognized_date = intent['slots']['Date']['value']
        card_title = recognized_date
        speech_output = "getting closer"
        speech_output = "I think you said" + prefix + recognized_date + suffix

    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, "", should_end_session))
        
def get_my_time_response(intent,session):
    card_title = "Recognized AMAZON.TIME"
    prefix = '<say-as interpret-as="time">'
    suffix = '</say-as>'
    if 'Time' in intent['slots']:
        recognized_time = intent['slots']['Time']['value']
        card_title = recognized_time
        speech_output = "I think you said" + prefix + recognized_time + suffix
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, "", should_end_session))

def get_goodbye_response():
    card_title = "Session Ended"
    speech_output = "Goodbye "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, "", should_end_session))
        
def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Goodbye."
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))




# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    

    if intent_name == "GiveMeCurrentEvents":
        return get_current_events()  
    if intent_name == "GiveMeCurrentEventsDate":
        return get_current_events_date(intent,session)  
    if intent_name == "WhenIsHighTide":
        return get_high_tide_response()
    if intent_name == "WhenIsHighTideDate":
        return get_high_tide_response_date(intent,session)
    if intent_name == "WhenIsSlackWater":
        return get_slack_water_response()
    if intent_name == "WhenIsSlackWaterDate":
        return get_slack_water_response_date(intent,session)
    if intent_name == "WhenIsLowTide":
        return get_low_tide_response()
    if intent_name == "WhenIsLowTideDate":
        return get_low_tide_response_date(intent,session)
    if intent_name == "DateEvent":
        return get_my_date_response(intent,session)   
    if intent_name == "TimeEvent":
        return get_my_time_response(intent,session)   
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "ThankYouGoodbyeIntent":
        return get_goodbye_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# echo ask app framework ( what are today's current events, when is tomorrow, when is 9 fifteen )
# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("starting up" + "event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
