"""SQL-запросы для поиска сотрудников с максимальной зарплатой в отделе."""

# Запрос для получения всех сотрудников с максимальной зарплатой в каждом отделе
# (если несколько человек получают максимум, будут выведены все)
QUERY_ALL_MAX = """
SELECT m.name, m.department, t.max_salary
FROM (
    SELECT department, MAX(salary) as max_salary
    FROM employee
    GROUP BY department
) t
JOIN employee m ON m.department = t.department AND t.max_salary = m.salary
ORDER BY m.department;
"""

# Запрос для получения одного сотрудника с максимальной зарплатой в отделе
# (если несколько, будет выбран первый по алфавиту имени — зависит от сортировки)
QUERY_ONE_MAX = """
SELECT DISTINCT ON (department) department, name, salary
FROM employee
ORDER BY department, salary DESC, name;
"""