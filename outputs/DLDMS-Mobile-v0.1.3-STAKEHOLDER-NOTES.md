# DLDMS Mobile Stakeholder Build

## Build Details

- App: Disability Labour Data MIS
- Android package: `zm.org.zilard.dldms`
- Version: `0.1.3`
- Android build: `4`
- Format: installable APK
- APK file: `DLDMS-Mobile-v0.1.3-build4.apk`
- SHA-256: `BD088A0437974628E76AFD0C6E532A424832E02D6E5C909368E45B629B13C34B`

## Install From Expo

Open this link on the Android phone and select **Install**:

https://expo.dev/accounts/dleza/projects/dldms-mobile/builds/6ee55cb5-6353-4df6-866d-31d9bd0b6805

The Expo-hosted build expires on 5 October 2026. The APK file saved beside this note does not depend on that link and can be shared directly.

Android may ask for permission to install an app from the browser, email client, file manager, or messaging app used to open the APK.

## Connect To Django

This prototype currently connects to the Django server through the laptop's local network address:

`http://192.168.1.63:8000/api/mobile`

For a local demonstration:

1. Connect the laptop and stakeholder phones to the same Wi-Fi network.
2. From the Django project folder, run `python manage.py runserver 0.0.0.0:8000`.
3. Confirm Windows Firewall allows Python/Django on private networks.
4. Sign in with the Django account assigned to the stakeholder.

The API server address is editable on the mobile sign-in screen. If the laptop's Wi-Fi address changes, enter the new address before signing in.

For testing from different offices or mobile networks, deploy Django to a secure public HTTPS address and use that address in the app.
