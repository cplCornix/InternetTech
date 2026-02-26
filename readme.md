## Для запуска запроса:
1. Создайте таблицу orders в вашей среде:
   ```sql
   CREATE TABLE orders
   (
      Customer_name VARCHAR(50),
      Order_day DATE,
      Order_Id VARCHAR(10),
      Prod_Name VARCHAR(10),
      Qty INTEGER,
      Price INTEGER
    );
   ```
   
2. Заполните ее данными:
   ```sql
   INSERT INTO orders (Customer_name, Order_day, Order_Id, Prod_Name, Qty, Price) VALUES
   ('Mahesh', '2023-01-01', '01', 'iPhone',  1, 10),
   ('Mahesh', '2023-01-01', '01', 'iPad',    1, 20),
   ('Mahesh', '2023-01-01', '01', 'Airpods', 1, 20),
   ('Wayne',  '2023-01-01', '02', 'iPhone',  1, 10),
   ('Wayne',  '2023-01-01', '02', 'shirt',   1, 20),
   ('Wayne',  '2023-01-01', '02', 'shoe',    1, 20);
   ```

3. Выполните запрос.

#### Примечание:
В разных СУБД функция извлечения месяца может отличаться (```DATE_TRUNC``` в PostgreSQL или ```DATE_FORMAT``` в MySQL)
