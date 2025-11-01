#include <SDL3/SDL.h>
#include <stdbool.h>
#include <stdio.h>

#define SCREEN_WIDTH 800
#define SCREEN_HEIGHT 600
#define PADDLE_WIDTH 20
#define PADDLE_HEIGHT 100
#define BALL_SIZE 15
#define WIN_SCORE 5

int main() {
    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        SDL_Log("SDL could not initialize! SDL_Error: %s", SDL_GetError());
        return 1;
    }

    SDL_Window* window = SDL_CreateWindow("Pong 🎮", SCREEN_WIDTH, SCREEN_HEIGHT, SDL_WINDOW_RESIZABLE);
    if (!window) {
        SDL_Log("Window could not be created! SDL_Error: %s", SDL_GetError());
        SDL_Quit();
        return 1;
    }

    SDL_Renderer* renderer = SDL_CreateRenderer(window, NULL);
    if (!renderer) {
        SDL_Log("Renderer could not be created! SDL_Error: %s", SDL_GetError());
        SDL_DestroyWindow(window);
        SDL_Quit();
        return 1;
    }

    SDL_FRect player1 = {50, SCREEN_HEIGHT / 2 - PADDLE_HEIGHT / 2, PADDLE_WIDTH, PADDLE_HEIGHT};
    SDL_FRect player2 = {SCREEN_WIDTH - 70, SCREEN_HEIGHT / 2 - PADDLE_HEIGHT / 2, PADDLE_WIDTH, PADDLE_HEIGHT};
    SDL_FRect ball = {SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, BALL_SIZE, BALL_SIZE};

    float ballVelX = 4, ballVelY = 4;
    float paddleSpeed = 400.0f; // pixels per second
    float ballSpeed = 400.0f;
    int score1 = 0, score2 = 0;
    bool running = true;
    bool paused = false;
    bool gameOver = false;
    Uint64 now = SDL_GetTicks();
    Uint64 last = now;
    float delta = 0.0f;
    SDL_Event event;

    float scorePopupTimer = 0;
    int lastScoredPlayer = 0; // 1 or 2

    while (running) {
        last = now;
        now = SDL_GetTicks();
        delta = (now - last) / 1000.0f; // seconds since last frame

        // 🎮 Event handling
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_EVENT_QUIT)
                running = false;
            else if (event.type == SDL_EVENT_KEY_DOWN) {
                if (event.key.keysym.sym == SDLK_p)
                    paused = !paused;
                if (event.key.keysym.sym == SDLK_r) {
                    // restart game
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

        if (paused || gameOver) {
            // only render static screen
        } else {
            const Uint8* keys = SDL_GetKeyboardState(NULL);

            // 🕹 Player 1 (W/S)
            if (keys[SDL_SCANCODE_W] && player1.y > 0)
                player1.y -= paddleSpeed * delta;
            if (keys[SDL_SCANCODE_S] && player1.y < SCREEN_HEIGHT - PADDLE_HEIGHT)
                player1.y += paddleSpeed * delta;

            // 🕹 Player 2 (Arrow keys)
            if (keys[SDL_SCANCODE_UP] && player2.y > 0)
                player2.y -= paddleSpeed * delta;
            if (keys[SDL_SCANCODE_DOWN] && player2.y < SCREEN_HEIGHT - PADDLE_HEIGHT)
                player2.y += paddleSpeed * delta;

            // 🏐 Move ball
            ball.x += ballVelX * delta * (ballSpeed / 4);
            ball.y += ballVelY * delta * (ballSpeed / 4);

            // Bounce off top/bottom
            if (ball.y <= 0 || ball.y + BALL_SIZE >= SCREEN_HEIGHT)
                ballVelY = -ballVelY;

            // Player 1 paddle collision
            if (SDL_HasRectIntersectionFloat(&ball, &player1)) {
                ballVelX = fabs(ballVelX);
                ballSpeed += 50; // speed increase
            }

            // Player 2 paddle collision
            if (SDL_HasRectIntersectionFloat(&ball, &player2)) {
                ballVelX = -fabs(ballVelX);
                ballSpeed += 50; // speed increase
            }

            // 🎯 Scoring
            if (ball.x <= 0) {
                score2++;
                lastScoredPlayer = 2;
                scorePopupTimer = 1.0f; // show for 1 sec
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

            // 🏆 Check win
            if (score1 >= WIN_SCORE || score2 >= WIN_SCORE) {
                gameOver = true;
            }

            if (scorePopupTimer > 0)
                scorePopupTimer -= delta;
        }

        // 🎨 RENDER SECTION
        SDL_SetRenderDrawColor(renderer, 20, 25, 45, 255);
        SDL_RenderClear(renderer);

        // Middle line
        SDL_SetRenderDrawColor(renderer, 80, 80, 120, 255);
        SDL_FRect mid = {SCREEN_WIDTH / 2 - 2, 0, 4, SCREEN_HEIGHT};
        SDL_RenderFillRect(renderer, &mid);

        // Player paddles
        SDL_SetRenderDrawColor(renderer, 255, 180, 80, 255);
        SDL_RenderFillRect(renderer, &player1);
        SDL_SetRenderDrawColor(renderer, 100, 200, 255, 255);
        SDL_RenderFillRect(renderer, &player2);

        // Ball
        SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);
        SDL_RenderFillRect(renderer, &ball);

        // Score indicators
        SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);
        for (int i = 0; i < score1; i++) {
            SDL_FRect dot = {SCREEN_WIDTH / 4 - i * 20, 20, 10, 10};
            SDL_RenderFillRect(renderer, &dot);
        }
        for (int i = 0; i < score2; i++) {
            SDL_FRect dot = {SCREEN_WIDTH * 3 / 4 + i * 20, 20, 10, 10};
            SDL_RenderFillRect(renderer, &dot);
        }

        // ✨ Score popup
        if (scorePopupTimer > 0) {
            SDL_SetRenderDrawColor(renderer,
                lastScoredPlayer == 1 ? 255 : 100,
                lastScoredPlayer == 2 ? 255 : 100,
                100, 255);
            SDL_FRect popup = {SCREEN_WIDTH / 2 - 40, SCREEN_HEIGHT / 2 - 40, 80, 80};
            SDL_RenderFillRect(renderer, &popup);
        }

        // 🏁 Winner message
        if (gameOver) {
            SDL_SetRenderDrawColor(renderer, 0, 255, 100, 180);
            SDL_FRect winBox = {SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT / 2 - 40, 300, 80};
            SDL_RenderFillRect(renderer, &winBox);
        }

        SDL_RenderPresent(renderer);
    }

    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}
