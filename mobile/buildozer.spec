[app]
title = ML Interview Prep
package.name = mlinterviewprep
package.domain = com.mlinterviewprep
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
# Include the shared logic files from the project root
source.include_patterns = ../config.py,../data_manager.py,../question_generator.py,../scenario_questions.py
version = 1.0.0

requirements = python3,kivy==2.3.0,httpx,python-dotenv,certifi

orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 33
android.minapi = 26
android.ndk = 25b
android.sdk = 33
android.arch = arm64-v8a

ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.7.0

[buildozer]
log_level = 2
warn_on_root = 1
