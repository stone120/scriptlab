#!/bin/bash
#
if [ ! $# -ge 1 ];then
 echo -e "脚本使用方法:\033[1;32msh $0 role_id_1 role_id_2 ...\033[0m"
 exit 1
fi
 
###############定义变量###############
red="\033[5;31m"
red1="\033[1;31m"
green="\033[1;32m"
close="\033[0m"
date=`date +%Y%m%d`
db="storage"
datapath="/root/dol_db_update"
 
###############定义函数###############
move() {
 if [ -d $datapath/$date ];then
   echo -e "$green[$date]目录已经存在!$close"
   mv $datapath/$1 $datapath/$date &> /dev/null
   if [ $? = 0 ];then
     echo -e "$green[$1]文件移动到[$date]目录成功!$close"
   else
     if [ -e $datapath/$date/$1 ];then
     echo -e "$red[$1]$close已存在于$red[$date]$close目录中!"
     else
     echo -e "移动$red[$1]$close文件到$red[$date]$close目录失败，原因自行查看!"
     fi
   fi
 else
   cd $datapath
   mkdir $date
   echo -e "$green[$date]目录创建成功!$close"
   mv $datapath/$1 $datapath/$date &> /dev/null
   if [ $? = 0 ];then
     echo -e "$green[$1]文件移动到[$date]目录成功!$close"
   else
     if [ -e $datapath/$date/$1 ];then
     echo -e "$red[$1]$close已存在于$red[$date]$close目录中!"
     else
     echo -e "移动$red[$1]$close文件到$red[$date]$close目录失败，原因自行查看!"
     fi
   fi
 fi
}
 
del() {
 cd $datapath
 if [ -n $roleid ];then
   ./dol_db_update CHARA_DEL $roleid &> /dev/null
   echo -e "$green删除角色[$roleid]成功,自动重新恢复[$1]角色,请等待!$close"
   restore $replace $replace1
 else
   echo -e "$red1删除角色[$roleid]失败,请检查你输入的角色ID是否正确!$close"
   echo -e "$red1角色恢复到[$1]终止,请重新运行脚本并输入需要恢复的角色ID号!$close"
   exit 1
 fi
}
 
restore() {
 cd $datapath
 ./dol_db_update NECRO $1 > $1
 grep "SUCCESS" $1 &> /dev/null
 if [ $? = 0 ];then
   echo -e "$green[$1]恢复成功$close!"
   mysql -e "SELECT id,name,account_id,created,last_save,lv_adv,lv_trd,lv_btl FROM $db.dol_chara_store WHERE id=$1;"
   move $replace
   echo -e "$green<<<===============================================角色ID[$1]恢复成功=================================================>>>$close"
 else
   echo -e "$red1[$1]恢复失败,失败原因如下!$close"
   grep "UNIQUE" $1 &> /dev/null
   if [ $? = 0 ];then
     echo -e "$red[$1]$close的角色名有重复,需要删除重复角色名才可以恢复$red[$1]$close,[$!]角色名如下:"
     mysql -e "SELECT id,name,account_id FROM $db.dol_chara_graveyard WHERE id=$1;"
     echo -e "$green重复角色如下,查询需要一点时间,请耐心等待......$close"
     ACC1=`mysql -N -s -e "select id from $db.dol_chara_store where name='$rolename';"`
     mysql -e "select id,name,account_id,created,last_save,lv_adv,lv_trd,lv_btl from $db.dol_chara_store where name='$rolename';"
     if [ -n "$ACC1" ];then
     read -p "输入需要删除的角色ID[$ACC1],你也可以输入[q|Q]退出脚本:" roleid
     case $roleid in
     q|Q)
       echo -e "$green角色恢复到[$1]结束,请重新运行脚本并输入需要恢复的角色ID号!$close"
       exit 1
       ;;
     $ACC1)
       del $replace
       ;;
     *)
       read -p "输入的角色ID有误,请重新输入:" roleid
     esac
     fi
   else
     grep "slot_full" $1 &> /dev/null
     if [ $? = 0 ]; then
     echo -e "$red[$1]$close的账号下角色以满,需要删除一个角色后才可恢复$red[$1]$close!"
     mysql -e "SELECT id,name,account_id FROM $db.dol_chara_graveyard WHERE id=$1;"
     echo -e "$green[$1]账号角色如下,查询需要一点时间,请耐心等待:$close"
     ACC2=`mysql -N -s -e "select id from $db.dol_chara_store where account_id=$account_id;"`
     ACC3=$(echo $ACC2 | awk '{print $1}')
     ACC4=$(echo $ACC2 | awk '{print $2}')
     ACC5=$(echo $ACC2 | awk '{print $3}')
     mysql -e "select id,name,account_id,created,last_save,lv_adv,lv_trd,lv_btl from $db.dol_chara_store where account_id=$account_id;"
     if [ -n "$ACC5" ];then
     if [ -n "$ACC4" ];then
       read -p "从上面显示的角色中选择一个角色ID进行删除[$ACC3 $ACC4 $ACC5],你也可以输入[q|Q]退出脚本或敲回车继续恢复下一个ID[$2]:" roleid
       case $roleid in
       q|Q)
         echo -e "$green角色恢复到[$1]结束,请重新运行脚本并输入需要恢复的角色ID号!$close"
         exit 1
         ;;
       $ACC3|$ACC4|$ACC5)
         del $replace
         ;;
       *)
         echo -e "$red1输入的角色ID不是给定的ID号[$ACC3 $ACC4 $ACC5],所以角色删除失败,因此[$1]恢复失败,继续恢复下一个角色[$replace1]!$close"
       esac
     else
       read -p "系统检测到info表中数据未导入到store表中,是否执行导入操作[y/n]:" yn
       case $yn in
       y|Y)
         echo "正在执行info表中数据导入到store表中,请等待....."
         mysql -u root storage < /usr/local/etc/koei/chara_tbl_mng.sql &> /dev/null
         restore $replace $replace1
         ;;
       n|N)
         echo -e "$green由于不执行info表中数据导入到store表中,因此程序被迫中断,必须进行导入操作才可恢复角色或者跳过此角色重新运行角色!$close"
         exit 1
         ;;
       *)
         echo -e "$green由于不执行info表中数据导入到store表中,因此程序被迫中断,必须进行导入操作才可恢复角色或者跳过此角色重新运行角色!$close"
         exit 1
       esac
     fi
     else
     if [ -n "$ACC4" ];then
       read -p "从上面显示的角色中选择一个角色ID进行删除[$ACC3 $ACC4],你也可以输入[q|Q]退出脚本或敲回车继续恢复下一个ID[$2]:" roleid
       case $roleid in
       q|Q)
         echo -e "$green角色恢复到[$1]结束,请重新运行脚本并输入需要恢复的角色ID号!$close"
         exit 1
         ;;
       $ACC3|$ACC4)
         del $replace
         ;;
       *)
         echo -e "$red1输入的角色ID不是给定的ID号[$ACC3 $ACC4],所以角色删除失败,因此[$1]恢复失败,继续恢复下一个角色[$replace1]!$close"
       esac
     else
       read -p "系统检测到info表中数据未导入到store表中,是否执行导入操作[y/n]:" yn
       case $yn in
       y|Y)
         echo "正在执行info表中数据导入到store表中,请等待....."
         mysql -u root storage < /usr/local/etc/koei/chara_tbl_mng.sql &> /dev/null
         restore $replace $replace1
         ;;
       n|N)
         echo -e "$green由于不执行info表中数据导入到store表中,因此程序被迫中断,必须进行导入操作才可恢复角色或者跳过此角色重新运行角色!$close"
         exit 1
         ;;
       *)
         echo -e "$green由于不执行info表中数据导入到store表中,因此程序被迫中断,必须进行导入操作才可恢复角色或者跳过此角色重新运行角色!$close"
         exit 1
       esac
     fi
     fi
   else  
     echo "$red1恢复角色ID[$1]出现故障,请根据错误日志信息逐一排查解决!$close,继续恢复下一个[$replace1]"
     cat $datapath/$1
   fi
   fi
 fi
}
 
