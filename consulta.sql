select distinct COLUMN_NAME from information_schema.columns 
where table_schema = 'tpch' 
and table_NAME not in 
(select table_name from information_schema.views 
where table_schema not in 
('sys','information_schema', 'mysql', 'performance_schema'))
and column_name not in -- minus primary keys
(select sta.column_name
from information_schema.tables as tab
inner join information_schema.statistics as sta
        on sta.table_schema = tab.table_schema
        and sta.table_name = tab.table_name
        and sta.index_name = 'primary'
where tab.table_schema = 'tpch'
    and tab.table_type = 'BASE TABLE')
and column_name not in  -- minus foreign keys
(select  kcu.column_name as fk_columns
from information_schema.referential_constraints fks
join information_schema.key_column_usage kcu
     on fks.constraint_schema = kcu.table_schema
     and fks.table_name = kcu.table_name
     and fks.constraint_name = kcu.constraint_name);