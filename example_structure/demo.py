from dotenv import load_dotenv
import neo4j_db_connector as nc
import os
from nodes import *
from relations import *

if __name__ == '__main__':
    load_dotenv()
    conn = nc.Neo4jConnection(uri=os.getenv("URI"), user=os.getenv("USERNAME"), pwd=os.getenv("PASSWORD"))

    sc = Scenario(name='Авторизация по OTP')
    st0 = UserStep("Пользователь нажимает кнопку «Войти»", branch_type=BranchType.main)
    st1 = AppStep("Пользователю отображается экран ввода номера телефона", branch_type=BranchType.main)
    st2 = UserStep("Пользователь вводит номер телефона и нажимает кнопку «Далее»", branch_type=BranchType.main)
    st3 = AppStep("Пользователю отображается экран SMS-подтверждения", branch_type=BranchType.main)
    st4 = UserStep("Пользователь вводит код подтверждения и нажимает кнопку «Далее»", branch_type=BranchType.main)

    sc.db_merge_node(conn)
    st0.db_merge_node(conn)
    st1.db_merge_node(conn)
    st2.db_merge_node(conn)
    st3.db_merge_node(conn)
    st4.db_merge_node(conn)

    s_rel1 = Include(sc, st0)
    s_rel2 = Preceede(st0, st1)
    s_rel3 = Preceede(st1, st2)
    s_rel4 = Preceede(st2, st3)
    s_rel5 = Preceede(st3, st4)

    s_rel1.db_create_relation(conn)
    s_rel2.db_create_relation(conn)
    s_rel3.db_create_relation(conn)
    s_rel4.db_create_relation(conn)
    s_rel5.db_create_relation(conn)

    today_screen = Screen("Сегодня", event_name="today")
    mymagnit_screen = Screen("Мой Магнит", event_name="myMagnit")
    phone_screen = Screen("Ввод номера телефона", event_name="phoneEnter")
    sms_screen = Screen("Ввод SMS-подверждения", event_name="smsCode")

    today_screen.db_merge_node(conn)
    mymagnit_screen.db_merge_node(conn)
    phone_screen.db_merge_node(conn)
    sms_screen.db_merge_node(conn)

    next_button = Button("Далее", event_name="next")
    next_button.db_merge_node(conn)

    rel1 = BePerformedOn(st0, today_screen)
    rel2 = BePerformedOn(st0, mymagnit_screen)
    rel3 = BePerformedOn(st1, phone_screen)
    rel4 = BePerformedOn(st2, phone_screen)
    rel5 = BePerformedOn(st3, sms_screen)
    rel6 = BePerformedOn(st4, sms_screen)
    rel7 = InteractWith(st2, next_button)
    rel8 = InteractWith(st4, next_button)

    rel1.db_create_relation(conn)
    rel2.db_create_relation(conn)
    rel3.db_create_relation(conn)
    rel4.db_create_relation(conn)
    rel5.db_create_relation(conn)
    rel6.db_create_relation(conn)
    rel7.db_create_relation(conn)
    rel8.db_create_relation(conn)