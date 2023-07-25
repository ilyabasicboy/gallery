<h2>Установка</h2>
<ul>
	<li>Скачать проект: git clone git@github.com:ilyabasicboy/gallery.git</li>
	<li>Установить зависимости: pip install -r requirements.txt</li>
	<li>Сделать миграции: python manage.py migrate</li>
</ul>

<h2>Описание сервиса</h2>

Проектируемый сервис предназначен для обеспечения возможности обмена файлами пользователями приложений для обмена мгновенными сообщениями.
Приложения реализуют протокол XMPP, и работают по клиент-серверной архитектуре. При обмене файлов, отправитель файла загружает его в сетевое хранилище, получателю пересылается ссылка на загруженный файл.
Сервис также имеет возможности для управления загруженными файлами (просмотр списка загруженных файлов, удаление файлов, и т.д.)


<h2>Описание API</h2>

<h3>Авторизация</h3>
<div>Bearer Token:</div>
<div>Token требуют передачи параметров авторизации в заголовке HTTP-запроса вида: Authorization Bearer <значение> 
Значение токена получается методом. Используется конкретным пользователем для управлением медиагалереей.</div>

<h3>GET api/v1/files/slot/</h3>
<div>Получение ответа, можно ли загружать данный файл. Метод принимает гет параметры либо json с метаданными файла(размер, имя, хэш файла).
Если данный пользователь уже имеет такой файл, то генерируется новая ссылка на этот файл. Если такой файл еще не загружен, то приходит ответ 200 и информация о квоте пользователя.</div>

<h3>POST api/v1/files/upload/</h3>
<div>Загрузка файла на сервер. Метод принимает multipart/form-data с данными файла. Если файл уже есть, то отдаётся ссылка на файл.</div>

<h3>GET  api/v1/files/</h3>
<div>Получение списка загруженных файлов для конкретного пользователя.</div>

<h3>DELETE api/v1/files/</h3>
<div>Удаление медиа-файла (симлинка). Если удаляется последний симлинк на файл с таким хэшем, то удаляется и сам физический файл.
Если указать временной промежуток или media_type, то удалятся все объекты, подходящие под эти параметры. Если указать id, то удалится один конкретный файл.</div>

<h3>POST api/v1/account/xmpp_code_request/</h3>
<div>Запрос одноразового кода по XMPP для получения токена.</div>

<h3>POST api/v1/account/xmpp_auth/</h3>
<div>Проверка одноразового кода и выдача токена.</div>
	
<h3>GET  api/v1/account/tokens/</h3>
<div>Получение списка всех токенов пользователя.</div>

<h3>DELETE  api/v1/account/tokens/</h3>
<div>Удаление токена.</div>

<h3>DELETE api/v1/account/</h3>
<div>Удаление аккаунта</div>

<h3>GET  api/v1/account/quota/</h3>
<div>Получение информации о квоте пользователя.</div>

<h3>PUT  api/v1/account/quota/</h3>
<div>Админский запрос для изменение квоты пользователя.</div>


<h3>GET api/v1/account/list/</h3>
<div>Админский запрос для получения списка всех пользователей и информации об их квотах.</div>


<h3>POST api/v1/avatar/upload/</h3>
<div>Загрузка файла на сервер. Метод принимает multipart/form-data с данными файла. Если файл уже есть, то отдаётся ссылка на файл. Загруженный файл обрезается до размеров 1536x1536  с центром кропа посередине(если изначальный размер > 1536, иначе делается кроп по наименьшей стороне) Сохраняется в оригинальном формате.</div>
<div>Названия thumbnail составляются как size_filename.ext. </div>
<div>Пример: 48_selfie_avatar.webp, 256_selfie_avatar.png.</div>

<h3>GET  api/v1/avatar/</h3>
<div>Получение списка загруженных аватарок для конкретного пользователя. </div>

<h3>DELETE api/v1/avatar/</h3>
<div>Удаление аватарки.</div>

<h3>GET  api/v1/files/stats/</h3>
<div>Получение статистики по использованию места: категория файла(медиа тип), количество файлов, использованное ими место.
Можно использовать фильтры(медиа тайп, дата больше чем, дата меньше чем).</div>
