WITH ordered AS (
  SELECT
    customer_id,
    membership_start_date,
    membership_end_date,
    membership_status,
    LAG(membership_status) OVER (
      PARTITION BY customer_id
      ORDER BY membership_start_date
    ) AS prev_status,
    LEAD(membership_status) OVER (
      PARTITION BY customer_id
      ORDER BY membership_start_date
    ) AS next_status
  FROM membership_history
),

start_events AS (
  SELECT
    customer_id,
    membership_start_date AS change_date,
    CASE
      WHEN prev_status IS NULL THEN
        -- Первый период: считаем, что до него был Non-member
        CASE membership_status
          WHEN 'Free' THEN 'WarmStart'
          WHEN 'Paid' THEN 'ColdStart'
          -- Если статус Non-member, то перехода нет (можно исключить)
          ELSE NULL
        END
      ELSE
        -- Переход из предыдущего статуса в текущий
        CASE
          WHEN prev_status = 'Free' AND membership_status = 'Paid' THEN 'Convert'
          WHEN prev_status = 'Paid' AND membership_status = 'Free' THEN 'ReverseConvert'
          WHEN prev_status = 'Paid' AND membership_status = 'Non-member' THEN 'Cancel'
          WHEN prev_status = 'Free' AND membership_status = 'Non-member' THEN 'Cancel'
          WHEN prev_status = 'Non-member' AND membership_status = 'Paid' THEN 'ColdStart'
          WHEN prev_status = 'Non-member' AND membership_status = 'Free' THEN 'WarmStart'
          WHEN prev_status = 'Paid' AND membership_status = 'Paid' THEN 'Renewal'
          WHEN prev_status = 'Free' AND membership_status = 'Free' THEN 'Renewal'
          ELSE NULL
        END
    END AS event
  FROM ordered
),

end_events AS (
  SELECT
    customer_id,
    membership_end_date AS change_date,
    CASE membership_status
      WHEN 'Paid' THEN 'Cancel'
      WHEN 'Free' THEN 'Cancel'
      -- Non-member в конце не порождает события, так как остаётся Non-member
      ELSE NULL
    END AS event
  FROM ordered
  WHERE next_status IS NULL  -- только последний период
)

SELECT customer_id, change_date, event
FROM start_events
WHERE event IS NOT NULL

UNION ALL

SELECT customer_id, change_date, event
FROM end_events
WHERE event IS NOT NULL

ORDER BY customer_id, change_date;