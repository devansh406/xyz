#include <SDL3/SDL.h>
#include <SDL3_ttf/SDL_ttf.h>
#include <stdbool.h>
#include <stdio.h>

#define SCREEN_WIDTH 800
#define SCREEN_HEIGHT 600
#define PADDLE_WIDTH 20
#define PADDLE_HEIGHT 100
#define BALL_SIZE 15
#define WIN_SCORE 5

// Helper: render text
void renderText(SDL_Renderer* renderer, TTF_Font* font, const char* text, int x, int y, SDL_Color color) {
    SDL_Surface* surface = TTF_RenderText_Solid(font, text, color);
    SDL_Texture* texture = SDL_CreateTextureFromSurface(renderer, surface);
    SDL_Rect dst = {x, y, surface->w, surface->h};
    SDL_RenderTexture(renderer, texture, NULL, &dst);
    SDL_DestroySurface(surface);
    SDL_DestroyTexture(texture);
}

int main() {
    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        SDL_Log("SDL could not initialize! SDL_Error: %s", SDL_GetError());
        return 1;
    }

    if (TTF_Init() == -1) {
        SDL_Log("SDL_ttf could not initialize! TTF_Error: %s", TTF_GetError());
        return 1;
    }

    SDL_Window* window = SDL_CreateWindow("Pong 🎮", SCREEN_WIDTH, SCREEN_HEIGHT, SDL_WINDOW_RESIZABLE);
    SDL_Renderer* renderer = SDL_CreateRenderer(window, NULL);

    // Load font
    TTF_Font* font = TTF_OpenFont("arial.ttf", 28);
    if (!font) {
        SDL_Log("Failed to load font: %s", TTF_GetError());
        SDL_Quit();
        return 1;
    }

    SDL_FRect player1 = {50, SCREEN_HEIGHT / 2 - PADDLE_HEIGHT / 2, PADDLE_WIDTH, PADDLE_HEIGHT};
    SDL_FRect player2 = {SCREEN_WIDTH - 70, SCREEN_HEIGHT / 2 - PADDLE_HEIGHT / 2, PADDLE_WIDTH, PADDLE_HEIGHT};
    SDL_FRect ball = {SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, BALL_SIZE, BALL_SIZE};

    float ballVelX = 4, ballVelY = 4;
    float paddleSpeed = 400.0f;
    float ballSpeed = 400.0f;
    int score1 = 0, score2 = 0;
    bool running = true, paused = false, gameOver = false;
    Uint64 now = SDL_GetTicks(), last = now;
    float delta = 0.0f;
    SDL_Event event;
    float scorePopupTimer = 0;
    int lastScoredPlayer = 0;

    while (running) {
        last = now;
        now = SDL_GetTicks();
        delta = (now - last) / 1000.0f;

        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_EVENT_QUIT)
                running = false;
            else if (event.type == SDL_EVENT_KEY_DOWN) {
                if (event.key.keysym.sym == SDLK_p)
                    paused = !paused;
                if (event.key.keysym.sym == SDLK_r) {
                    // Restart
                    score1 = score2 = 0;
                    gameOver = false;
                    ball.x = SCREEN_WIDTH / 2;
                    ball.y = SCREEN_HEIGHT / 2;
                    ballVelX = 4;
                    ballVelY = 4;
                    ballSpeed = 400.0f;
                }
            }
        }

        if (!paused && !gameOver) {
            const Uint8* keys = SDL_GetKeyboardState(NULL);
            if (keys[SDL_SCANCODE_W] && player1.y > 0)
                player1.y -= paddleSpeed * delta;
            if (keys[SDL_SCANCODE_S] && player1.y < SCREEN_HEIGHT - PADDLE_HEIGHT)
                player1.y += paddleSpeed * delta;

            if (keys[SDL_SCANCODE_UP] && player2.y > 0)
                player2.y -= paddleSpeed * delta;
            if (keys[SDL_SCANCODE_DOWN] && player2.y < SCREEN_HEIGHT - PADDLE_HEIGHT)
                player2.y += paddleSpeed * delta;

            ball.x += ballVelX * delta * (ballSpeed / 4);
            ball.y += ballVelY * delta * (ballSpeed / 4);

            if (ball.y <= 0 || ball.y + BALL_SIZE >= SCREEN_HEIGHT)
                ballVelY = -ballVelY;

            if (SDL_HasRectIntersectionFloat(&ball, &player1)) {
                ballVelX = fabs(ballVelX);
                ballSpeed += 50;
            }
            if (SDL_HasRectIntersectionFloat(&ball, &player2)) {
                ballVelX = -fabs(ballVelX);
                ballSpeed += 50;
            }

            if (ball.x <= 0) {
                score2++;
                lastScoredPlayer = 2;
                scorePopupTimer = 1.0f;
                ball.x = SCREEN_WIDTH / 2;
                ball.y = SCREEN_HEIGHT / 2;
                ballVelX = fabs(ballVelX);
                ballSpeed = 400.0f;
            } else if (ball.x + BALL_SIZE >= SCREEN_WIDTH) {
                score1++;
                lastScoredPlayer = 1;
                scorePopupTimer = 1.0f;
                ball.x = SCREEN_WIDTH / 2;
                ball.y = SCREEN_HEIGHT / 2;
                ballVelX = -fabs(ballVelX);
                ballSpeed = 400.0f;
            }

            if (score1 >= WIN_SCORE || score2 >= WIN_SCORE)
                gameOver = true;

            if (scorePopupTimer > 0)
                scorePopupTimer -= delta;
        }

        // 🎨 Rendering
        SDL_SetRenderDrawColor(renderer, 20, 25, 45, 255);
        SDL_RenderClear(renderer);

        SDL_SetRenderDrawColor(renderer, 80, 80, 120, 255);
        SDL_FRect mid = {SCREEN_WIDTH / 2 - 2, 0, 4, SCREEN_HEIGHT};
        SDL_RenderFillRect(renderer, &mid);

        SDL_SetRenderDrawColor(renderer, 255, 180, 80, 255);
        SDL_RenderFillRect(renderer, &player1);
        SDL_SetRenderDrawColor(renderer, 100, 200, 255, 255);
        SDL_RenderFillRect(renderer, &player2);
        SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);
        SDL_RenderFillRect(renderer, &ball);

        // 🧮 Scoreboard
        SDL_Color white = {255, 255, 255, 255};
        char scoreText1[10], scoreText2[10];
        sprintf(scoreText1, "%d", score1);
        sprintf(scoreText2, "%d", score2);
        renderText(renderer, font, scoreText1, SCREEN_WIDTH / 4, 30, white);
        renderText(renderer, font, scoreText2, SCREEN_WIDTH * 3 / 4, 30, white);

        // ✨ Score popup
        if (scorePopupTimer > 0) {
            SDL_Color popupColor = lastScoredPlayer == 1 ? (SDL_Color){255, 180, 80, 255}
                                                         : (SDL_Color){100, 200, 255, 255};
            renderText(renderer, font,
                       lastScoredPlayer == 1 ? "PLAYER 1 +1" : "PLAYER 2 +1",
                       SCREEN_WIDTH / 2 - 90, SCREEN_HEIGHT / 2 - 20, popupColor);
        }

        // 🏁 Winner message
        if (gameOver) {
            SDL_Color green = {0, 255, 120, 255};
            const char* winMsg = score1 > score2 ? "PLAYER 1 WINS!" : "PLAYER 2 WINS!";
            renderText(renderer, font, winMsg, SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT / 2 - 30, green);
            renderText(renderer, font, "Press R to Restart", SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT / 2 + 20, white);
        }

        // ⏸ Paused text
        if (paused && !gameOver) {
            SDL_Color yellow = {255, 255, 100, 255};
            renderText(renderer, font, "PAUSED", SCREEN_WIDTH / 2 - 60, SCREEN_HEIGHT / 2 - 20, yellow);
        }

        SDL_RenderPresent(renderer);
    }

    TTF_CloseFont(font);
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    TTF_Quit();
    SDL_Quit();
    return 0;
}
