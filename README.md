# Budget Thuis Home Assistant Integration
A custom integration for Budget Thuis. 

## Install integration
- Download the browser extension and install it.
  - You can find the extension here: https://github.com/arjenbos/ha-budget-thuis-browser-extensions
- Add the repository to HACS.
- Install the integration via HACS.
- Add the integration:
  - Name: whatever you like
  - Client ID: whatever you like (will be ignored).
  - Client secret: whatever you like (will be ignored).
  - You will be redirected to Budget Thuis:
    - If you aren't logged in, then Budget Thuis will show you a login page.
    - If you're already logged in, then it will redirect you back to Home Assistant oAuth2 callback (check your Home Assistant URL!).
- Done!
