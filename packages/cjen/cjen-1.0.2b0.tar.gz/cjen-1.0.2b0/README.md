<!--
 * @Author: your name
 * @Date: 2022-02-05 00:15:52
 * @LastEditTime: 2022-02-22 18:40:31
 * @LastEditors: your name
 * @Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 * @FilePath: \PyPackage\cjen\README.md
-->

该项目封装了测试人员写自动化代码的常用功能作为装饰器，
目标是能让测试人员更关注业务逻辑的实现，隐藏和业务逻辑无关的细节。
GitHub地址：https://github.com/thcpc/cjen

# Release 1.0.1
get_mapping, put_mapping, post_mapping, delete_mapping, upload_mapping 增加json_clazz参数，作用同operate.json.factory

# Release 1.0.2
- 1. 修改metaMysql 没有数据时，是警告信息而不是错误信息

- 2. 方便批量检查，增加了 context["cursor"]

# Release 1.0.2b
- 1. 修改了创建metaMysql后，直接释放数据库连接池（临时修改方案）
