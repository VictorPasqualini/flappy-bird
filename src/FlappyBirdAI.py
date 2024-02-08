import pygame
import os
import random
import neat

ai_playing = True
generation = 0

WIDTH_SCREEN = 500
HEIGHT_SCREEN = 800

PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('../resources/imgs', 'pipe.png')))
GROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('../resources/imgs', 'base.png')))
BACKGROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('../resources/imgs', 'bg.png')))
BIRD_IMAGE = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('../resources/imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('../resources/imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('../resources/imgs', 'bird3.png')))
]

pygame.font.init()
FONT = pygame.font.SysFont('arial', 50)

class Bird:
    IMAGES = BIRD_IMAGE
    
    # animacoes da rotacao
    max_rotation = 25
    speed_rotation = 20
    animation_time = 5

    def __init__(self, x, y):

        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.height = self.y
        self.time = 0
        self.image_count = 0
        self.image = self.IMAGES[0]

    def jump(self):

        self.speed = -10.5
        self.time = 0
        self.height = self.y

    def move(self):
        
        # calcula deslocamento
        self.time += 1
        throw = 1.5 * (self.time**2) + self.speed * self.time

        # restringe deslocamento
        if throw > 16:
            throw = 16
        elif throw < 0:
            throw -= 2

        self.y += throw

        # angulo do passaro
        if throw < 0 or self.y < (self.height + 50):
            if self.angle < self.max_rotation:
                self.angle = self.max_rotation
        else:
            if self.angle > -90:
                self.angle -= self.speed_rotation

    def draw(self, screen):

        self.image_count += 1

        if self.image_count < self.animation_time:
            self.image = self.IMAGES[0]
        elif self.image_count < self.animation_time * 2:
            self.image = self.IMAGES[1]
        elif self.image_count < self.animation_time * 3:
            self.image = self.IMAGES[2]
        elif self.image_count < self.animation_time * 4:
            self.image = self.IMAGES[1]
        elif self.image_count >= self.animation_time * 4 + 1:
            self.image = self.IMAGES[0]
            self.image_count = 0

        if self.angle <= -80:
            self.imagem = self.IMAGES[1]
            self.image_count = self.animation_time * 2

        rotationed_image = pygame.transform.rotate(self.image, self.angle)
        pos_center_image = self.image.get_rect(topleft = (self.x, self.y)).center
        rectangle = rotationed_image.get_rect(center = pos_center_image)
        screen.blit(rotationed_image, rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)
        
class Pipe:

    DISTANCE = 200
    SPEED = 5

    def __init__(self, x):

        self.x = x
        self.height = 0
        self.top_position = 0
        self.bot_position = 0
        self.TOP_PIPE = pygame.transform.flip(PIPE_IMAGE, False, True)
        self.BOT_PIPE = PIPE_IMAGE
        self.passed = False
        self.define_height()

    def define_height(self):

        self.height = random.randrange(50, 450)
        self.top_position = self.height - self.TOP_PIPE.get_height()
        self.bot_position = self.height + self.DISTANCE

    def move(self):

        self.x -= self.SPEED

    def draw(self, screen):

        screen.blit(self.TOP_PIPE, (self.x, self.top_position))
        screen.blit(self.BOT_PIPE, (self.x, self.bot_position))

    def collide(self, bird):

        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.TOP_PIPE)
        bot_mask = pygame.mask.from_surface(self.BOT_PIPE)

        distance_top = (self.x - bird.x, self.top_position - round(bird.y))
        distance_bot = (self.x - bird.x, self.bot_position - round(bird.y))

        point_top = bird_mask.overlap(top_mask, distance_top)
        point_bot = bird_mask.overlap(bot_mask, distance_bot)

        if point_bot or point_top:
            return True
        else:
            return False

class Ground:

    SPEED = 5
    WIDTH = GROUND_IMAGE.get_width()
    IMAGE = GROUND_IMAGE


    def __init__(self, y):

        self.y = y
        self.x0 = 0
        self.x1 = self.WIDTH

    def move(self):

        self.x0 -= self.SPEED
        self.x1 -= self.SPEED

        if self.x0 + self.WIDTH < 0:
            self.x0 = self.x1 + self.WIDTH
        
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x0 + self.WIDTH

    def draw(self, screen):

        screen.blit(self.IMAGE, (self.x0, self.y))
        screen.blit(self.IMAGE, (self.x1, self.y))

def draw_screen(screen, birds, pipes, ground, score):

    screen.blit(BACKGROUND_IMAGE, (0, 0))
    
    for bird in birds:
        bird.draw(screen)

    for pipe in pipes:
        pipe.draw(screen)

    text_score = FONT.render(f"Pontuação: {score}", 1, (255, 255, 255))
    screen.blit(text_score, (WIDTH_SCREEN - 10 - text_score.get_width(), 10))

    if ai_playing:
        text_generation = FONT.render(f"Geração: {generation}", 1, (255, 255, 255))
        screen.blit(text_generation, (10, 10))
                
    ground.draw(screen)

    pygame.display.update()

def main(genomes, config): # fitness function

    global generation
    generation += 1

    if ai_playing:
        networks = []
        genomes_list = []
        birds = []

        for _, genome in genomes:
            network = neat.nn.FeedForwardNetwork.create(genome, config)

            networks.append(network)
            genome.fitness = 0
            genomes_list.append(genome)
            birds.append(Bird(230, 350))

    else:
        birds = [Bird(230, 350)]

    ground = Ground(730)
    pipes = [Pipe(700)]
    screen = pygame.display.set_mode((WIDTH_SCREEN, HEIGHT_SCREEN))
    score = 0
    time = pygame.time.Clock()

    running = True

    while running:

        time.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()

            if not ai_playing:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        for bird in birds:
                            bird.jump()

        pipe_index = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > (pipes[0].x + pipes[0].TOP_PIPE.get_width()):
                pipe_index = 1
        else:
            running = False
            break
                
        for i, bird in enumerate(birds):
            bird.move()
            genomes_list[i].fitness += 0.1
            output = networks[i].activate((bird.y, 
                                          abs(bird.y - pipes[pipe_index].height),
                                          abs(bird.y - pipes[pipe_index].bot_position)))
            
            if output[0] > 0.5:
                bird.jump()

        ground.move()

        add_pipe = False
        delete_pipe = []
        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.collide(bird):
                    birds.pop(i)

                    if ai_playing:
                        genomes_list[i].fitness -= 1
                        genomes_list.pop(i)
                        networks.pop(i)
                    
                if not pipe.passed and bird.x > pipe.x:
                    pipe.passed = True
                    add_pipe = True
            
            pipe.move()

            if pipe.x + pipe.TOP_PIPE.get_width() < 0:
                delete_pipe.append(pipe)

        if add_pipe:
            score += 1
            pipes.append(Pipe(600))
            
            for genome in genomes_list:
                genome.fitness += 5

        for pipe in delete_pipe:
            pipes.remove(pipe)

        for i, bird in enumerate(birds):
            if (bird.y + bird.image.get_height()) > ground.y or bird.y < 0:
                birds.pop(i)

                if ai_playing:
                    genomes_list.pop(i)
                    networks.pop(i)

        draw_screen(screen, birds, pipes, ground, score)

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)
    
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())

    if ai_playing:
        population.run(main, 50)
    else:
        main(None, None)

if __name__ == '__main__':
    path = os.path.dirname(__file__)
    config_path = os.path.join(path, 'config.txt')
    run(config_path)
