# ML_PRO2026

## 1. Pytest
1 skipped, т.к. бд не поднимается отдельно, а пихать pytest внутрь контейнера для полноценного теста абсурд. Для Dockerfile url для бд раскомменчивается.
<img width="1285" height="637" alt="image" src="https://github.com/user-attachments/assets/97eaf7c2-c080-4084-83f4-cbc85bcdf5de" />

Колхозный вариант - сделать проверку с помощью докерного адреса контейнера с бд, который будет поднят "позже".
<img width="1202" height="405" alt="image" src="https://github.com/user-attachments/assets/4275a879-ace9-4989-a4f9-0ac10a72647e" />

<img width="1290" height="897" alt="image" src="https://github.com/user-attachments/assets/6f56c91d-985d-41d1-ae29-f57e9bb1d727" />

<img width="852" height="297" alt="image" src="https://github.com/user-attachments/assets/c557dcd2-3c9f-4adb-84fe-6d501e71bae0" />


## 2. Select из логов
<img width="1280" height="916" alt="image" src="https://github.com/user-attachments/assets/34f90e48-2590-40eb-815b-c35c13af7b6e" />


## 3. Kubernetes
<img width="1281" height="832" alt="image" src="https://github.com/user-attachments/assets/13b1cf64-5e6f-4345-85f6-ccc55fae6364" />

Журнал проблем :
- Проблемы с окружениями - решения перезагрузки и пересборки
- Был казус с пересозданием схемы бд - забыл что том хранится на хостовой тачке
