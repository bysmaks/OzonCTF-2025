# BimBim | Hard | Misc

## Информация

NO NO NO MISTER GOSHA YOU ACTUALLY NEED TO READ PYTHON SOURCE CODE. Maybe python license too? flag.txt located in the same directory as task.py

nc misc.ozon-ctf-2025.ru 9235

## Деплой

Указываем команду необходимую для запуска задачи на сервере

```sh
cd deploy
docker-compose up --build -d
```

## Выдать участинкам

public/task.py
IP:9235 сервера

## Описание

Прочитать python license.

## Решение

Недавно я задумался как работает функция `license` в python. Не могут же это быть обычные принты?
Так и есть:
https://github.com/python/cpython/blob/0dbaeb94a8b39972ebda7782b50bb49488951e3c/Lib/site.py#L447

Как видим, он кладет какие-то файлы в путь и считывает их:
```python
builtins.license = _sitebuiltins._Printer(
    "license",
    "See https://www.python.org/psf/license/",
    files, dirs)
```

Вот собственно `_Printer`:
https://github.com/python/cpython/blob/3.11/Lib/_sitebuiltins.py#L29

Нас интересует что происходит при вызове `license`:
```python
class _Printer(object):
    def __init__(self, name, data, files=(), dirs=()):
        import os
        self.__name = name
        self.__data = data
        self.__lines = None
        self.__filenames = [os.path.join(dir, filename)
                            for dir in dirs
                            for filename in files]

    def __setup(self):
        if self.__lines:
            return
        data = None
        for filename in self.__filenames:
            try:
                with open(filename, encoding='utf-8') as fp:
                    data = fp.read()
                break
            except OSError:
                pass
        if not data:
            data = self.__data
        self.__lines = data.split('\n')
        self.__linecnt = len(self.__lines)

    # ...

    def __call__(self):
        self.__setup()
        prompt = 'Hit Return for more, or q (and Return) to quit: '
        lineno = 0
        while 1:
            try:
                for i in range(lineno, lineno + self.MAXLINES):
                    print(self.__lines[i])
            except IndexError:
                break
            else:
                lineno += self.MAXLINES
                key = None
                while key is None:
                    key = input(prompt)
                    if key not in ('', 'q'):
                        key = None
                if key == 'q':
                    break
```

Как видим при вызове `_Printer(...)(my_params)` он считает нужный нам файл. Так давайте вызовем `type(license)` с нужными нам параметрами и прочитаем `flag.txt`.

Осталось обойти довольно тривиальные ограничения `'flag' in inp` и все готово:

```python
type(license)(0,0,('f'+'lag'+chr(46)+'txt',),(chr(46),))()
```

[Эксплоит](solve/sol.py)

## Флаг

`ozonctf{BIMBIM_BAMBAM_01230cxdsa3rew}`
