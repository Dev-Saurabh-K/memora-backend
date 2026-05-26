import requests

def get_image_url(topic: str) -> str:
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={topic}&gsrnamespace=6&prop=imageinfo&iiprop=url&format=json"
    
    headers = {
        "User-Agent": "MyHackathonApp/1.0 (saurabhkumar.sakr@gmail.com)"
    }
    
    try:
        response = requests.get(url=url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            #Safely navigate Wikimedia's nested dynamic keys
            pages = data.get("query", {}).get("pages", {})
            if not pages:
                print(f"No images found for topic: {topic}")
                return ""
            
            # Get the first page object from the dynamic dictionary keys
            first_page_id = list(pages.keys())[0]
            image_info = pages[first_page_id].get("imageinfo", [])
            
            if image_info:
                image_url = image_info[0].get("url")
                return image_url
                
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        
    return ""

# Test the function
# print(get_image_url("daffodils"))


