import requests

class Hass:
    def __init__(self, base_url, token):
        base_url = base_url.rstrip('/api/')
        self.base_url = f'{base_url}/api'
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def getState(self, entity_id):
        url = f"{self.base_url}/states/{entity_id}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                raise Exception(response.text())
            response = response.json()
        except:
            if response.status_code == 401:
                raise Exception(f'\033[91mUnauthorized: Invalid token\033[0m')
            raise Exception(f'\033[91mFailed to get state for "{entity_id}" ({url})\033[0m')
        
        if entity_id.split('.')[0] == 'light':
            try:
                brightness = int(response['attributes']['brightness'])
                brightness_pct = round(brightness / 255 * 100)
            except:
                brightness_pct = 0
            response['attributes']['brightness_pct'] = brightness_pct
        
        return response
    

    def call_service(self, entity_id, service, service_data={}):
        domain = entity_id.split('.')[0]
        url = f"{self.base_url}/services/{domain}/{service}"
        service_data['entity_id'] = entity_id
        try:
            response = requests.post(url, headers=self.headers, json=service_data)
            if response.status_code != 200:
                raise Exception(response.text)
        except:
            if response.status_code == 401:
                raise Exception(f'\033[91mUnauthorized: Invalid token\033[0m')
            raise Exception(f'\033[91mFailed to call service "{service}" for "{entity_id}" ({url})\033[0m')
        return response.json()
    

    def activate_script(self, script_name):
        return self.call_service(f"script.{script_name}", "turn_on")
    
    def trigger_automation(self, automation_name, skip_condition=False):
        return self.call_service(f"automation.{automation_name}", "trigger", {"skip_condition": skip_condition})
    
    def activate_scene(self, scene_name):
        response = self.call_service(f"scene.{scene_name}", "turn_on")
        if response == []:
            raise Exception(f'\033[91mScene "{scene_name}" not found\033[0m')
        return response

    def fire_event(self, event_name, event_data):
        url = f"{self.base_url}/events/{event_name}"
        response = requests.post(url, headers=self.headers, json=event_data)
        return response.text