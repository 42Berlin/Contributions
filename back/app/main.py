import json
import os

from app.lib.intra import ic
from fastapi import FastAPI, Request, Response
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

def pretty_json(json_data):
    try:
        return json.dumps(json_data, sort_keys=True, indent=4)
    except:
        try:
            data = json.load(json_data)
            return json.dumps(data, sort_keys=True, indent=4)
        except:
            return json_data

def get_intra_projects():
    with open('/code/app/projects.json', 'r') as f:
        projects = json.load(f)
        f.close()
    
    return projects

SPECIAL_PROJECTS = [
    1331,   # minishell
    1326,   # cub3d
    1315,   # miniRT
    1336,   # ft_irc
    1332,   # webserv
    1337,   # ft_transcendence
]

@app.get("/")
def get_root():
    return {'hello': 'World'}

@app.get('/projects')
def get_projects(req: Request):
    data = []
    projects = []
    res = []

    token = req.headers.get("Authorization")

    if not token or token != ("Bearer " + os.getenv("SECRET_TOKEN")):
        return Response("Not authorized.", 403)

    with open('/code/app/projects_users.json', 'r') as f:
        data = json.load(f)
        f.close()

    projects = get_intra_projects()

    for x in data:
        if x["user"]["staff?"]:
            continue
        for project in projects:
            if x["project"]["id"] == project["id"]:
                team = None
                name = ''
                for team_of_project_user in x["teams"]:
                    if team_of_project_user["id"] == x["current_team_id"]:
                        team = team_of_project_user
                        break

                if not team:
                    print('no team found')
                    continue

                if len(team["users"]) > 1:
                    name = team["name"]
                else:
                    name = x["user"]["login"]

                is_already_in_it = False
                for proj in res:
                    if proj["id"] == x['current_team_id']:
                        is_already_in_it = True
                        break

                if not is_already_in_it:
                    res.append({
                        'id': x['current_team_id'],
                        'mark': x["final_mark"],
                        'xp': project["difficulty"],
                        'team_name': name,
                        'validated_at': x["marked_at"],
                        'special': x["project"]["id"] in SPECIAL_PROJECTS,
                        'project_name': project["name"],
                    })

    return res

@app.get('/days')
def get_days(req: Request):
    res = {}
    now = datetime.today()

    projects_user = get_projects(req)    

    for i in range(50):
        day_of_validation = now - timedelta(days=i)
        day_of_validation = day_of_validation.replace(hour=0, minute=0, second=0, microsecond=0)

        res[day_of_validation] = {
            'date': day_of_validation,
            'project_passed': 0,
            'special_passed': False,
        }
    
    for p in projects_user:
        
        day_of_validation = datetime.strptime(p["validated_at"], '%Y-%m-%dT%H:%M:%S.%fZ')
        day_of_validation = day_of_validation.replace(hour=0, minute=0, second=0, microsecond=0)
        
        if day_of_validation not in res:
            res[day_of_validation] = {
                'date': day_of_validation,
                'project_passed': 0,
                'special_passed': False,
            }

        res[day_of_validation]['project_passed'] += 1
        if not res[day_of_validation]['special_passed'] and \
            p['special']:
            res[day_of_validation]['special_passed'] = True
    
    real_res = list(res.values())
    real_res.sort(key= lambda x: x["date"])
    return real_res

@app.get("/reload")
def reload_json_file(req: Request):
    json_data = []
    response = ''
    projects = []
    today = datetime.now()

    token = req.headers.get("Authorization")

    if not token or token != ("Bearer " + os.getenv("SECRET_TOKEN")):
        return Response("Not authorized.", 403)

    last_modified_projects_users = datetime.fromtimestamp(
            os.path.getmtime('/code/app/projects_users.json')
        )
    last_modified_projects = datetime.fromtimestamp(
            os.path.getmtime('/code/app/projects.json')
        )

    if today - last_modified_projects_users < timedelta(seconds=50):
        response += 'Project users have already been realoaded lately (base delay 1 minute). '
    else:
        projects_users = ic.pages_threaded(f'/projects_users/?filter[campus]=51'
                        f'&filter[cursus]=21' 
                        f'&range[marked_at]={today - timedelta(days=50)},{today}')

        for x in projects_users:
            if x['validated?']:
                json_data.append(x)

        with open('/code/app/projects_users.json', 'w') as f:
            json.dump(json_data, f)
            f.close()
        
        response += "Project users reloaded. "
    
    if today - last_modified_projects < timedelta(days=15):
        response += 'Project have already been realoaded lately (base delay 15 days).'
    else:
        projects = ic.pages_threaded(f'/cursus/21/projects')
        with open('/code/app/projects.json', 'w') as f:
            json.dump(projects, f)
            f.close()
        response += 'Projects have been reloaded.'

    return response
