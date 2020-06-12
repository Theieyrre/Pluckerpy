import json, sys
import termcolor as t

accounts = {}

count, tr_index, amb_index = 0, 0, 0
while True:
    account, tr_dict, amb_dict = {}, {}, {}
    try:
        main_name = input("Enter account screen name: ")
        name = input("Enter account name: ")
        account["screen_name"] = main_name
        account["name"] = name
        while True:
            follower = {}
            try:
                f_main_name = input("Enter follower screen name: ")
                follower["screen_name"] = f_main_name
                f_name = input("Enter account name: ")
                follower["name"] = f_name
                f_label = input("Enter label: ")
                follower["label"] = f_label
                f_list = input("Enter list name:(TR/AMB) ")
                if f_list == "TR":
                    tr_dict[tr_index] = follower
                    tr_index += 1
                else:
                    amb_dict[amb_index] = follower
                    amb_index += 1
            except KeyboardInterrupt:
                print(t.colored("Followers complete !", "yellow"))
                account["tr_followers"] = tr_dict
                account["amb_followers"] = amb_dict
                break
        accounts[count] = account
        count += 1
    except KeyboardInterrupt:
        print(t.colored("Accounts complete !", "yellow"))
        output = open("turkish.json", "w")
        json.dump(accounts, output, indent=4)
        sys.exit(t.colored("Data saved in turkish.json", "green"))

