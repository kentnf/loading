
# mongodb command
sudo service mongod start|stop|restart|status

mongo 		-- open mongo shell and connect to mongodb in localhost
exit		-- exit mongo shell and disconnect to mongodb

show dbs			-- show databases
use dbname			-- connect to database
show collections	-- just show collections

db.createCollection(name);
db.collectionname.drop();

use dbname;			-- and
db.dropDatabase();	-- the two command will drop the database

db.collectionname.find();	-- search all document in collectionname

# pymongo usage
from pymongo import * # 导包
con = Connection(...) # 链接
db = con.database # 链接数据库
db.authenticate('username', 'password') # 登录
db.drop_collection('users') #删除表
db.logout() # 退出
db.collection_names() # 查看所有表
db.users.count() # 查询数量
db.users.find_one({'name' : 'xiaoming'}) # 单个对象
db.users.find({'age' : 18}) # 所有对象
db.users.find({'id':64}, {'age':1,'_id':0}) # 返回一些字段 默认_id总是返回的 0不返回 1返回
db.users.find({}).sort({'age': 1}) # 排序
db.users.find({}).skip(2).limit(5) # 切片


