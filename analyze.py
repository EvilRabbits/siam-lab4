import sys
import vk_api
import networkx as nx
import matplotlib.pyplot as plt


def auth_handler():
    code = input("Введите код аутентификации: ")
    remember_me = False
    return code, remember_me


def get_friends(login, password, enable_two_factor):
    print("Получаем всех ваших друзей")

    add_me = True
    start_id = None

    if enable_two_factor:
        vk_session = vk_api.VkApi(login, password, auth_handler=auth_handler)
    else:
        vk_session = vk_api.VkApi(login, password)

    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as e:
        print(e)
        return

    api = vk_session.get_api()
    my_id = start_id if start_id else api.users.get()[0]["id"]
    friend = api.friends.get(user_id=my_id)["items"]

    if add_me:
        friend.append(my_id)

    friends, __errors = vk_api.vk_request_one_param_pool(
        vk_session,
        "friends.get",
        key="user_id",
        values=friend,
    )

    cleaned_friends = {}
    s = set(friend)
    for k, v in friends.items():
        t = list(s & set(v["items"]))
        if len(t) > 0 and len(t) < 20:
            cleaned_friends[k] = t

    print("Количесто друзей в сумме с вами: ", len(cleaned_friends))

    return cleaned_friends


def draw_friends_graph(friends):
    print("Рисуем граф")

    graph = nx.Graph(directed=False)

    for k, v in friends.items():
        graph.add_node(k)
        for i in v:
            graph.add_edge(k, i)

    pos = nx.spring_layout(graph)
    nx.draw(
        graph,
        pos,
        node_size=30,
        width=0.2,
    )

    plt.show()


def main():
    try:
        login = sys.argv[1]
        password = sys.argv[2]
        enable_two_factor = True if sys.argv[3] == "true" else False
    except:
        print("""
Неправильный запуск
    python analyze.py [логин] [пароль] [включить двухфакторку]
Пример запуска: python analyze.py +79666666666 superpassword false
              """)
        return

    draw_friends_graph(get_friends(login, password, enable_two_factor))


if __name__ == "__main__":
    main()
