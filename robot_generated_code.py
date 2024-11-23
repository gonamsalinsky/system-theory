import turtle


def perform_switch_case(state, t, turn):
    x = round(t.position()[0] / 10)
    y = round(t.position()[1] / 10)
    num_turns = 5

    if state == "INIT":
        if True:
            state = "UP"
            t.setheading(90)  # Поворот в сторону движения вперед
            return state, turn
    if state == "RIGHT":
        if x >= turn:
            state = "DOWN"
            t.setheading(270)  # Поворот в сторону движения назад
            return state, turn
        if x < turn:
            state = "RIGHT"
            t.forward(10)  # Перемещение
            return state, turn
    if state == "DOWN":
        if y <= -turn:
            state = "LEFT"
            t.setheading(180)  # Поворот в сторону движения влево
            return state, turn
        if y > -turn:
            state = "DOWN"
            t.forward(10)  # Перемещение
            return state, turn
    if state == "LEFT":
        if x <= -turn:
            state = "UP"
            turn += 1  # Начало следующего витка
            t.setheading(90)  # Поворот в сторону движения вперед
            return state, turn
        if x > -turn:
            state = "LEFT"
            t.forward(10)  # Перемещение
            return state, turn
    if state == "UP":
        if turn > num_turns:
            state = "STOP"
            return state, turn
        if y >= turn:
            state = "RIGHT"
            t.setheading(0)  # Поворот в сторону движения вправо
            return state, turn
        if y < turn:
            state = "UP"
            t.forward(10)  # Перемещение
            return state, turn


def draw():
    start_state = "INIT"
    end_state = "STOP"
    curr_state = start_state
    t = turtle.Turtle()
    turn = 1

    while curr_state != end_state:
        curr_state, turn = perform_switch_case(curr_state, t, turn)
    turtle.done()


if  __name__ == "__main__":
    draw()