import pyodbc
import json
import pprint
import time
from States import States
pyodbc.pooling = False

class Database:

    # Only primary and foreign keys
    # tables = {
    #     'customer': ['c_custkey', 'c_nationkey'],
    #     'lineitem': ['l_orderkey', 'l_linenumber', 'l_partkey', 'l_suppkey'],
    #     'nation': ['n_nationkey', 'n_regionkey'],
    #     'orders': ['o_orderkey', 'o_custkey'],
    #     'part': ['p_partkey'],
    #     'partsupp': ['ps_partkey', 'ps_suppkey'],
    #     'region': ['r_regionkey'],
    #     'supplier': ['s_suppkey', 's_nationkey']
    # }

    # Only columns used in queries  
    '''tables = {
        'customer': ['c_custkey', 'c_nationkey', 'c_name', 'c_address', 'c_comment'],
        'lineitem': ['l_orderkey', 'l_linenumber', 'l_partkey', 'l_suppkey', 'l_extendedprice', 'l_linestatus', 'l_tax', 'l_linenumber', 'l_comment'],
        'nation': ['n_nationkey', 'n_regionkey', 'n_comment'],
        'orders': ['o_orderkey', 'o_custkey', 'o_orderpriority', 'o_shippriority', 'o_clerk', 'o_totalprice'],
        'part': ['p_partkey', 'p_mfgr', 'p_retailprice', 'p_comment'],
        'partsupp': ['ps_partkey', 'ps_suppkey', 'ps_comment'],
       'region': ['r_regionkey', 'r_comment'],
        'supplier': ['s_suppkey', 's_nationkey', 's_name', 's_address', 's_phone', 's_acctbal']
    }'''
    S = States(3)
    tables = S.getStates()



    queries = [
        "select l_returnflag, l_linestatus, sum(l_quantity) as sum_qty, sum(l_extendedprice) as sum_base_price, sum(l_extendedprice * (1 - l_discount)) as sum_disc_price, sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge, avg(l_quantity) as avg_qty, avg(l_extendedprice) as avg_price, avg(l_discount) as avg_disc, count(*) as count_order from lineitem where l_shipdate <= date '1994-7-17' - interval '108' day group by l_returnflag, l_linestatus order by l_returnflag, l_linestatus;",
        "select s_acctbal, s_name, n_name, p_partkey, p_mfgr, s_address, s_phone, s_comment from part, supplier, partsupp, nation, region where p_partkey = ps_partkey and s_suppkey = ps_suppkey and p_size = 30 and p_type like '%STEEL' and s_nationkey = n_nationkey and n_regionkey = r_regionkey and r_name = 'ASIA' and ps_supplycost = ( select min(ps_supplycost) from partsupp, supplier, nation, region where p_partkey = ps_partkey and s_suppkey = ps_suppkey and s_nationkey = n_nationkey and n_regionkey = r_regionkey and r_name = 'ASIA' ) order by s_acctbal desc, n_name, s_name, p_partkey limit 100;",
        "select l_orderkey, sum(l_extendedprice * (1 - l_discount)) as revenue, o_orderdate, o_shippriority from customer, orders, lineitem where c_mktsegment = 'AUTOMOBILE' and c_custkey = o_custkey and l_orderkey = o_orderkey and o_orderdate < date '1995-03-13' and l_shipdate > date '1995-03-13' group by l_orderkey, o_orderdate, o_shippriority order by revenue desc, o_orderdate limit 10;",
        "select o_orderpriority, count(*) as order_count from orders where o_orderdate >= date '1995-01-01' and o_orderdate < date '1995-01-01' + interval '3' month and exists ( select * from lineitem where l_orderkey = o_orderkey and l_commitdate < l_receiptdate ) group by o_orderpriority order by o_orderpriority;",
        "select n_name, sum(l_extendedprice * (1 - l_discount)) as revenue from customer, orders, lineitem, supplier, nation, region where c_custkey = o_custkey and l_orderkey = o_orderkey and l_suppkey = s_suppkey and c_nationkey = s_nationkey and s_nationkey = n_nationkey and n_regionkey = r_regionkey and r_name = 'MIDDLE EAST' and o_orderdate >= date '1994-01-01' and o_orderdate < date '1994-01-01' + interval '1' year group by n_name order by revenue desc;",
        "select sum(l_extendedprice * l_discount) as revenue from lineitem where l_shipdate >= date '1993-01-01' and l_shipdate < date '1993-01-01' + interval '1' year and l_discount between 0.06 - 0.01 and 0.06 + 0.01 and l_quantity < 24;",
        "select supp_nation, cust_nation, l_year, sum(volume) as revenue from ( select n1.n_name as supp_nation, n2.n_name as cust_nation, extract(year from l_shipdate) as l_year, l_extendedprice * (1 - l_discount) as volume from supplier, lineitem, orders, customer, nation n1, nation n2 where s_suppkey = l_suppkey and o_orderkey = l_orderkey and c_custkey = o_custkey and s_nationkey = n1.n_nationkey and c_nationkey = n2.n_nationkey and (  (n1.n_name = 'JAPAN' and n2.n_name = 'INDIA')  or (n1.n_name = 'INDIA' and n2.n_name = 'JAPAN') ) and l_shipdate between date '1995-01-01' and date '1996-12-31' ) as shipping group by supp_nation, cust_nation, l_year order by supp_nation, cust_nation, l_year;",
        "select o_year, sum(case when nation = 'INDIA' then volume else 0 end) / sum(volume) as mkt_share from ( select extract(year from o_orderdate) as o_year, l_extendedprice * (1 - l_discount) as volume, n2.n_name as nation from part, supplier, lineitem, orders, customer, nation n1, nation n2, region where p_partkey = l_partkey and s_suppkey = l_suppkey and l_orderkey = o_orderkey and o_custkey = c_custkey and c_nationkey = n1.n_nationkey and n1.n_regionkey = r_regionkey and r_name = 'ASIA' and s_nationkey = n2.n_nationkey and o_orderdate between date '1995-01-01' and date '1996-12-31' and p_type = 'SMALL PLATED COPPER' ) as all_nations group by o_year order by o_year;",
        "select nation, o_year, sum(amount) as sum_profit from ( select n_name as nation, extract(year from o_orderdate) as o_year, l_extendedprice * (1 - l_discount) - ps_supplycost * l_quantity as amount from part, supplier, lineitem, partsupp, orders, nation where s_suppkey = l_suppkey and ps_suppkey = l_suppkey and ps_partkey = l_partkey and p_partkey = l_partkey and o_orderkey = l_orderkey and s_nationkey = n_nationkey and p_name like '%dim%' ) as profit group by nation, o_year order by nation, o_year desc;",
        "select c_custkey, c_name, sum(l_extendedprice * (1 - l_discount)) as revenue, c_acctbal, n_name, c_address, c_phone, c_comment from customer, orders, lineitem, nation where c_custkey = o_custkey and l_orderkey = o_orderkey and o_orderdate >= date '1993-08-01' and o_orderdate < date '1993-08-01' + interval '3' month and l_returnflag = 'R' and c_nationkey = n_nationkey group by c_custkey, c_name, c_acctbal, c_phone, n_name, c_address, c_comment order by revenue desc limit 20;",
        "select ps_partkey, sum(ps_supplycost * ps_availqty) as value from partsupp, supplier, nation where ps_suppkey = s_suppkey and s_nationkey = n_nationkey and n_name = 'MOZAMBIQUE' group by ps_partkey having sum(ps_supplycost * ps_availqty) > ( select sum(ps_supplycost * ps_availqty) * 0.0001000000 from partsupp, supplier, nation where ps_suppkey = s_suppkey and s_nationkey = n_nationkey and n_name = 'MOZAMBIQUE' ) order by value desc;",
        "select l_shipmode, sum(case when o_orderpriority = '1-URGENT' or o_orderpriority = '2-HIGH' then 1 else 0 end) as high_line_count, sum(case when o_orderpriority <> '1-URGENT' and o_orderpriority <> '2-HIGH' then 1 else 0 end) as low_line_count from orders, lineitem where o_orderkey = l_orderkey and l_shipmode in ('RAIL', 'FOB') and l_commitdate < l_receiptdate and l_shipdate < l_commitdate and l_receiptdate >= date '1997-01-01' and l_receiptdate < date '1997-01-01' + interval '1' year group by l_shipmode order by l_shipmode;",
        "select c_count, count(*) as custdist from ( select c_custkey, count(o_orderkey) as c_count from customer left outer join orders on c_custkey = o_custkey and o_comment not like '%pending%deposits%' group by c_custkey ) c_orders group by c_count order by custdist desc, c_count desc;",
        "select 100.00 * sum(case when p_type like 'PROMO%' then l_extendedprice * (1 - l_discount) else 0 end) / sum(l_extendedprice * (1 - l_discount)) as promo_revenue from lineitem, part where l_partkey = p_partkey and l_shipdate >= date '1996-12-01' and l_shipdate < date '1996-12-01' + interval '1' month;",
        "select s_suppkey, s_name, s_address, s_phone, total_revenue from supplier, revenue0 where s_suppkey = supplier_no and total_revenue = ( select max(total_revenue) from revenue0 ) order by s_suppkey;",
        "select p_brand, p_type, p_size, count(distinct ps_suppkey) as supplier_cnt from partsupp, part where p_partkey = ps_partkey and p_brand <> 'Brand#34' and p_type not like 'LARGE BRUSHED%' and p_size in (48, 19, 12, 4, 41, 7, 21, 39) and ps_suppkey not in ( select s_suppkey from supplier where s_comment like '%Customer%Complaints%' ) group by p_brand, p_type, p_size order by supplier_cnt desc, p_brand, p_type, p_size;",
        "select sum(l_extendedprice) / 7.0 as avg_yearly from lineitem, part where p_partkey = l_partkey and p_brand = 'Brand#44' and p_container = 'WRAP PKG' and l_quantity < ( select 0.2 * avg(l_quantity) from lineitem where l_partkey = p_partkey );",
        "select c_name, c_custkey, o_orderkey, o_orderdate, o_totalprice, sum(l_quantity) from customer, orders, lineitem where o_orderkey in ( select l_orderkey from lineitem group by l_orderkey having sum(l_quantity) > 314 ) and c_custkey = o_custkey and o_orderkey = l_orderkey group by c_name, c_custkey, o_orderkey, o_orderdate, o_totalprice order by o_totalprice desc, o_orderdate limit 100;",
        "select sum(l_extendedprice* (1 - l_discount)) as revenue from lineitem, part where ( p_partkey = l_partkey and p_brand = 'Brand#52' and p_container in ('SM CASE', 'SM BOX', 'SM PACK', 'SM PKG') and l_quantity >= 4 and l_quantity <= 4 + 10 and p_size between 1 and 5 and l_shipmode in ('AIR', 'AIR REG') and l_shipinstruct = 'DELIVER IN PERSON' ) or ( p_partkey = l_partkey and p_brand = 'Brand#11' and p_container in ('MED BAG', 'MED BOX', 'MED PKG', 'MED PACK') and l_quantity >= 18 and l_quantity <= 18 + 10 and p_size between 1 and 10 and l_shipmode in ('AIR', 'AIR REG') and l_shipinstruct = 'DELIVER IN PERSON' ) or ( p_partkey = l_partkey and p_brand = 'Brand#51' and p_container in ('LG CASE', 'LG BOX', 'LG PACK', 'LG PKG') and l_quantity >= 29 and l_quantity <= 29 + 10 and p_size between 1 and 15 and l_shipmode in ('AIR', 'AIR REG') and l_shipinstruct = 'DELIVER IN PERSON' );",
        "select s_name, s_address from supplier, nation where s_suppkey in ( select ps_suppkey from partsupp where ps_partkey in ( select p_partkey from part where p_name like 'green%' ) and ps_availqty > ( select 0.5 * sum(l_quantity) from lineitem where l_partkey = ps_partkey and l_suppkey = ps_suppkey and l_shipdate >= date '1993-01-01' and l_shipdate < date '1993-01-01' + interval '1' year ) ) and s_nationkey = n_nationkey and n_name = 'ALGERIA' order by s_name;",
        "select s_name, count(*) as numwait from supplier, lineitem l1, orders, nation where s_suppkey = l1.l_suppkey and o_orderkey = l1.l_orderkey and o_orderstatus = 'F' and l1.l_receiptdate > l1.l_commitdate and exists ( select * from lineitem l2 where l2.l_orderkey = l1.l_orderkey and l2.l_suppkey <> l1.l_suppkey ) and not exists ( select * from lineitem l3 where l3.l_orderkey = l1.l_orderkey and l3.l_suppkey <> l1.l_suppkey and l3.l_receiptdate > l3.l_commitdate ) and s_nationkey = n_nationkey and n_name = 'EGYPT' group by s_name order by numwait desc, s_name limit 100;",
        "select cntrycode, count(*) as numcust, sum(c_acctbal) as totacctbal from ( select substring(c_phone from 1 for 2) as cntrycode, c_acctbal from customer where substring(c_phone from 1 for 2) in ('20', '40', '22', '30', '39', '42', '21') and c_acctbal > ( select avg(c_acctbal) from customer where c_acctbal > 0.00 and substring(c_phone from 1 for 2) in ('20', '40', '22', '30', '39', '42', '21') ) and not exists ( select * from orders where o_custkey = c_custkey ) ) as custsale group by cntrycode order by cntrycode;"
    ]

    def __init__(self):
        # SERVER
        self.connection_string = 'DRIVER={MySQL ODBC 8.0};SERVER=127.0.0.1;DATABASE=tpch;UID=dbuser;PWD=dbuser'
        # LOCAL
        #self.connection_string = 'DRIVER={MySQL ODBC 8.0};SERVER=127.0.0.1;DATABASE=tpch;UID=root;PWD=root'

        # Enable logging
        self.conn = pyodbc.connect(self.connection_string)
        self.cur = self.conn.cursor()
        self.cur.execute("SET GLOBAL general_log = 'ON';")
        self.conn.commit()
        self.cur.close()
        self.conn.close()


    """
        Action-related methods
    """
    def drop_index(self, column, table):
        command = ("DROP INDEX idx_%s ON %s;" % (column, table))
        try:
            self.conn = pyodbc.connect(self.connection_string)
            self.cur = self.conn.cursor()
            self.cur.execute(command)
            self.conn.commit()
            self.cur.close()
            self.conn.close()
            print('Dropped index on (%s) %s' % (table, column))
        except pyodbc.Error as ex:
            print("Didn't drop index on %s, error %s" % (column, ex))


    def create_index(self, column, table):
        command = "CREATE INDEX idx_%s ON %s (%s);" % (column, table, column)
        try:
            self.conn = pyodbc.connect(self.connection_string)
            self.cur = self.conn.cursor()
            self.cur.execute(command)
            self.conn.commit()
            self.cur.close()
            self.conn.close()
            print('Created index on (%s) %s' % (table, column))
        except pyodbc.Error as ex:
            print("Didn't create index on %s, error %s" % (column, ex))


    """
        State-related methods
    """
    def get_table_columns(self, table):
        self.conn = pyodbc.connect(self.connection_string)
        self.cur = self.conn.cursor()
        self.cur.execute('SHOW COLUMNS FROM %s;' % table)
        table_columns = list()
        for row in self.cur.fetchall():
            if row[0] not in self.tables[table]:
                #print(row[0])
                table_columns.append(row[0])
        self.conn.commit()
        self.cur.close()
        self.conn.close()
        return table_columns


    def get_table_indexed_columns(self, table):
        self.conn = pyodbc.connect(self.connection_string)
        self.cur = self.conn.cursor()
        self.cur.execute('SHOW INDEXES FROM %s;' % table)
        table_indexes = list()
        for index in self.cur.fetchall():
            if index[2] not in self.tables[table]:
                table_indexes.append(index[4])
        self.conn.commit()
        self.cur.close()
        self.conn.close()
        return table_indexes


    def get_indexes_map(self):
        indexes_map = dict()
        for table in self.tables.keys():
            indexes_map[table] = dict()
            indexed_columns = self.get_table_indexed_columns(table)
            table_columns = self.get_table_columns(table)
            for column in table_columns:
                indexes_map[table][column] = 0
                for index in indexed_columns:
                    if column == index:
                        indexes_map[table][column] = 1

        return indexes_map 

    
    """
        Environment-related methods
    """
    def reset_indexes(self):
        # FETCH INDEX NAMES
        self.conn = pyodbc.connect(self.connection_string)
        self.cur = self.conn.cursor()

        for table in self.tables.keys():
            self.cur.execute('SHOW INDEXES FROM %s;' % table)
            index_names = list()

            for index in self.cur.fetchall():
                index_names.append(index[2])

            for index in index_names:
                if "idx_" in index:
                    self.cur.execute("DROP INDEX %s ON %s;" % (index, table))
        
        self.conn.commit()
        self.cur.close()
        self.conn.close()
        
        return True
    

    def analyze_tables(self):
        self.conn = pyodbc.connect(self.connection_string)
        self.cur = self.conn.cursor()
        for table in self.tables.keys():
            self.cur.execute('ANALYZE TABLE %s;' % table)
        self.conn.commit()
        self.cur.close()
        self.conn.close()
        print('Analyzed tables')


    def get_state_info(self):
        # Analyze tables
        self.analyze_tables()

        # Establish new connection
        self.conn = pyodbc.connect(self.connection_string)
        self.cur = self.conn.cursor()

        # Get queries EXPLAIN
        queries_cost = list()
        queries_explain = list()
        for query in self.queries:
            # Execute EXPLAIN command for query
            self.cur.execute("EXPLAIN FORMAT=JSON %s" % query)

            # Parse result
            result = self.cur.fetchall()
            result = str(result[0])
            result = result[2:-4]
            result = result.replace("\\n", "")
            result = result.replace("\\", "")
            query_explain = json.loads(result)

            # Append results
            queries_explain.append(query_explain)
            queries_cost.append(float(query_explain['query_block']['cost_info']['query_cost']))
        
        # Get indexes size
        # query_sizes = "SELECT table_name, round( data_length / ( 1024 *1024 ) , 2 ) AS 'data_length_mb', round( index_length / ( 1024 *1024 ) , 2 ) AS 'index_length_mb', round( round( data_length + index_length ) / ( 1024 *1024 ) , 2 ) AS 'total_size_mb' FROM information_schema.tables WHERE table_schema ='tpch' ORDER BY data_length DESC;"
        query_sizes = "SELECT * FROM information_schema.tables WHERE table_schema = 'tpch' ORDER BY data_length desc;"
        self.cur.execute(query_sizes)
        result = self.cur.fetchall()
        table_sizes = dict()
        for row in result:
            if row.TABLE_NAME in self.tables.keys():
                table_sizes[row.TABLE_NAME] = dict()
                table_sizes[row.TABLE_NAME]['table_rows'] = row.TABLE_ROWS
                table_sizes[row.TABLE_NAME]['avg_row_length'] = row.AVG_ROW_LENGTH
                table_sizes[row.TABLE_NAME]['data_length'] = row.DATA_LENGTH
                table_sizes[row.TABLE_NAME]['index_length'] = row.INDEX_LENGTH
                table_sizes[row.TABLE_NAME]['data_free'] = row.DATA_FREE

        # Close connection
        self.conn.commit()
        self.cur.close()
        self.conn.close()

        return queries_cost, queries_explain, table_sizes



if __name__ == "__main__":
    db = Database()

    if (db.reset_indexes()):
        print("YEAHH!")

    start = time.time()
    db.get_state_info()
    end = time.time()
    
    #print("Elapsed time:", end - start)
   # print(db.get_table_indexed_columns("lineitem"))

    # db.create_index('c_phone', 'customer')
    # db.create_index('l_commitdate', 'lineitem')
    # db.create_index('n_name', 'nation')
    # db.create_index('o_clerk', 'orders')
    # db.create_index('p_brand', 'part')
    # db.create_index('s_phone', 'supplier')
    # db.create_index('ps_availqty', 'partsupp')

    #db.create_index('o_orderdate', 'orders')

    # if (db.reset_indexes()):
    #     print("YEAHH!")

    indexes_map = db.get_indexes_map()

    pprint.pprint(indexes_map)