###############检查输入合法性###############
LIST=$@
for i in $LIST;do
 test=$(echo $i | sed 's/[0-9]//g')
 if [ ! -z $test ];then
   echo -e "$green对不起,你输入的角色ID有误,只能输入数字且数字字符个数不得大于10,请重新输入!$close"
   exit 1
 else
   count=`echo ${#i}`
   if [ $count -gt 10 ];then
   echo -e "$green对不起,你输入的角色ID有误,只能输入数字且数字字符个数不得大于10,请重新输入!$close"
   exit 1
   fi
 fi
done
 
################业务逻辑###################
for((i=0;$#>i;));do
account_id=`mysql -N -s -e "SELECT account_id FROM $db.dol_chara_graveyard WHERE id=$1;"`
rolename=`mysql -N -s -e "SELECT name FROM $db.dol_chara_graveyard WHERE id=$1;"`
role_id=`mysql -N -s -e "SELECT id FROM $db.dol_chara_store WHERE id=$1;"`
replace="$1"
replace1="$2"
if [ -s $account_id ]; then
 echo -e "$green没有查询到被删除角色ID[$1]!$close"
 if [ -n "$role_id" ];then
   echo -e "$green[$1]角色存在于dol_chara_store表中,表示此角色并没有被删除或已经恢复!$close"
 else
   echo -e "$green并且此角色ID[$1]不存在于dol_chara_store表中,由以上两个条件判断出,你输入的角色ID[$1]很有可能是一个错误的角色ID号,请检查后再次输>入...$close"
 fi
else
 restore $replace $replace1
fi
shift 1
done
echo -e "\n"
echo -e "$green<<<======================================时间[$date]共恢复角色如下==========================================>>>$close"
cat $datapath/$date/*
echo -e "$green<<<==================================================结束======================================================>>>$close"
echo -e "\n"