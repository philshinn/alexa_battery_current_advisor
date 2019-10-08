#---------------------------------------------

from batteryCurrentAdvisor import *

startupEvent = {
  "session": {
    "new": True,
    "sessionId": "amzn1.echo-api.session.[unique-value-here]",
    "attributes": {},
    "user": {
      "userId": "amzn1.ask.account.[unique-value-here]"
    },
    "application": {
      "applicationId": "amzn1.ask.skill.[unique-value-here]"
    }
  },
  "version": "1.0",
  "request": {
    "locale": "en-US",
    "timestamp": "2016-10-27T18:21:44Z",
    "type": "LaunchRequest",
    "requestId": "amzn1.echo-api.request.[unique-value-here]"
  },
  "context": {
    "AudioPlayer": {
      "playerActivity": "IDLE"
    },
    "System": {
      "device": {
        "supportedInterfaces": {
          "AudioPlayer": {}
        }
      },
      "application": {
        "applicationId": "amzn1.ask.skill.[unique-value-here]"
      },
      "user": {
        "userId": "amzn1.ask.account.[unique-value-here]"
      }
    }
  }
}

def testFunctions():
    dbg = True
    url = "https://tidesandcurrents.noaa.gov/api/datagetter?product=predictions&application=NOS.COOPS.TAC.WL&date=today&datum=MLLW&station=8518750&time_zone=lst_ldt&units=english&interval=hilo&format=json"
    myData = get_raw_data(url)
    if dbg: print(myData)
    data = read_data()
    if dbg:
        print("data length=",len(data),"data=",data)
        for elem in data:
            print(vars(elem))   
    
if __name__ == "__main__":
    dbg = True
    data = testFunctions()

