from homeassistant.const import Platform

DOMAIN = "budgetthuis"
BUDGETTHUIS_CLIENT_ID = "mobile"
BUDGETTHUIS_AUTH_URL = "https://accounts.budgetthuis.nl/connect/authorize"
BUDGETTHUIS_TOKEN_URL = "https://accounts.budgetthuis.nl/connect/token"
BUDGETTHUIS_REDIRECT_URI = "budgetthuis://login_success"
BUDGETTHUIS_SCOPE = "mobileApi offline_access openid email idsServiceExternal"

PLATFORMS = [
    Platform.SENSOR
]
