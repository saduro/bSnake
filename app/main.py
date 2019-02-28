import json
import os
import random
import bottle

from api import ping_response, start_response, move_response, end_response

@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
    '''

@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.
    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()

@bottle.post('/start')
def start():
    data = bottle.request.json

    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    print(json.dumps(data))

    color = "#FF0000"

    return start_response(color)


@bottle.post('/move')
def move():
    data = bottle.request.json

    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    print(json.dumps(data))
    myId = data['you']['id']
    turn = data['turn']
    body = data['you']['body']
    snakes = data['board']['snakes']
    foods = data['board']['food']
    moveOption = []
    riskyMove = []
    x = body[0]['x']
    y = body[0]['y']
    xLimit = data['board']['width'] - 1
    yLimit = data['board']['height'] - 1
    LonguestSnake = 1
    food = 1
    left = 1
    right = 1
    up = 1
    down = 1
    
    for snake in snakes:
        if snakes['id'] != myId:
            if len(snake['body']) >= len(body):
                LonguestSnake = 0
                head = snake['body'][0]
                if head['x'] == x:
                    if head['y']+2 == y:
                        up = 0
                        riskyMove += ['up']
                    elif head['y']-2 == y:
                        down = 0
                        riskyMove += ['down']
                if head['y'] == y:
                    if head['x']+2 == x:
                        left = 0
                        riskyMove += ['left']
                    if head['x']-2 == x:
                        right = 0
                        riskyMove += ['right']
                if head['x']+1 == x:
                    if head['y']+1 == y:
                        up = 0
                        riskyMove += ['up']
                        left = 0
                        riskyMove += ['left']
                    if head['y']-1 == y:
                        down = 0
                        riskyMove += ['down']
                        left = 0
                        riskyMove += ['left']
                if head['x']-1 == x:
                    if head['y']+1 == y:
                        up = 0
                        riskyMove += ['up']
                        right = 0
                        riskyMove += ['right']
                    if head['y']-1 == y:
                        down = 0
                        riskyMove += ['down']
                        right = 0
                        riskyMove += ['right']
            i=1
            for b in snake['body']:
                if i != len(snake['body']):
                    if x == b['x']:
                        if b['y'] == y-1:
                            up = 0
                            if 'up' in riskyMove:
                                riskyMove.remove('up')
                        elif b['y'] == y+1:
                            down = 0
                            if 'down' in riskyMove:
                                riskyMove.remove('down')
                    elif y == b['y']:
                        if  b['x'] == x-1:
                            left = 0
                            if 'left' in riskyMove:
                                riskyMove.remove('left')
                        elif  b['x'] == x+1:
                            right = 0
                            if 'right' in riskyMove:
                                riskyMove.remove('right')
                i+=1
    
    i=1
    for b in body:
        if i != len(body):
            if x == b['x']:
                if b['y'] == y-1:
                    up = 0
                    if 'up' in riskyMove:
                        riskyMove.remove('up')
                elif b['y'] == y+1:
                    down = 0
                    if 'down' in riskyMove:
                        riskyMove.remove('down')
            elif y == b['y']:
                if  b['x'] == x-1:
                    left = 0
                    if 'left' in riskyMove:
                        riskyMove.remove('left')
                elif  b['x'] == x+1:
                    right = 0
                    if 'right' in riskyMove:
                        riskyMove.remove('right')
        i+=1
    
    minDistance = 1000000000
    if len(foods) != 0:
        for f in foods:
            xDistance = f['x']-x
            yDistance = f['y']-y
            distance = abs(xDistance)+abs(yDistance)
            if distance <= minDistance:
                minDistance = distance
                xFoodDistance = xDistance
                yFoodDistance = yDistance
    else:
        food = 0
    
    if x and left:
        moveOption += ['left']
    if x != xLimit and right:
        moveOption += ['right']
    if y and up:
        moveOption += ['up']
    if y != yLimit and down:
        moveOption += ['down']
    
    if food and not LonguestSnake:
        if xFoodDistance == 0:
            if yFoodDistance < 0:
                if 'up' in moveOption:
                    direction = 'up'
                else:
                    if len(moveOption):
                        direction = random.choice(moveOption)
                    else:
                       direction = random.choice(riskyMove) 
            else:
                if 'down' in moveOption:
                    direction = 'down'
                else:
                    if len(moveOption):
                        direction = random.choice(moveOption)
                    else:
                       direction = random.choice(riskyMove) 
        elif yFoodDistance == 0:
            if xFoodDistance < 0:
                if 'left' in moveOption:
                    direction = 'left'
                else:
                    if len(moveOption):
                        direction = random.choice(moveOption)
                    else:
                       direction = random.choice(riskyMove) 
            else:
                if 'right' in moveOption:
                    direction = 'right'
                else:
                    if len(moveOption):
                        direction = random.choice(moveOption)
                    else:
                        direction = random.choice(riskyMove) 
        elif abs(xFoodDistance) < abs(yFoodDistance):
            if xFoodDistance < 0:
                if 'left' in moveOption:
                    direction = 'left'
                else:
                    if yFoodDistance < 0:
                        if 'up' in moveOption:
                            direction = 'up'
                        else:
                            if len(moveOption):
                                direction = random.choice(moveOption)
                            else:
                                direction = random.choice(riskyMove) 
                    else:
                        if 'down' in moveOption:
                            direction = 'down'
                        else:
                            if len(moveOption):
                                direction = random.choice(moveOption)
                            else:
                                direction = random.choice(riskyMove) 
            else:
                if 'right' in moveOption:
                    direction = 'right'
                else:
                    if yFoodDistance < 0:
                        if 'up' in moveOption:
                            direction = 'up'
                        else:
                            if len(moveOption):
                                direction = random.choice(moveOption)
                            else:
                                direction = random.choice(riskyMove) 
                    else:
                        if 'down' in moveOption:
                            direction = 'down'
                        else:
                            if len(moveOption):
                                direction = random.choice(moveOption)
                            else:
                                direction = random.choice(riskyMove) 
        elif abs(yFoodDistance) < abs(xFoodDistance):
            if yFoodDistance < 0:
                if 'up' in moveOption:
                    direction = 'up'
                else:
                    if xFoodDistance < 0:
                        if 'left' in moveOption:
                            direction = 'left'
                        else:
                            if len(moveOption):
                                direction = random.choice(moveOption)
                            else:
                                direction = random.choice(riskyMove) 
                    else:
                        if 'right' in moveOption:
                            direction = 'right'
                        else:
                            if len(moveOption):
                                direction = random.choice(moveOption)
                            else:
                                direction = random.choice(riskyMove)
            else:
                if 'down' in moveOption:
                    direction = 'down'
                else:
                    if xFoodDistance < 0:
                        if 'left' in moveOption:
                            direction = 'left'
                        else:
                            if len(moveOption):
                                direction = random.choice(moveOption)
                            else:
                                direction = random.choice(riskyMove)
                    else:
                        if 'right' in moveOption:
                            direction = 'right'
                        else:
                            if len(moveOption):
                                direction = random.choice(moveOption)
                            else:
                                direction = random.choice(riskyMove)
        else:
            if len(moveOption):
                direction = random.choice(moveOption)
            else:
                direction = random.choice(riskyMove)
    else:
        if len(moveOption):
            direction = random.choice(moveOption)
        else:
            direction = random.choice(riskyMove)
    

    return move_response(direction)


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print(json.dumps(data))

    return end_response()

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
