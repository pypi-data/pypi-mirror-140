from requests import Session
from os import startfile
import time
from random import randint

server = Session()

class roPy():
    
    def xsrf(cookie):
        try:
            resp = server.post('https://auth.roblox.com/v2/logout', 
            cookies={
                '.ROBLOSECURITY': cookie
            })
            return resp.headers['X-CSRF-TOKEN']
        except KeyError:
            return 'Invalid Cookie'

    def follow(cookie, userId):
        token = roPy.xsrf(cookie)
        if not token == 'Invalid Cookie':
            resp = server.post(f'https://friends.roblox.com/v1/users/{userId}/follow', 
            cookies={
                '.ROBLOSECURITY': cookie
            },
            headers={
                'X-CSRF-TOKEN': token
            })
            return(resp.json())
        else:
            return 'Invalid Cookie'

    def favorite_asset(cookie, shirtId):
        token = roPy.xsrf(cookie)
        if not token == 'Invalid Cookie':
            resp = server.post('https://www.roblox.com/v2/favorite/toggle', 
            cookies={
                '.ROBLOSECURITY': cookie
            },
            headers={
                'X-CSRF-TOKEN': token
            },
            data=
            {
                "itemTargetId": shirtId,
                "favoriteType": 'Asset'
            })
            return(resp.json())
            
    def comment_asset(cookie, assetId, text, captcha, captchaId):
        token = roPy.xsrf(cookie)
        if not token == 'Invalid Cookie':
            resp = server.post('https://www.roblox.com/comments/post', 
            cookies={
                '.ROBLOSECURITY': cookie
            },
            headers={
                'X-CSRF-TOKEN': token
            },
            data=
            {
                "assetId": assetId,
                "text": text,
                'captchaToken': captcha,
                'captchaId': captchaId
            })
            return(resp.json())

    def get_robux(cookie, userId):
        resp = server.get(f'https://economy.roblox.com/v1/users/{userId}/currency',
        cookies={
            '.ROBLOSECURITY': cookie
        })
        return resp.json()

    def get_summary(cookie, time, userId):
        resp = server.get(f'https://economy.roblox.com/v2/users/{userId}/transaction-totals?timeFrame={time}&transactionType=summary',
        cookies={
            '.ROBLOSECURITY': cookie
        })
        return resp.json()
    
    def get_userId(cookie):
        resp = server.get('https://users.roblox.com/v1/users/authenticated',
		cookies={
			'.ROBLOSECURITY': cookie
		})
        try:
            return resp.json()['id']
        except KeyError:
            return 'Invalid Cookie'

    def get_conversations(cookie):
        conversations = []
        response = [1]
        page = 0
        while len(response) > 0:
            page+=1
            resp = server.get(f'https://chat.roblox.com/v2/get-user-conversations?pageNumber={page}&pageSize=100',
            cookies={
                '.ROBLOSECURITY': cookie
            })
            response = resp.json()
            for x in response:
                conversations.append(x)
        return conversations

    def get_groups(cookie, userId):
        groups = []
        resp = server.get(f'https://groups.roblox.com/v1/users/{userId}/groups/roles',
        cookies={
            '.ROBLOSECURITY': cookie
        })
        for item in resp.json()['data']:
            groups.append(item)
        return groups

    def authentication_ticket(cookie):
        resp = server.post('https://auth.roblox.com/v1/authentication-ticket/',
        cookies={
            '.ROBLOSECURITY': cookie
        },
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'X-CSRF-TOKEN': roPy.xsrf(cookie),
            'origin': 'https://www.roblox.com',
            'referer': 'https://www.roblox.com/'
        })
        return resp.headers['rbx-authentication-ticket']

    def join_game(cookie, placeId):
        auth = roPy.authentication_ticket(cookie)
        browserTrackerId = int("55393295400")+randint(1,100)
        launchTime = int(time.time()*1000)
        url = f"roblox-player:1+launchmode:play+gameinfo:{auth}+launchtime:{launchTime}+placelauncherurl:https://assetgame.roblox.com/game/PlaceLauncher.ashx?request=RequestGame&browserTrackerId={browserTrackerId}&placeId={placeId}&isPlayTogetherGame=false+browsertrackerid:{browserTrackerId}+robloxLocale:en_us+gameLocale:en_us"
        startfile(url)

    def like_game(cookie, gameId):
        token = roPy.xsrf(cookie)
        if not token == 'Invalid Cookie':
            resp = server.post(f'https://www.roblox.com/voting/vote?assetId={gameId}&vote=true',
            cookies={
                '.ROBLOSECURITY': cookie
            },
            headers={
                'X-CSRF-TOKEN': token
            })

        else:
            return 'Invalid Cookie'

