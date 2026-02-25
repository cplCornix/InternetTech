WITH ranked_transactions AS (
    SELECT 
        user_id,
        item,
        ROW_NUMBER() OVER (
            PARTITION BY user_id 
            ORDER BY transaction_ts ASC, transaction_id ASC
        ) AS rn
    FROM transactions
)
SELECT 
    user_id,
    item
FROM ranked_transactions
WHERE rn = 1
ORDER BY user_id;