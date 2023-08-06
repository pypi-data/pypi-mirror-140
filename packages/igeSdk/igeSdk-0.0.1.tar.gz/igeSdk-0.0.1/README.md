# igeSdk
igeSdk is a compilation of all necessary third party SDKs in order to make your game ready to be published, which contains Analytics, Advertisement, InAppPurchase and CrossPromotion features.

The current implementation status is as below:
- [x] Analytics : Ready (v0.0.1)
- [ ] Advertisement : WIP (ETA: v0.0.2)
- [ ] InAppPurchase : WIP
- [ ] CrossPromotion : WIP

*The SDK supports **Android** and **iOS** platforms. On unsupported platforms (Windows, Linux, MacOS, ...), it the code still running with dummy functionalities.*

## Configuration and Initialization
To config the SDK, you need to create `igeSdk.config` which is a json file contains settings for different modules.

Configuration for Advertisement, InAppPurchase and CrossPromotion is WIP.

To initialize the SDK, just `import igeSdk` and call `initialize()` method in your main logic code, like below:
```py
import igeSdk

class GameManager(Script):

    def onStart(self):
        igeSdk.initialize()
        # Other initialization stuffs
```

The code above will inialize all the enabled modules which are configured in the configuration file.

*Notice, the SDK only initialize modules which have been configured. So, to disable unwanted modules, just remove their settings out of the configuration file.*

## Analytic

The Analytics module is used in order to send informations to the different analytics platform. We are currently using Facebook, GameAnalytics AppsFlyer.

To configure Analytics features, put those settins into `igeSdk.config`:
```
{
  "FacebookAppId": "YOUR_FACEBOOK_APP_ID",
  "AppsFlyerAppid": "YOUR_APPSFLYER_APP_ID",
  "AppsFlyerApiKey": "YOUR_APPSFLYER_API_KEY",
  "GameAnalyticsGameKey": "YOUR_GAMEANALYTIC_API_KEY",
  "GameAnalyticsSecretKey": "YOUR_GAMEANALYTIC_SECRET_KEY"
}
```

Trackers for Advertisement, InAppPurchase and CrossPromotion modules are sent automatically by the SDK. Game developers should only focus on Progression and Design events to boost their games' performance and revenues, using API below:
```py
import igeSdk
from igeSdk import Analytics

# Level started event: send when player start new level
Analytics.levelStarted(levelName: str)

# Level passed event: send when player successfully passed the level
Analytics.levelPassed(levelName: str, score: int)

# Level failed event: send when player failed the level
Analytics.levelFailed(levelName: str, score: int)

# Custom event: used to track other stuffs like game design events, game states, ...
Analytics.customEvent(eventName: str, eventValue_optional: float)

```

## Advertisement
WIP - ETA: v0.0.2

## InAppPurchase
WIP

## CrossPromotion
WIP