## Тестовые задания для Python

### Задача 1: Что может быть проще SQL?

Вам дана таблица в postgres, которая представляет из себя список сотрудников с их зарплатами и отделами.
Необходимо написать запрос, который будет выбирать человека с максимальной зарплатой из каждого отдела. В качестве тестовых данных можете использовать [дамп таблицы](employee.sql), пример схемы:

```text
postgres=# \d employee
            Table "public.employee"
   Column   |         Type          | Modifiers
------------+-----------------------+-----------
 id         | integer               | not null
 name       | character varying(30) |
 department | character varying(30) |
 salary     | integer               |
Indexes:
    "employee_pkey" PRIMARY KEY, btree (id)
```

Если нам нужна информация о всех сотрудниках, имеющих максимальную зарплату в отделе(в случае, когда она одинаковая):

```text
SELECT m.name, m.department, t.mx FROM (SELECT department, max(salary) as mx from employee GROUP BY department) t JOIN employee m on m.department = t.department and t.mx = m.salary;
```

Если достаточно информации о любом из сотрудников с максимальной зарплатой:

```text
SELECT DISTINCT ON (department) department, name, salary from employee ORDER BY department, salary DESC;
```

Запустить запросы, посмотреть результ:

```text
make sql
```
