## Для запуска запроса:
1. Создайте таблицу membership_history:
   ```
   CREATE TABLE membership_history (
     customer_id INTEGER,
     membership_start_date TEXT,  -- дата в формате YYYY-MM-DD
     membership_end_date TEXT,
     membership_status TEXT
   );
   ```

2. Заполните ее данными:
   ```
   INSERT INTO membership_history (customer_id, membership_start_date, membership_end_date, membership_status) VALUES
   (114, '2015-01-01', '2015-02-15', 'Free'),
   (114, '2015-02-15', '2015-03-15', 'Paid'),
   (114, '2015-03-15', '2015-04-01', 'Non-member'),
   (114, '2015-04-01', '2015-10-01', 'Paid'),
   (114, '2015-10-01', '2016-01-01', 'Paid');
   ```

3. Выполните запрос.
