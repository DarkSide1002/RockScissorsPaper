import random
import cv2
import mediapipe as mp

scissors_image = cv2.imread("images/Scissors.png")
paper_image = cv2.imread("images/Paper.png")
rock_image = cv2.imread("images/img.png")

p = [0 for i in range(21)]  # создаем массив из 21 ячейки для хранения высоты каждой точки
finger = [0 for i in range(5)]

# Подключаем камеру
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Width
cap.set(4, 720)  # Lenght

new_height = 200
new_width = 200

delay = 0
check = True
res = False
screen_img = None
screen_img2 = None

mpHands = mp.solutions.hands
hands = mpHands.Hands(False)
npDraw = mp.solutions.drawing_utils

gestures = ["Rock", "Scissors", "Paper"]
results_of_play = ["Draw", "Computer Won", "You Won"]


def distance(point1, point2):
    return abs(point1 - point2)


def get_gesture():
    return random.choice(gestures)


def check_hand(handLms):
    for id, point in enumerate(handLms.landmark):
        # получаем размеры изображения с камеры и масштабируем
        width, height, color = img.shape
        width, height = int(point.x * height), int(point.y * width)

        p[id] = height  # заполняем массив высотой каждой точки

    # получаем расстояние, с которым будем сравнивать каждый палец
    distanceGood = distance(p[0], p[5]) + (distance(p[0], p[5]) / 2)
    # заполняем массив 1 (палец поднят) или 0 (палец сжат)
    finger[1] = 1 if distance(p[0], p[8]) > distanceGood else 0
    finger[2] = 1 if distance(p[0], p[12]) > distanceGood else 0
    finger[3] = 1 if distance(p[0], p[16]) > distanceGood else 0
    finger[4] = 1 if distance(p[0], p[20]) > distanceGood else 0
    finger[0] = 1 if distance(p[4], p[17]) > distanceGood else 0

    # готовим сообщение для отправки
    # 0 - большой палец, 1 - указательный, 2 - средний, 3 - безымянный, 4 - мизинец
    if not (finger[0]) and finger[1] and (finger[2]) and not (finger[3]) and not finger[4]:
        msg = 'Scissors'
    elif not (finger[0]) and not finger[1] and not finger[2] and not (finger[3]) and not (finger[4]):
        msg = 'Rock'
    else:
        msg = 'Paper'

    computer_choice = get_gesture()
    result = results_of_play[gestures.index(msg) - gestures.index(computer_choice)]
    npDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
    return result, computer_choice, msg


# Зацикливаем получение кадров от камеры
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)  # Mirror flip

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            if delay > 25:
                if check:
                    res, screen_img, screen_img2 = check_hand(handLms)
                    if screen_img == "Paper":
                        screen_img = paper_image
                    elif screen_img == "Scissors":
                        screen_img = scissors_image
                    else:
                        screen_img = rock_image
                    if screen_img2 == "Paper":
                        screen_img2 = paper_image
                    elif screen_img2 == "Scissors":
                        screen_img2 = scissors_image
                    else:
                        screen_img2 = rock_image

                    check = False
            else:
                delay += 1
        npDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    if res:
        if res == "You Won":
            cv2.putText(img, res, (450, 360), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), 12, cv2.LINE_AA)
        elif res == "Draw":
            cv2.putText(img, res, (500, 360), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), 12, cv2.LINE_AA)
        else:
            cv2.putText(img, res, (300, 360), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), 12, cv2.LINE_AA)

    if screen_img is not None and screen_img2 is not None:
        screen_img_new = cv2.resize(screen_img, (new_width, new_height))
        screen_img2_new = cv2.resize(screen_img2, (new_width, new_height))
        cv2.putText(img, "You picked", (890, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(img, "Computer picked", (220, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        img[0:new_height, -new_width:] = screen_img2_new
        img[0:new_height, 0:new_width] = screen_img_new
        cv2.putText(img, 'Press "R" to restart GAME', (200, 620), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5,
                    cv2.LINE_AA)

    cv2.imshow('python', img)

    if cv2.waitKey(1) == ord("r"):
        delay = 0
        check = True
        res = False
        screen_img = None

    if cv2.waitKey(20) == 27:  # exit on ESC
        break

cv2.destroyWindow("python")
cap.release()
cv2.waitKey(1)
