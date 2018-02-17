# OK Mail Parser

## Uppsetning

* [virtualenv](https://python-guide.readthedocs.io/en/latest/dev/virtualenvs/#virtualenv) er notað upp á 
að halda utanum dependencies. Sjá [skjölun](https://python-guide.readthedocs.io/en/latest/dev/virtualenvs/#virtualenv) 
virtualenv er sett upp. 
* Dependency eru geymd í requirements.txt
* Þegar dependncy er bætt við þarf að frysta það með `pip freeze > requirements.txt`
* Dependency sett in með `pip install -r requirements.txt`
* Afrita credentials-example.py yfir í credentials.py og fylla út. Hægt er að nota eigið netfang og lykilorð í þróun. 
credentials.py er í `.gitignore` og fer því ekki óvart inn í github.

## Skjölun

Autotask python api: https://atws.readthedocs.io/ 

## Þróunarumhverfi

Mælt er með að nota [PyCharm Community Edition](https://www.jetbrains.com/pycharm/download) frá Intellij sem er frítt
og byrja á því að læra á debugger-inn. Debugger-inn er gulls ígildi þegar það kemur að því að kynnast gögnunum. 

[Kennsla á python debugger i PyCharm](https://www.jetbrains.com/help/pycharm/part-1-debugging-python-code.html)
