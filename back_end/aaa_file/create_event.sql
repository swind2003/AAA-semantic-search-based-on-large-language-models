-- CREATE EVENT [IFNOT EXISTS] event_name
--     　　 ON SCHEDULE schedule(调度时间设置)
--     　　 [ON COMPLETION [NOT] PRESERVE]
--     　　 [ENABLE | DISABLE | DISABLE ON SLAVE]
--     　　 [COMMENT 'comment']
--     　　 DO sql_statement;
-- 定时事件
-- 每小时刷新 将用户的提问次数变为8
DROP EVENT
IF
	EXISTS flush_query_times;
CREATE EVENT flush_query_times ON SCHEDULE EVERY 1 HOUR STARTS '2023-11-26 21:00:00' DO
BEGIN
		UPDATE users 
		SET users.current_query_times = users.query_times;
END;
-- 每隔一天将用户被限制登录的天数减一
DROP EVENT
IF
	EXISTS minus_one_day;
CREATE EVENT minus_one_day ON SCHEDULE EVERY 1 DAY STARTS '2023-11-26 00:00:00' DO
BEGIN
		UPDATE users 
		SET restriction_time = restriction_time - 1 
	WHERE
		restriction_time > 0;

END;