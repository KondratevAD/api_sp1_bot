# Бот-ассистент

## Описание
Телеграм-бота, который:
* обращается к API сервиса Практикум.Домашка;
* узнает, взята ли домашка в ревью, проверена ли она, провалена или принята;
* отправляет результат в Телеграм-чат.
Бот регулярно опрашивает API домашки и при получении обновлений парсить ответ и отправляет сообщение в Телеграм.
Также Бот логирует момент своего запуска и каждую отправку сообщения. Сообщения уровня ERROR бот логирует и отправляет Телеграм.

## Стек технологий
Python 3.9.4, 
