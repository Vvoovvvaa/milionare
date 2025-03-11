import random
import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Кто хочет стать миллионером?")

font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

current_question = 0
score = 0
disabled_buttons = []
fifty_fifty_used = False
call_used = False
friend_advice = ""

def load_questions():
    questions = []
    with open("questions.txt", "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(";")
            if len(parts) == 5:
                correct_answer = parts[1]
                options = parts[1:5]
                random.shuffle(options)
                questions.append({"question": parts[0], "options": options, "answer": correct_answer})
    random.shuffle(questions)
    return questions

highscores_file = "highscores.txt"

def save_leaderboard(name, score):
    with open(highscores_file, "a", encoding="utf-8") as f:
        f.write(f"{name}: {score}\n")

def show_leaderboard():
    screen.fill((0, 0, 0))
    draw_text("Таблица лидеров:", 200, 100)
    y_offset = 150
    with open(highscores_file, "r", encoding="utf-8") as f:
        for line in f.readlines():
            draw_text(line.strip(), 200, y_offset)
            y_offset += 30
    pygame.display.flip()
    pygame.time.delay(5000)

def draw_text(text, x, y, color=(255, 255, 255)):
    rendered_text = font.render(text, True, color)
    screen.blit(rendered_text, (x, y))

def draw_buttons(options, disabled_buttons):
    buttons = []
    for i, option in enumerate(options):
        rect = pygame.Rect(200, 250 + i * 50, 400, 40)
        buttons.append((rect, option))
        color = (0, 128, 255) if option not in disabled_buttons else (128, 128, 128)
        pygame.draw.rect(screen, color, rect)
        draw_text(option, rect.x + 10, rect.y + 10)
    return buttons

def apply_fifty_fifty(questions, current_question, disabled_buttons):
    global fifty_fifty_used
    if fifty_fifty_used:
        return
    question = questions[current_question]
    correct = question["answer"]
    incorrect_options = [opt for opt in question["options"] if opt != correct]
    removed = random.sample(incorrect_options, 2)
    disabled_buttons.extend(removed)
    fifty_fifty_used = True

def call_friend(questions, current_question):
    global call_used, friend_advice
    if call_used:
        return
    question = questions[current_question]
    correct = question["answer"]
    options = question["options"]
    if random.random() < 0.7:
        suggested = correct
    else:
        suggested = random.choice([opt for opt in options if opt != correct])
    friend_advice = f"Друг советует: {suggested}"
    call_used = True

def get_player_name():
    input_active = True
    user_text = ""
    input_box = pygame.Rect(200, 250, 400, 40)
    color_active = pygame.Color('dodgerblue2')
    color_inactive = pygame.Color('lightskyblue3')
    color = color_inactive
    active = False

    while input_active:
        screen.fill((0, 0, 0))
        draw_text("Введите ваше имя:", 200, 200)
        pygame.draw.rect(screen, color, input_box, 2)
        text_surface = font.render(user_text, True, (255, 255, 255))
        screen.blit(text_surface, (input_box.x + 10, input_box.y + 10))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN and user_text:
                        return user_text
                    elif event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        user_text += event.unicode

def show_win_screen():
    screen.fill((0, 255, 0))
    draw_text("Поздравляем, вы выиграли!", 200, 250, (255, 255, 0))
    draw_text("Нажмите любую клавишу для выхода", 200, 300, (255, 255, 0))
    pygame.display.flip()
    wait_for_keypress()

def wait_for_keypress():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

def game_loop():
    global current_question, player_name, score, friend_advice, fifty_fifty_used, call_used,disabled_buttons
    while current_question < len(questions):
        screen.fill((0, 0, 0))
        question = questions[current_question]
        draw_text(question["question"], 200, 150)
        draw_text(f"Очки: {score}", 600, 50)
        buttons = draw_buttons(question["options"], disabled_buttons)

        pygame.draw.rect(screen, (255, 0, 0), (50, 500, 100, 40))
        draw_text("50:50", 60, 510)
        pygame.draw.rect(screen, (0, 255, 0), (200, 500, 150, 40))
        draw_text("Звонок", 210, 510)

        if friend_advice:
            draw_text(friend_advice, 200, 550, color=(255, 255, 0))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 50 <= x <= 150 and 500 <= y <= 540:
                    apply_fifty_fifty(questions, current_question, disabled_buttons)
                if 200 <= x <= 350 and 500 <= y <= 540:
                    call_friend(questions, current_question)
                for rect, option in buttons:
                    if rect.collidepoint(event.pos) and option not in disabled_buttons:
                        if option == question["answer"]:
                            score = score * 2 if score else 100
                            current_question += 1
                            friend_advice = ""
                            call_used = False
                        else:
                            save_leaderboard(player_name, score)
                            show_leaderboard()
                            pygame.quit()
                            sys.exit()

        clock.tick(30)

if __name__=="__main__":
    questions = load_questions()
    player_name = get_player_name()
    game_loop()
    show_win_screen()
    save_leaderboard(player_name, score)
    show_leaderboard()
