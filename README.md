# praktikum_new_diplom
## Запуск проекта:
cd foodgram-project-react
cd backend
. venv/Scripts/activate
. venv/bin/activate
cd foodgram
python manage.py runserver
### Создать миграции:
```bash
python manage.py makemigrations
```
### Выполнить миграции:
```bash
python manage.py migrate
```
### Создать суперпользователя:
```bash
python manage.py createsuperuser
```
### Запустить проект:
```bash
python manage.py runserver
```
cd foodgram-project-react
cd infra
docker-compose up
http://localhost

cd frontend
npm run start

git add .
git commit -m "Push to Docker Hub"
git push