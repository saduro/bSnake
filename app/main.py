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
    def createMap(board):
       map = [[0]*board['height'] for i in range(board['width'])]
       return map

    def drawFood(foods,map):
            for food in foods:
                    map[food['x']][food['y']] = 1
            return map

    def drawHead(mySnake,snake,map,board):
            if snake['id'] != mySnake['id']:
                    headX = snake['body'][0]['x']
                    headY = snake['body'][0]['y']
                    if len(snake['body'])< len(mySnake['body']):
                            map[headX][headY] = 4
                            if headX != board['width'] -1:
                                    if map[headX+1][headY] < 2:
                                            map[headX+1][headY] = 2
                            if headX != 0:
                                    if map[headX-1][headY] < 2:
                                            map[headX-1][headY] = 2
                            if headY != board['height']-1:
                                    if map[headX][headY+1] < 2:
                                            map[headX][headY+1] = 2
                            if headY != 0:
                                    if map[headX][headY-1] < 2:
                                            map[headX][headY-1] = 2
                    else:
                            map[headX][headY] = 4
                            if headX != board['width']-1:
                                    if map[headX+1][headY] < 3:
                                            map[headX+1][headY] = 3
                            if headX != 0:
                                    if map[headX-1][headY] < 3:
                                            map[headX-1][headY] = 3
                            if headY != board['height']-1:
                                    if map[headX][headY+1] < 3:
                                            map[headX][headY+1] = 3
                            if headY != 0:
                                    if map[headX][headY-1] < 3:
                                            map[headX][headY-1] = 3
            return map

    def drawSnakes(mySnake,board,map):
            for snake in board['snakes']:
                    for bodyBits in snake['body']:
                            map[bodyBits['x']][bodyBits['y']] = 5
                    map = drawHead(mySnake,snake,map,board)
            return map

    def getMap(board,mySnake):
            map = createMap(board)
            map = drawFood(board['food'],map)
            map = drawSnakes(mySnake,board,map)
            return map

    def evalMinDirection(directions,xMinDistance,yMinDistance):
            if xMinDistance == 0:
                    if yMinDistance < 0:
                            directions['up'] += 20
                    else:
                            directions['down'] += 20
            elif yMinDistance == 0:
                    if xMinDistance < 0:
                            directions['left'] += 20
                    else:
                            directions['right'] += 20
            elif abs(yMinDistance) < abs(xMinDistance):
                    if xMinDistance < 0:
                            directions['left'] += 20
                    else:
                            directions['right'] += 20
                    if yMinDistance < 0:
                            directions['up'] += 10
                    else:
                            directions['down'] += 10
            else:
                    if xMinDistance < 0:
                            directions['left'] += 10
                    else:
                            directions['right'] += 10
                    if yMinDistance < 0:
                            directions['up'] += 20
                    else:
                            directions['down'] += 20
            return directions

    def evalFood(foods,directions,head):
            minDistance = 1000000000
            for food in foods:
                    xDistance = food['x']-head['x']
                    yDistance = food['y']-head['y']
                    distance = abs(xDistance)+abs(yDistance)
                    if distance <= minDistance:
                            minDistance = distance
                            xMinDistance = xDistance
                            yMinDistance = yDistance
            directions = evalMinDirection(directions,xMinDistance,yMinDistance)
            return directions

    def evalImediateKill(directions,head,map,board):
            if head['x'] != board['width']-1:
                    if map[head['x']+1][head['y']] == 2:
                            directions['right'] += 30
            if head['x'] != 0:
                    if map[head['x']-1][head['y']] == 2:
                            directions['left'] += 30
            if head['y'] != board['height']-1:
                    if map[head['x']][head['y']+1] == 2:
                            directions['down'] += 30
            if head['y'] != 0:
                    if map[head['x']][head['y']-1] == 2:
                            directions['up'] += 30
            return directions

    def evalLongKill(directions,snakes,mySnake):
            minDistance = 1000000000
            for snake in snakes:
                    if snake['id'] != mySnake['id']:
                            xDistance = snake['body'][0]['x']-mySnake['body'][0]['x']
                            yDistance = snake['body'][0]['y']-mySnake['body'][0]['y']
                            distance = abs(xDistance)+abs(yDistance)
                            if distance <= minDistance:
                                    minDistance = distance
                                    xMinDistance = xDistance
                                    yMinDistance = yDistance
            directions = evalMinDirection(directions,xMinDistance,yMinDistance)
            return directions

    def evalDanger(directions,head,map,board):
            if head['x'] != board['width']-1:
                    if map[head['x']+1][head['y']] > 3:
                            directions['right'] -= 160
                    elif map[head['x']+1][head['y']] > 2:
                            directions['right'] -= 60
            else:
                    directions['right'] -= 160
            if head['x'] != 0:
                    if map[head['x']-1][head['y']] > 3:
                            directions['left'] -= 160
                    elif map[head['x']-1][head['y']] > 2:
                            directions['left'] -= 60
            else:
                    directions['left'] -= 160
            if head['y'] != board['height']-1:
                    if map[head['x']][head['y']+1] > 3:
                            directions['down'] -= 160
                    elif map[head['x']][head['y']+1] > 2:
                            directions['down'] -= 60
            else:
                    directions['down'] -= 160
            if head['y'] != 0:
                    if map[head['x']][head['y']-1] > 3:
                            directions['up'] -= 160
                    elif map[head['x']][head['y']-1] > 2:
                            directions['up'] -= 60
            else:
                    directions['up'] -= 160
            return directions

    def compareSize(mySnake,snakes):
            info = 1
            for snake in snakes:
                if TRUE:
                    if len(mySnake['body'])<= len(snake['body']):
                            info = 0
            return info

    def getArea(x,y,board,map,area):
            if x >= 0 and y >= 0 and x <= board['width']-1 and y <= board['height']-1:
                    if map[x][y]!= 8:
                            if map[x][y] < 4:
                                    map[x][y] = 8
                                    area += 1 + getArea(x+1,y,board,map,area) + getArea(x-1,y,board,map,area) + getArea(x,y+1,board,map,area) + getArea(x,y-1,board,map,area)
                            else:
                                    return 0
                    else:
                           return 0 
            else:
                    return 0
            return area

    def evalSpace(mySnake,board,directions):
            area = 0
            map = getMap(board,mySnake)
            left = getArea(mySnake['body'][0]['x']-1,mySnake['body'][0]['y'],board,map,area)
            map = getMap(board,mySnake)
            right = getArea(mySnake['body'][0]['x']+1,mySnake['body'][0]['y'],board,map,area)
            map = getMap(board,mySnake)
            down = getArea(mySnake['body'][0]['x'],mySnake['body'][0]['y']+1,board,map,area)
            map = getMap(board,mySnake)
            up = getArea(mySnake['body'][0]['x'],mySnake['body'][0]['y']-1,board,map,area)
            if left < len(mySnake['body']):
                    directions['left'] -= 60
            if right < len(mySnake['body']):
                    directions['right'] -= 60
            if down < len(mySnake['body']):
                    directions['down'] -= 60
            if up < len(mySnake['body']):
                    directions['up'] -= 60
            return directions


    def getNextMove(directions,mySnake,map,board):
            bigEnough = compareSize(mySnake,board['snakes'])
            if len(board['food']) != 0 and (mySnake['health'] < 40 or not bigEnough):
                    directions = evalFood(board['food'],directions,mySnake['body'][0])
            directions = evalImediateKill(directions,mySnake['body'][0],map,board)
            if len(board['snakes']) < 3 and bigEnough:
                    directions = evalLongKill(directions,board['snakes'],mySnake)
            directions = evalDanger(directions,mySnake['body'][0],map,board)
            directions = evalSpace(mySnake,board,directions)
            return (directions)

    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    print(json.dumps(data))
    directions = {'left':0,'up':0,'right':0,'down':0}

    map = getMap(data['board'],data['you'])
    directions = getNextMove(directions,data['you'],map,data['board'])
    direction = max(directions, key=directions.get)

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
